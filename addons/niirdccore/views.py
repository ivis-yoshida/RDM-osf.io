# -*- coding: utf-8 -*-
from rest_framework import status as http_status
from flask import request
import logging
import requests
#!
import urllib.parse
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import SHORT_NAME
from . import settings
from framework.exceptions import HTTPError
from website.project.decorators import (
    must_be_valid_project,
    must_have_permission,
    must_have_addon,
)
from website.ember_osf_web.views import use_ember_app
from addons.jupyterhub.apps import JupyterhubAddonAppConfig

logger = logging.getLogger(__name__)

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_set_config(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    try:
        dmp_id = request.json['dmp']['redboxOid']
        dmp_metadata = request.json['dmp']['metadata']

        # fetch API key
        dmr_api_key = request.json['dmr_api_key']
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    # save dmp_id, API key
    addon.set_dmp_id(dmp_id)
    addon.set_dmr_api_key(dmr_api_key)

    # provisioning
    dataAnalysisResources = dmp_metadata.get("vivo:Dataset_redbox:DataAnalysisResources")

    if dataAnalysisResources == JupyterhubAddonAppConfig.full_name \
        or dataAnalysisResources ==  JupyterhubAddonAppConfig.short_name:

        # add jupyterHub
        node.add_addon(JupyterhubAddonAppConfig.short_name, auth=None, log=False)
    else:
        return {"result": "jupyterhub none"}

    return {"result": "jupyterhub added"}

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_get_dmp_info(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    dmp_id = addon.get_dmp_id()
    url = settings.DMR_URL + 'v1/dmp/' + str(dmp_id)
    headers = {'Authorization': 'Bearer ' + addon.get_dmr_api_key()}
    response = requests.get(url, headers=headers)
    data = response.json()

    dataset = niirdccore_dataset_dammy()

    # return {'data': {'id': node._id, 'type': 'dmp-status',
    #                 'attributes': data['dmp'],
    #                 'relationships': {
    #                     'dataset': {
    #                         'links': {'related': 'http://localhost:5000/api/v1/project/256df/niirdccore/dmp-dataset'}
    #                     }
    #                 }}
    #         }

    return {'data': {'id': node._id, 'type': 'dmp-status',
                    'attributes': data['dmp'],
                    'relationships': {
                        'dmp-dataset': {
                            'data': [{'id': '1', 'type': 'dmp-dataset'}]
                        }
                    }},
            'embeds': [
                {
                    #'id': '1', 'type': 'dmp-dataset', 'attributes': {'dataset': data['dmp']['dataset'][0]},
                    'id': '1', 'type': 'dmp-dataset', 'attributes': {'title': 'データセットタイトル１', 'dataset_id': {'type': 'dataset', 'identifier': 'abcd'}},
                    'relationships': {'dmp-status': {'data': {'id': node._id, 'type': 'dmp-status'}}}
                }]
            }

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_niirdccore(**kwargs):
    return use_ember_app()

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_apply_dmp_subscribe(**kwargs):
    node = kwargs['node']
    addon = node.get_addon(SHORT_NAME)
    addon_list = AddonList()

    addon_list.set_node_id(node._id)
    addon_list.set_addon_id(kwargs['addon_id'])
    addon_list.set_callback(kwargs['callback'])
    addon_list.set_owner(node.get_addon(SHORT_NAME))

    return

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_dmp_notification(**kwargs):
    node = kwargs['node']

    # コールバック関数を呼び出す関数
    def _notification_handler(func, **kwargs):
        return func(**kwargs)

    # リクエストボディ取得
    try:
        dmp_record = request.json['dmp']
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    addon_list = AddonList.objects.filter(node_id=node._id)

    for addon in addon_list:
        # デコレータ対策のため、nodeも引数に含める
        _notification_handler(
            func=eval(addon.callback),
            node=node,
            dmp_record=dmp_record)

    return

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def addonList_all_clear(**kwargs):
    AddonList.objects.all().delete()
    return "all list data deleted"

#! dummy DMR method
@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def dmr_dummy(**kwargs):
    return "200 OK"

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_get_dataset(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    dmp_id = addon.get_dmp_id()
    url = settings.DMR_URL + '/v1/dmp/' + str(dmp_id)
    headers = {'Authorization': 'Bearer ' + addon.get_dmr_api_key()}
    response = requests.get(url, headers=headers)
    data = response.json()
    dataset = data['dmp']['dataset']
    #dataset = data['dataset']

    return {'data': {'id': node._id, 'type': 'dmp-dataset',
                    'attributes': data}}
@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_update_dataset(**kwargs):
    return 200

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def niirdccore_create_dataset(**kwargs):
    return 200

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_niirdccore(**kwargs):
    return use_ember_app()

# dammy start
def niirdccore_dammy(**kwargs):
    return {
        "version": 1,
         "dmp": {
            "dmp_id": {
            "identifier": "6f19e6f0ce79cd0c87c1e498ada46078",
            "type": "other"
            },
            "contact": {
            "contact_id": {
                "identifier": "dmr_user_a@rdm.nii.ac.jp",
                "type": "orcid"
            },
            "mbox": "tsunekawa@nii.ac.jp",
            "name": "Tsunekawa Mao",
            "role": "Data manager",
            },
            "project": {
            "title": "タイトルAAAA",
            "description": "説明BBBB",
            "project_id": "プロジェクトIDXXXX",
            "keywords": "キーワードCCCC",
            "website": "プロジェクトのウェブサイトDDD",
            "start": "2020-01-20",
            "end": "2021-01-31",
            "funding": {
                "funder_name": "研究費助成元EEE",
                "grand_id":{
                "identifier": "研究費助成番号FFF"
                },
            },
            "type": "研究活動の種別GGG"
            },
            "contributors": [
                {
                "contact_id": {
                    "identifier": "dmr_user_b@rdm.nii.ac.jp",
                    "type": "orcid"
                },
                "mbox": "tsunekawa@nii.ac.jp", "name": "Tsunekawa Mao", "role" : "Chief Investigator"
                },
                {
                "contact_id": {
                    "identifier": "dmr_user_c@rdm.nii.ac.jp",
                    "type": "other"
                },
                "mbox": "junko.sasaki@ivis.co.jp", "name": "Sasaki Junko", "role": "role1"
                },
            ],
            "dataset": [
                {
                    "dataset_id": {
                        "type": "other",
                        "identifier": "fajfowerguraheh"
                    },
                    "title": "新エネルギー研究実験データ",
                    "description": "新エネルギー研究実験データです。",
                    "type": "dataset",
                    "access_policy": "CC-BYで公開しています。",
                    "data_access": "open",
                    "issued": "2021-04-01",
                    "creator": {
                        "name": "John Due",
                        "mbox": "john@example.com",
                        "creator_id": {
                            "type": "orcid",
                            "identifier": "xxxx-example-0000"
                        }
                    },
                    "contact": {
                        "name": "John Due",
                        "mbox": "john@example.com",
                        "contact_id": {
                            "type": "orcid",
                            "identifier": "xxxx-example-0000"
                        }
                    },
                    "distribution":
                        {
                            "host": {
                                "title": "X大学リポジトリ",
                                "url": "https://repository.example.com/"
                            },
                            "title": "新エネルギー研究実験データ",
                            "access_url": "https://doi.org/XXXXX/XXX",
                            "byte_size": "1GB未満",
                            "license": {
                                "name": "Creative Commons Lisense 4.0 BY",
                                "lisence_ref": "https://creativecommons.org/licenses/by/4.0/",
                                "start-date": "2021-04-01"
                            }
                        }
                },
                {
                    "dataset_id": {
                        "type": "other",
                        "identifier": "aaaaaaaaaaaaaaa"
                    },
                    "title": "新エネルギー研究実験データ２",
                    "description": "新エネルギー研究実験データです。",
                    "type": "dataset",
                    "access_policy": "CC-BYで公開しています。",
                    "data_access": "open",
                    "issued": "2021-04-01",
                    "creator": {
                        "name": "John Due",
                        "mbox": "john@example.com",
                        "creator_id": {
                            "type": "orcid",
                            "identifier": "xxxx-example-0000"
                        }
                    },
                    "contact": {
                        "name": "John Due",
                        "mbox": "john@example.com",
                        "contact_id": {
                            "type": "orcid",
                            "identifier": "xxxx-example-0000"
                        }
                    },
                    "distribution":
                        {
                            "host": {
                                "title": "X大学リポジトリ",
                                "url": "https://repository.example.com/"
                            },
                            "title": "新エネルギー研究実験データ",
                            "access_url": "https://doi.org/XXXXX/XXX",
                            "byte_size": "1GB未満",
                            "license": {
                                "name": "Creative Commons Lisense 4.0 BY",
                                "lisence_ref": "https://creativecommons.org/licenses/by/4.0/",
                                "start-date": "2021-04-01"
                            }
                        }
                }
            ],
            "created": "2020-09-18T06:14:02.604Z",
            "modified": "2020-10-20T05:27:04.069Z"
        }
     }
def niirdccore_dataset_dammy(**kwargs):
    return {
        "dataset":
        [
            {
                "dataset_id": {
                    "type": "other",
                    "identifier": "fajfowerguraheh"
                },
                "title": "新エネルギー研究実験データ",
                "description": "新エネルギー研究実験データです。",
                "type": "dataset",
                "access_policy": "CC-BYで公開しています。",
                "data_access": "open",
                "issued": "2021-04-01",
                "creator": {
                    "name": "John Due",
                    "mbox": "john@example.com",
                    "creator_id": {
                        "type": "orcid",
                        "identifier": "xxxx-example-0000"
                    }
                },
                "manager": {
                    "name": "John Due",
                    "mbox": "john@example.com",
                    "manager_id": {
                        "type": "orcid",
                        "identifier": "xxxx-example-0000"
                    }
                },
                "distribution":
                    {
                        "host": {
                            "title": "X大学リポジトリ",
                            "url": "https://repository.example.com/"
                        },
                        "title": "新エネルギー研究実験データ",
                        "access_url": "https://doi.org/XXXXX/XXX",
                        "byte_size": "1GB未満",
                        "license": {
                            "name": "Creative Commons Lisense 4.0 BY",
                            "lisence_ref": "https://creativecommons.org/licenses/by/4.0/",
                            "start-date": "2021-04-01"
                        }
                    }
            },
            {
                "dataset_id": {
                    "type": "other",
                    "identifier": "aaaaaaaaaaaaaaa"
                },
                "title": "新エネルギー研究実験データ２",
                "description": "新エネルギー研究実験データです。",
                "type": "dataset",
                "access_policy": "CC-BYで公開しています。",
                "data_access": "open",
                "issued": "2021-04-01",
                "creator": {
                    "name": "John Due",
                    "mbox": "john@example.com",
                    "creator_id": {
                        "type": "orcid",
                        "identifier": "xxxx-example-0000"
                    }
                },
                "manager": {
                    "name": "John Due",
                    "mbox": "john@example.com",
                    "manager_id": {
                        "type": "orcid",
                        "identifier": "xxxx-example-0000"
                    }
                },
                "distribution":
                    {
                        "host": {
                            "title": "X大学リポジトリ",
                            "url": "https://repository.example.com/"
                        },
                        "title": "新エネルギー研究実験データ",
                        "access_url": "https://doi.org/XXXXX/XXX",
                        "byte_size": "1GB未満",
                        "license": {
                            "name": "Creative Commons Lisense 4.0 BY",
                            "lisence_ref": "https://creativecommons.org/licenses/by/4.0/",
                            "start-date": "2021-04-01"
                        }
                    }
            }
        ],
  }
# dammy end
