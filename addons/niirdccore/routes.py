"""
Routes associated with the niirdccore addon
"""

from framework.routing import Rule, json_renderer
from website.routes import notemplate
from . import SHORT_NAME
from . import views

# HTML endpoints
page_routes = {
    'rules': [
        # Home (Base) | GET
        Rule(
            [
                '/<pid>/{}'.format(SHORT_NAME),
                '/<pid>/node/<nid>/{}'.format(SHORT_NAME),
            ],
            'get',
            views.project_niirdccore,
            notemplate
        ),

    ]
}

# JSON endpoints
api_routes = {
    'rules': [
        Rule([
            '/project/<pid>/{}/settings'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/settings'.format(SHORT_NAME),
        ], 'post', views.niirdccore_set_config, json_renderer),
        Rule([
            '/project/<pid>/{}/dmp'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dmp'.format(SHORT_NAME),
        ], 'get', views.niirdccore_get_dmp_info, json_renderer),
        Rule([
            '/project/{}/dmp_notification'.format(SHORT_NAME),
        ], 'post', views.niirdccore_dmp_notification, json_renderer),
        Rule([
            '/project/<pid>/{}/ADDONLIST_ALL_CLEAR'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/ADDONLIST_ALL_CLEAR'.format(SHORT_NAME),
        ], 'post', views.addonList_all_clear, json_renderer),
        Rule([
            '/project/<pid>/{}/DMR_DUMMY'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/DMR_DUMMY'.format(SHORT_NAME),
        ], 'get', views.dmr_dummy, json_renderer),
        Rule([
            '/project/<pid>/{}/fetch_dmr_api_key'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/fetch_dmr_api_key'.format(SHORT_NAME),
        ], 'get', views.fetch_dmr_api_key, json_renderer),
    ],
    'prefix': '/api/v1',
}
