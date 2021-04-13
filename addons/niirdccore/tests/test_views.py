# -*- coding: utf-8 -*-
from rest_framework import status as http_status
from flask import request
from django.db.models import Subquery

import http
import requests
import socket
import mock
import pytest
import webtest
from webtest.app import AppError
from nose.tools import *  # noqa

import framework
from framework.auth import Auth
from framework.exceptions import HTTPError
from addons.base.tests.views import (
    OAuthAddonAuthViewsTestCaseMixin, OAuthAddonConfigViewsTestCaseMixin
)
from tests.base import OsfTestCase, get_default_metaschema
from osf_tests.factories import ProjectFactory, AuthUserFactory, InstitutionFactory
from admin.rdm_addons.utils import get_rdm_addon_option

import website
from website.util import api_url_for
from addons.niirdccore.tests.utils import NiirdccoreAddonTestCase
from addons.niirdccore import apps, models, settings, views, SHORT_NAME

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def raise_for_status(self):
            response = requests.Response()
            response.status_code = self.status_code
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                raise HTTPError(http_status.HTTP_410_GONE)

        def json(self):
            return self.json_data

    if kwargs['headers']['Authorization'] == 'Bearer valid':
        return MockResponse({'dmp': 'dummy_value'}, 200)
    else:
        return MockResponse({'dmp': 'null'}, 405)

