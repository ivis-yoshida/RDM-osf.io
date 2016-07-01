import re
import sys
import json
import uuid
import sqlite3
from datetime import datetime
from hashlib import sha256, md5

from geoip import geolite2

from modularodm import Q

from website.app import init_app
from website.models import User, Node, NodeLog
from website.util.metrics import get_entry_point

from scripts.migrate_piwik import utils
from scripts.migrate_piwik import settings
from scripts.migrate_piwik import lookup_data


def main():

    history_run_id = utils.get_history_run_id_for('extract')
    complaints_run_id = utils.get_complaints_run_id_for('extract')
    if history_run_id != complaints_run_id:
        print("You need to validate your exported data! Bailing...")
        sys.exit()

    extract_complaints = utils.get_complaints_for('extract', 'r')
    extract_complaints.readline()  # toss header
    if extract_complaints.readline():
        print("You have unaddressed complaints! Bailing...")
        sys.exit()

    sqlite_db = sqlite3.connect(settings.SQLITE_PATH)
    sqlite_setup(sqlite_db)

    input_file = open(utils.get_dir_for('extract') + '/' + settings.EXTRACT_FILE, 'r')
    transform_dir = utils.get_dir_for('transform01')
    output_file = open(transform_dir + '/' + settings.TRANSFORM01_FILE, 'w')

    history_file = utils.get_history_for('transform01', 'w')
    history_file.write('Run ID: {}\n'.format(complaints_run_id))
    history_file.write('Beginning extraction at: {}Z\n'.format(datetime.utcnow()))

    user_cache = {}
    node_cache = {}
    location_cache = {}

    linenum = 0
    tally = {'missing_user': 0, 'missing_node': 0}
    for pageview_json in input_file.readlines():
        linenum += 1
        if not linenum % 1000:
            print('Transforming line {}'.format(linenum))

        raw_pageview = json.loads(pageview_json)
        visit = raw_pageview['visit']
        action = raw_pageview['action']

        location = None
        ip_addr = visit['ip_addr']
        if ip_addr is not None:
            if not location_cache.has_key(ip_addr):
                location_cache[ip_addr] = geolite2.lookup(ip_addr)

            location = location_cache[ip_addr]

        # artificial session id. actual value not important
        session_id = str(uuid.uuid4())
        keen_id = get_or_create_keen_id(visit['visitor_id'], sqlite_db)

        user_id = visit['user_id']
        if user_id is not None:
            if not user_cache.has_key(user_id):
                user_obj = User.load(user_id)
                user_cache[user_id] = {
                    'anon': md5(session_id).hexdigest(),
                    'entry_point': None if user_obj is None else get_entry_point(user_obj),
                    'locale': user_obj.locale if user_obj else '',
                    'timezone': user_obj.timezone if user_obj else '',
                    'institutions': [
                        {'id': inst._id, 'name': inst.name, 'logo_path': inst.logo_path}
                        for inst in user.affiliated_institutions
                    ] if user_obj else [],
                }

            anon_id = user_cache[user_id]['anon']
            user_entry_point = user_cache[user_id]['entry_point']
            user_locale = user_cache[user_id]['locale']
            user_timezone = user_cache[user_id]['timezone']
            user_institutions = user_cache[user_id]['institutions']


        node = None
        node_id = action['node_id']
        if node_id is not None:
            if not node_cache.has_key(node_id):
                node_cache[node_id] = Node.load(node_id)
            node = node_cache[node_id]


        node_public_date = None
        if node is not None:
            print "Triggered at least once"
            privacy_actions = NodeLog.find(
                Q('node', 'eq', 'vjsdy')
                & Q('action', 'in', [NodeLog.MADE_PUBLIC, NodeLog.MADE_PRIVATE])
            ).sort('date')
            if privacy_actions[-1].action == NodeLog.MADE_PUBLIC:
                node_public_date = privacy_actions[-1].date.isoformat()
                node_public_date = node_public_date[:-3] + 'Z'

        browser_version = [None, None]
        if visit['ua']['browser']['version']:
            browser_version = visit['ua']['browser']['version'].split('.')

        browser_info = {
            'device': {
                'family': visit['ua']['device'],
            },
            'os': {
                'major': None,
                'patch_minor': None,
                'minor': None,
                'family': parse_os_family(visit['ua']['os']),
                'patch': None,
            },
            'browser': {
                'major': browser_version[0],
                'minor': browser_version[1],
                'family': parse_browser_family(visit['ua']['browser']['name']),
                'patch': None,
            },
        }

        node_tags = None if action['node_tags'] is None else [
            tag for tag in action['node_tags'].split(',')
        ]

        # piwik stores resolution as 1900x600 mostly, but sometimes as a float?
        # For the sake of my sanity and yours, let's ignore floats.
        screen_resolution = (None, None)
        if re.search('x', visit['ua']['screen']):
            screen_resolution = visit['ua']['screen'].split('x')

        # piwik fmt: '2016-05-11 20:30:00', keen fmt: '2016-06-30T17:12:50.070Z'
        # piwik is always utc
        timestamp = datetime.strptime(action['timestamp'], '%Y-%m-%d %H:%M:%S')
        ts_formatted = timestamp.isoformat() + '.000Z'  # naive, but correct

        pageview = {
            'meta': {
                'epoch': 0,  # migrated from piwik
            },
            'page': {
                'title': action['page']['title'],
                'url': action['page']['url_prefix'] + action['page']['url'],
                'info': {}  # (add-on)
            },
            'referrer': {
                'url': action['referrer'] or None,
                'info': {}, # (add-on)
            },
            'tech': {
                'browser': {  # JS-side will be filled in by Keen.helpers.getBrowserProfile()
                    'cookies': True if visit['ua']['browser']['cookies'] else False,
                    'screen': {
                        'height': screen_resolution[1],
                        'width': screen_resolution[0],
                    },
                },
                'ip': ip_addr,  # private
                'ua': None,
                'info': browser_info,
            },
            'time': {
                'utc': timestamp_components(timestamp),
                'local': {}
            },
            'visitor': {
                'id': keen_id,
                'session': session_id,  # random val (sessionId)
                'returning': True if visit['visitor_returning'] else False,  # visit
            },
            'user': {
                'id': user_id,
                'entry_point': user_entry_point or '',  # empty string if no user
                'locale': user_locale or '',  # empty string if no user
                'timezone': user_timezone or '',  # empty string if no user
                'institutions': user_institutions,  # null if no user, else []
            },
            'node': {
                'id': node_id,
                'title': getattr(node, 'title', None),
                'type': getattr(node, 'category', None),
                'tags': node_tags,
                'made_public_date': node_public_date,
            },
            'geo': {},
            'anon': {
                'id': anon_id,
                'continent': getattr(location, 'continent', None),
                'country': getattr(location, 'country', None),
            },
            'keen': {
                'timestamp': ts_formatted,
                'addons': [
                    {
                        'name': 'keen:referrer_parser',
                        'input': {
                            'referrer_url': 'referrer.url',
                            'page_url': 'page.url'
                        },
                        'output': 'referrer.info'
                    },
                    {
                        'name': 'keen:url_parser',
                        'input': {
                            'url': 'page.url'
                        },
                        'output': 'page.info'
                    },
                    {
                        'name': 'keen:url_parser',
                        'input': {
                            'url': 'referrer.url'
                        },
                        'output': 'referrer.info'
                    },
                    {  # private
                        'name': 'keen:ip_to_geo',
                        'input': {
                            'ip': 'tech.ip'
                        },
                        'output': 'geo',
                    }
                ],
            }
        }

        if node_id is None:
            tally['missing_node'] += 1

        if user_id is None:
            tally['missing_user'] += 1

        output_file.write(json.dumps(pageview) + '\n')

    history_file.write('Finished extraction at: {}Z\n'.format(datetime.utcnow()))
    history_file.write('Final count was: {}\n'.format(linenum))
    history_file.write('{} pageviews lacked a user id.\n'.format(tally['missing_user']))
    history_file.write('{} pageviews lacked a node id.\n'.format(tally['missing_node']))
    sqlite_db.close()


