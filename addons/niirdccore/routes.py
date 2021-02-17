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
            '/project/<pid>/{}/dmp_notification'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dmp_notification'.format(SHORT_NAME),
        ], 'post', views.niirdccore_dmp_notification, json_renderer),
        Rule([
            '/project/<pid>/{}/ADDONLIST_ALL_CLEAR'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/ADDONLIST_ALL_CLEAR'.format(SHORT_NAME),
        ], 'post', views.addonList_all_clear, json_renderer),
        Rule([
            '/project/<pid>/{}/DMR_DUMMY/v1/dmp/<dmp_id>'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/DMR_DUMMY/v1/dmp/<dmp_id>'.format(SHORT_NAME),
        ], 'get', views.dmr_dummy, json_renderer),
        Rule([
            '/project/<pid>/{}/dmp-dataset'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dmp-dataset'.format(SHORT_NAME),
        ], 'get', views.niirdccore_get_dataset, json_renderer),
        Rule([
            '/project/<pid>/{}/dmp-dataset'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dmp-dataset'.format(SHORT_NAME),
        ], 'patch', views.niirdccore_update_dataset, json_renderer),
        Rule([
            '/project/<pid>/{}/dmp-dataset'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dmp-dataset'.format(SHORT_NAME),
            '/project/null/{}/dmp-dataset'.format(SHORT_NAME),
            '/project/null/node/<nid>/{}/dmp-dataset'.format(SHORT_NAME),
        ], 'post', views.niirdccore_create_dataset, json_renderer),
        # dammy start
        Rule([
            '/project/<pid>/{}/dammy/v1/dmp/<dmp_id>'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dammy/v1/dmp/<dmp_id>'.format(SHORT_NAME),
        ], 'get', views.niirdccore_dammy, json_renderer),
        Rule([
            '/project/<pid>/{}/dammy/v1/dataset/<dmp_id>'.format(SHORT_NAME),
            '/project/<pid>/node/<nid>/{}/dammy/v1/dataset/<dmp_id>'.format(SHORT_NAME),
        ], 'get', views.niirdccore_dataset_dammy, json_renderer),
        # dammy end
    ],
    'prefix': '/api/v1',
}
