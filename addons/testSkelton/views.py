# -*- coding: utf-8 -*-
from rest_framework import status as http_status
from flask import request
import logging
import urllib.request
import json
import requests

from . import SHORT_NAME
from . import settings
from framework.exceptions import HTTPError
from website.project.decorators import (
    must_be_contributor_or_public,
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)
from addons.niirdccore import views as core_views

logger = logging.getLogger(__name__)


@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def myskelton_get_config(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    return {'param_1': addon.get_param_1()}

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def myskelton_set_config(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    try:
        param_1 = request.json['param_1']
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)
    logger.info('param_1: {}'.format(param_1))
    addon.set_param_1(param_1)
    return {}

@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def apply_subscription(**kwargs):
    node = kwargs['node'] or kwargs['project']

    try:
        addon_id = request.json['apply_subscription']['addon_id']
        callback = request.json['apply_subscription']['callback']
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    return core_views.niirdccore_apply_dmp_subscribe(
        node=node,
        addon_id = addon_id,
        callback = callback
    )


@must_be_valid_project
@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def get_notification(**kwargs):
    node = kwargs['node']
    dmp_record = kwargs['dmp_record']
    return "success: " + node._id
    # return dmp_record