def sqlite_setup(sqlite_db):
    """Test whether we already have an sqlite db for mapping Piwik user_ids to new keen ids,
    and if not create one. 
    :return:
    """
    cursor = sqlite_db.cursor()

    try:
        cursor.execute('SELECT COUNT(*) FROM matched_ids')
    except sqlite3.OperationalError:
        cursor.execute('CREATE TABLE matched_ids (piwik_id TEXT, keen_id TEXT)')
        sqlite_db.commit()


def get_or_create_keen_id(user_id, sqlite_db):
    """Gets or creates a new Keen Id given a Piwik User Id from the db

    :param user_id: Piwik User Id from current row in database
    :param sqlite_db: SQLite3 database handle
    :return: Keen Id as str
    """
    cursor = sqlite_db.cursor()
    query = "SELECT * FROM matched_ids WHERE piwik_id='{p_id}'".format(p_id=user_id)
    cursor.execute(query)

    keen_id = cursor.fetchall()

    if len(keen_id) > 1:
        raise Exception("Multiple ID's found for single Piwik User ID")

    if not keen_id:
        keen_id = uuid.uuid4()
        query = "INSERT INTO matched_ids (piwik_id, keen_id) VALUES ('{p_id}', '{n_id}');".format(
            p_id=str(user_id), n_id=str(keen_id)
        )
        cursor.execute(query)
        sqlite_db.commit()
        return str(keen_id)

    return str(keen_id[0][1])


def parse_os_family(os_key):
    """Attempts to parse Piwik OS key codes into corresponding OS names

    :param os_name: Operating System keycode
    :return: Operating System name
    """

    if os_key in lookup_data.legacy_os_keys:
        os_key = lookup_data.legacy_os_keys[os_key]

    return lookup_data.os_keys.get(os_key, 'Unknown')


def parse_browser_family(browser_key):
    """Attempts to parse Piwik browser key codes into corresponding browser names

    :param browser_key: Browser keycode
    :return: Browser name
    """
    return lookup_data.browser_keys.get(browser_key, 'Unknown')


def timestamp_components(timestamp):
    return {
        'hour_of_day': timestamp.hour,
        'day_of_week': timestamp.isoweekday(),
        'day_of_month': timestamp.day,
        'month': timestamp.month,
        'year': timestamp.year,
    }

if __name__ == "__main__":
    init_app(set_backends=True, routes=False)
    main()
