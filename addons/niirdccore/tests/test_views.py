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

from framework.auth import Auth
from addons.base.tests.views import (
    OAuthAddonAuthViewsTestCaseMixin, OAuthAddonConfigViewsTestCaseMixin
)
from tests.base import OsfTestCase, get_default_metaschema
from osf_tests.factories import ProjectFactory, UserFactory, InstitutionFactory
from admin.rdm_addons.utils import get_rdm_addon_option

from website.util import api_url_for
from addons.niirdccore.tests.utils import NiirdccoreAddonTestCase
from addons.niirdccore import apps, models, views, SHORT_NAME

# pytestmark = pytest.mark.django_db

class TestNiirdccoreViews(NiirdccoreAddonTestCase,  OsfTestCase):

    # def setUp(self):
    #     super(TestNiirdccoreViews, self).setUp()
    #     self.set_node_settings(self.node_settings)

    # @mock.patch.object(models.AddonList, 'set_node_id')
    # @mock.patch.object(models.AddonList, 'set_addon_id')
    # @mock.patch.object(models.AddonList, 'set_callback')
    # @mock.patch.object(models.AddonList, 'set_owner')
    # @mock.patch.object(apps.AddonAppConfig, 'node_settings', NodeFactory)
    # def test_niirdccore_apply_dmp_subscribe(self):

        # self.node_settings.set_dmp_id('78c0f674a39962f2a70f7e9a9d783805')
        # self.node_settings.save()
        # url = self.project.api_url_for('{}_apply_dmp_subscribe'.format(SHORT_NAME))
        # res = self.app.get(
        #     url,
        #     auth=self.user.auth,
        #     node=self.nodesettings,
        #     addon_id='test',
        #     callback='test.callback'
        # )
        # assertIsNone(subscript)
        # subscript = views.niirdccore_apply_dmp_subscribe(
        #     auth=self.user.auth,
        #     # auth=Auth(user=mock_user),
        #     # node=mock_node,
        #     node=self.project,
        #     addon_id='test',
        #     callback='test.callback')


    #! mock sample (from: https://qiita.com/East-Da/items/211d06359a7573116eb7#%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E3%81%AE%E9%96%A2%E6%95%B0%E3%82%92mock%E3%81%99%E3%82%8B)

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

    # @mock.patch('requests.get', mock.Mock(return_value=200))
    # @mock.path('requests.Response.raise_for_status', mock.Mock(return_value=requests.Response()))
    # def test_niirdccore_get_dmp_info(self):
        # status_code = 200
        # response_mock = mock.Mock()
        # response_mock.status_code = status_code
        # mock.patch.object(requests, "get", return_value=response_mock)

        # self.node_settings.set_dmp_id('78c0f674a39962f2a70f7e9a9d783805')
        # self.node_settings.set_dmr_api_key('dummy_key')

        # url = self.project.api_url_for('{}_get_dmp_info'.format(SHORT_NAME))
        # res = self.app.get(url, auth=self.user.auth)
        # assert_equals(res.status_code, 200)

    def test_niirdccore_get_dmp_info_denied(self):
        with pytest.raises(AppError):
            url = self.project.api_url_for('{}_get_dmp_info'.format(SHORT_NAME))
            res = self.app.get(url, auth=self.user.auth)
            assert_equals(res.status_code, 410)

    # def test_niirdccore_update_dmp_info(self):
    #     self.node_settings.set_dmp_id('78c0f674a39962f2a70f7e9a9d783805')
    #     self.node_settings.set_dmr_api_key('dummy_key')

    #     url = self.project.api_url_for('{}_update_dmp_info'.format(SHORT_NAME))

    #     # create dataset
    #     res = self.app.patch_json(
    #         url,
    #         {
    #             'data': {
    #                 'attributes': {
    #                     'dataset': [
    #                         {
    #                             'datasetIsNew': 'true',
    #                             'datasetId': {
    #                                 'identifier': 'dummy_dataset_id'
    #                             }
    #                         }
    #                     ]
    #                 }
    #             }
    #         },
    #         auth=self.user.auth,
    #     )
    #     assert_equals(res.status_code, 200)

    #     res = self.app.patch_json(
    #         url,
    #         {
    #             'data': {
    #                 'attributes': {
    #                     'dataset': [
    #                         {
    #                             'datasetIsNew': 'false',
    #                             'datasetId': {
    #                                 'identifier': 'dummy_dataset_id'
    #                             }
    #                         }
    #                     ]
    #                 }
    #             }
    #         },
    #         auth=self.user.auth,
    #     )

    def test_niirdccore_update_dmp_info_denied(self):
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