class TestNiirdccoreViews(NiirdccoreAddonTestCase,  OsfTestCase):
    def test_niirdccore_set_config(self):
        # jupyterhub none
        url = self.project.api_url_for('{}_set_config'.format(SHORT_NAME))
        res = self.app.post_json(
            url,
            {
                'dmp': {
                    'redboxOid': '78c0f674a39962f2a70f7e9a9d783805',
                    'metadata':{}
                },
                'dmr_api_key': '5b7da054-34cc-4109-8474-40eef2dbe738'
            },
            auth=self.user.auth,
        )
        assert_equals(res.status_code, 200)
        assert_equals(res.json, { 'result': 'jupyterhub none' })

        # jupyterhub added
        res = self.app.post_json(
            url,
            {
                'dmp': {
                    'redboxOid': '78c0f674a39962f2a70f7e9a9d783805',
                    'metadata':{
                        'vivo:Dataset_redbox:DataAnalysisResources': {
                            'type': 'jupyterhub',
                            'name': 'DEMOPRESTIGESERVICE',
                            'url': 'https://google.com'
                        },
                    }
                },
                'dmr_api_key': '5b7da054-34cc-4109-8474-40eef2dbe738'
            },
            auth=self.user.auth,
        )
        assert_equals(res.status_code, 200)
        assert_equals(res.json, { 'result': 'jupyterhub added' })

    def test_niirdccore_set_config_denied(self):
        with pytest.raises(AppError):
            url = self.project.api_url_for('{}_set_config'.format(SHORT_NAME))
            res = self.app.post_json(
                url,
                {
                    'dmp': {
                        'redboxOid': '78c0f674a39962f2a70f7e9a9d783805',
                        'metadata':{}
                    },
                    # 'dmr_api_key': '5b7da054-34cc-4109-8474-40eef2dbe738'
                },
                auth=self.user.auth,
            )
            assert_equals(res.status_code, 400)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch.object(settings.defaults, 'DMR_URL', return_value='http://dummy_domain.com/')
    def test_niirdccore_get_dmp_info(self, mock_get, dummy_url):
        expected_res = {'data': {'id': self.project._id, 'type': 'dmp-status', 'attributes': 'dummy_value'}}

        self.node_settings.set_dmp_id('valid')
        self.node_settings.set_dmr_api_key('valid')

        url = self.project.api_url_for('{}_get_dmp_info'.format(SHORT_NAME))
        res = self.app.get(url, auth=self.user.auth, url_validity=True)
        assert_equals(res.status_code, 200)
        assert_equals(res.json, expected_res)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch.object(settings.defaults, 'DMR_URL', return_value='http://dummy_domain.com/')
    def test_niirdccore_get_dmp_info_dmp_id_none(self, mock_get, dummy_url):
        with pytest.raises(AppError):
            url = self.project.api_url_for('{}_get_dmp_info'.format(SHORT_NAME))
            res = self.app.get(url, auth=self.user.auth)
            assert_equals(res.status_code, 410)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('requests.Response.raise_for_status', side_effect=requests.exceptions.HTTPError)
    @mock.patch.object(settings.defaults, 'DMR_URL', return_value='http://dummy_domain.com/')
    def test_niirdccore_get_dmp_info_request_exception(self, err, mock_get, dummy_url):
        url = self.project.api_url_for('{}_get_dmp_info'.format(SHORT_NAME))
        self.node_settings.set_dmp_id('dummy_id')
        self.node_settings.set_dmr_api_key('dummy_key')
        with pytest.raises(AppError):
            res = self.app.get(url, auth=self.user.auth)
            assert_equal(res.status_code, 410)
            assert_equal(res.body, b'{"message_short": "Resource deleted", "message_long": "User has deleted this content. If this should not have occurred and the issue persists, please report it to <a href=\\"mailto:fake-support@osf.io\\">fake-support@osf.io</a>.", "code": 410, "referrer": null}')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('requests.post', side_effect=mocked_requests_get)
    @mock.patch('requests.put', side_effect=mocked_requests_get)
    @mock.patch.object(settings.defaults, 'DMR_URL', return_value='http://dummy_domain.com/')
    def test_niirdccore_update_dmp_info(self, mock_get, mock_post, mock_put, dummy_url):
        self.node_settings.set_dmp_id('valid')
        self.node_settings.set_dmr_api_key('valid')

        url = self.project.api_url_for('{}_update_dmp_info'.format(SHORT_NAME))

        # create dataset
        res = self.app.patch_json(
            url,
            {
                'data': {
                    'attributes': {
                        'dataset': [
                            {
                                'datasetIsNew': 'true',
                                'datasetId': {
                                    'identifier': 'dummy_dataset_id'
                                }
                            }
                        ]
                    }
                }
            },
            auth=self.user.auth,
        )
        assert_equals(res.status_code, 200)

        # update dataset
        res = self.app.patch_json(
            url,
            {
                'data': {
                    'attributes': {
                        'dataset': [
                            {
                                'datasetIsNew': 'false',
                                'datasetId': {
                                    'identifier': 'dummy_dataset_id'
                                }
                            }
                        ]
                    }
                }
            },
            auth=self.user.auth,
        )
        assert_equals(res.status_code, 200)

    @mock.patch.object(settings.defaults, 'DMR_URL', return_value='http://dummy_domain.com/')
    def test_niirdccore_update_dmp_info_denied(self, dummy_url):
        with pytest.raises(AppError):
            self.node_settings.set_dmp_id('78c0f674a39962f2a70f7e9a9d783805')

            url = self.project.api_url_for('{}_update_dmp_info'.format(SHORT_NAME))
            res = self.app.patch_json(
                url,
                {
                    'data': {}
                },
                auth=self.user.auth,
            )
            assert_equals(res.status_code, 200)

    def test_niirdccore_apply_dmp_subscribe(self):
        self.node_settings.set_dmp_id('dummy_id')
        subscript = views.niirdccore_apply_dmp_subscribe(
            node=self.project,
            user=self.user,
            addon_id='test',
            callback='test.callback')

    def test_niirdccore_apply_dmp_subscribe_denied(self):
        with pytest.raises(framework.exceptions.HTTPError):
            self.node_settings.set_dmp_id('dummy_id')
            subscript = views.niirdccore_apply_dmp_subscribe(
                node=self.project,
                auth=self.user.auth,
                addon_id='test',
                callback='test.callback')

    def test_niirdccore_dmp_notification(self):
        url = self.project.api_url_for('{}_dmp_notification'.format(SHORT_NAME))
        res = self.app.post_json(
            url,
            { 'dmp': {'data': 'this is dummy'}},
            auth=self.user.auth,
        )
        assert_equals(res.status_code, 200)
        assert_equals(res.body, b'null')

    def test_niirdccore_dmp_notification_denied(self):
        with pytest.raises(AppError):
            url = self.project.api_url_for('{}_dmp_notification'.format(SHORT_NAME))
            res = self.app.post_json(
                url,
                { 'dmp': {'data': 'this is dummy'}},
                # auth=self.user.auth,
            )

            url = self.project.api_url_for('{}_dmp_notification'.format(SHORT_NAME))
            res = self.app.post_json(
                url,
                {},
                auth=self.user.auth,
            )
            assert_equals(res.status_code, 400)
            assert_equals(res.body, b'{"message_short": "Bad request", "message_long": "If this should not have occurred and the issue persists, please report it to <a href=\\"mailto:fake-support@osf.io\\">fake-support@osf.io</a>.", "code": 400, "referrer": null}')
