# -*- coding: utf-8 -*-
from rest_framework import status as http_status
from flask import request
from django.db.models import Subquery
import logging
import requests
import json

from osf.models import RdmAddonOption
from addons.niirdccore.models import NodeSettings as CoreNodeSettings
from . import SHORT_NAME
from . import settings
from framework.exceptions import HTTPError
from website.project.decorators import (
    must_be_valid_project,
    must_have_permission,
    must_have_addon,
)
from addons.jupyterhub.apps import JupyterhubAddonAppConfig
from addons.niirdccore.models import AddonList

# 変更通知API用インポート
from addons import *

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
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    # save dmp_id
    addon.set_dmp_id(dmp_id)

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
    url = settings.DMR_URL + '/v1/dmp/' + str(dmp_id)
    headers = {'Authorization': 'Bearer ' + addon.get_dmr_api_key()}
    dmp_info = requests.get(url, headers=headers)

    return {'data': {'id': node._id, 'type': 'dmp-status',
                    'attributes':{'name': 'testname', 'mbox': 'testaddress', 'title': 'testtitle', 'description': 'testdescription'}}}

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def apply_dmp_subscribe(**kwargs):
    node = kwargs['node']

    addon_list = AddonList()

    addon_list.set_addon_id(kwargs['addon_id'])
    addon_list.set_callback(kwargs['callback'])
    addon_list.set_owner(node.get_addon(SHORT_NAME))

    return "SUCCESS( ADDON_ID:{}, CALLBACK:{} )".format(kwargs['addon_id'], kwargs['callback'])

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def dmp_notification(**kwargs):
    # 動的インポート
    # notification_dest = importlib.import_module('addons.testSkelton')

    # コールバック関数呼び出し
    def _notification_handler(func, **kwargs):
        return func(**kwargs)

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    try:
        # MODIFY: fetching request body
        dmp_record = request.json['dmp_record']
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    addon_list = AddonList.objects.all()

    for i in range(len(addon_list)):
        # デコレータ対策のため、nodeも引数に含める
        result = _notification_handler(func=eval(addon_list[i].callback),
            node=node, dmp_record=dmp_record)

    return


@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def addonList_all_clear(**kwargs):
    AddonList.objects.all().delete()
    return "all list data deleted"
