# -*- coding: utf-8 -*-
from rest_framework import status as http_status
from flask import request
import logging
import urllib.request

from . import SHORT_NAME
from . import settings
from framework.exceptions import HTTPError
from website.project.decorators import (
    must_be_contributor_or_public,
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)

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
    addon = node.get_addon(SHORT_NAME)

    addon_id = ""
    dmp_endpoint = ""
    try:
        addon_id = request.json['apply_subscription']['addon_id']
        dmp_endpoint = request.json['apply_subscription']['dmp_endpoint']
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    apply_subscription_url = "localhost:5000/api/v1/project/nsxh4/niirdccore/apply_subscription"
    access_token = "OYk9qDbP6eaSK24aHyUTKfU7VcgYAOaoshj1l6OAPjn2U3eIWEbSGaG9fZIguC92L38sS2"
    request_body = {
        "apply_subscription": {
            "addon_id": addon_id,
            "dmp_endpoint": dmp_endpoint,
        }
    }
    request_headers = {
        "Content-Type": "application/json",
        "Authorization": "OAuth2" + access_token,
    }
    apply_subscription_request = urllib.request.Request(
        apply_subscription_url,
        json.dumps(request_body).encode(),
        request_headers
    )
    with urllib.request.urlopen(req) as res:
        body = res.read()

    return "success"
