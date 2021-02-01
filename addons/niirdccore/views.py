# -*- coding: utf-8 -*-
from rest_framework import status as http_status
from flask import request
from django.db.models import Subquery
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
from addons.niirdccore.models import AddonList

from addons import *
from addons.jupyterhub.models import NodeSettings

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

    if dataAnalysisResources:
        try:
            typeName = dataAnalysisResources["type"]
            serviceName = dataAnalysisResources["name"]
            baseUrl = dataAnalysisResources["url"]
        except KeyError:
            raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

        if typeName == JupyterhubAddonAppConfig.full_name \
            or typeName ==  JupyterhubAddonAppConfig.short_name:

            # add jupyterHub
            node.add_addon(JupyterhubAddonAppConfig.short_name, auth=None, log=False)
            jupyterHub = node.get_addon(JupyterhubAddonAppConfig.short_name)
            jupyterHub.set_services([(serviceName, baseUrl)])

            return {"result": "jupyterhub added"}

    return {"result": "jupyterhub none"}

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
                    'attributes': dmp_info.json()}}

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

#! dummy fetch API_key method
@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def fetch_dmr_api_key(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    # クエリパラメータ（APIキー）を取得
    token_string = urllib.parse.urlparse(request.url).query.split('token=')
    dmr_api_key = token_string[1]

    # APIキーをDBへ保存
    addon.set_dmr_api_key(dmr_api_key)

    # DMP閲覧画面へ遷移
    return use_ember_app()
