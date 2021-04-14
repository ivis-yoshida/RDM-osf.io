from rest_framework import status as http_status
from flask import request
from django.db.utils import DataError
from django.db.transaction import TransactionManagementError
from django.db.models import Subquery, QuerySet

import random
import string
import requests
import mock
import pytest
import unittest
from nose.tools import *  # noqa

from framework.auth import Auth
from osf.models import RdmAddonOption
from osf.models.mixins import ContributorMixin
from osf.models.node import Node

from addons.base.tests.views import (
    OAuthAddonAuthViewsTestCaseMixin, OAuthAddonConfigViewsTestCaseMixin
)
from tests.base import OsfTestCase, get_default_metaschema
from osf_tests.factories import ProjectFactory, ProjectWithAddonFactory, UserFactory, InstitutionFactory
from admin.rdm_addons.utils import get_rdm_addon_option

from website.util import api_url_for
from addons.niirdccore import apps, models, views, SHORT_NAME
from addons.niirdccore.tests.utils import NiirdccoreAddonTestCase
from addons.niirdccore.tests.factories import NiirdccoreNodeSettingsFactory

pytestmark = pytest.mark.django_db

def mocked_addon_option(*args, **kwargs):
    class MockAddonOption:
        def __init__(self):
            self.organizational_node = ContributorMixin()

    return MockAddonOption()

class TestNiirdccoreModels(NiirdccoreAddonTestCase, unittest.TestCase):
    _NodeSettingsFactory = NiirdccoreNodeSettingsFactory

    def setUp(self):
        super(TestNiirdccoreModels, self).setUp()
        self.node = ProjectFactory()
        self.user = self.node.creator

        self.node_settings = self._NodeSettingsFactory(owner=self.node)
        self.node_settings.save()

        self.addon_list = models.AddonList()
        self.addon_list.save()

    def tearDown(self):
        try:
            self.addon_list.delete()
            self.node_settings.delete()
            self.node.delete()
            self.user.delete()
        except TransactionManagementError:
            pass
        super(TestNiirdccoreModels, self).tearDown()

    @classmethod
    def generate_string(self, n):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

    # NodeSettings #
    def test_dmp_id(self):
        self.node_settings.set_dmp_id('dmp_id')
        assert_equal(self.node_settings.get_dmp_id(), 'dmp_id')

        self.node_settings.set_dmp_id(111 > 100)
        self.assertTrue(self.node_settings.get_dmp_id())

        self.node_settings.set_dmp_id(None)
        self.assertIsNone(self.node_settings.get_dmp_id())

    def test_dmr_api_key(self):
        self.node_settings.set_dmr_api_key('dmp_id')
        assert_equal(self.node_settings.get_dmr_api_key(), 'dmp_id')

        self.node_settings.set_dmr_api_key(111 > 100)
        self.assertTrue(self.node_settings.get_dmr_api_key())

        self.node_settings.set_dmr_api_key(None)
        self.assertIsNone(self.node_settings.get_dmr_api_key())

    def test_add_niirdccore_addon(self):
        with mock.patch('osf.models.node.Node.has_addon', return_value=False),\
        mock.patch('django.db.models.QuerySet.first', side_effect=mocked_addon_option),\
        mock.patch('osf.models.mixins.ContributorMixin.is_contributor', return_value=True),\
        mock.patch('osf.models.node.Node.add_addon'):
            addon_result = self.node_settings.add_niirdccore_addon(self.node, '2021-03-11')
            self.assertIsNone(addon_result)
            self.node.add_addon.assert_called()

    def test_add_niirdccore_addon_not_available(self):
        with mock.patch('website.settings.ADDONS_AVAILABLE_DICT', return_value=[]),\
        mock.patch('django.db.models.QuerySet.first'),\
        mock.patch('osf.models.node.Node.add_addon'):
            addon_result = self.node_settings.add_niirdccore_addon(self.node, '2021-03-11')
            self.assertIsNone(addon_result)
            QuerySet.first.assert_not_called()
            self.node.add_addon.assert_not_called()


    def test_add_niirdccore_addon_already_has_addon(self):
        with mock.patch('osf.models.node.Node.has_addon', return_value=True),\
        mock.patch('django.db.models.QuerySet.first'),\
        mock.patch('osf.models.node.Node.add_addon'):
            addon_result = self.node_settings.add_niirdccore_addon(self.node, '2021-03-11')
            self.assertIsNone(addon_result)
            QuerySet.first.assert_not_called()
            self.node.add_addon.assert_not_called()

    def test_add_niirdccore_addon_option_is_none(self):
        with mock.patch('osf.models.node.Node.has_addon', return_value=False), \
        mock.patch('django.db.models.QuerySet.first', return_value=None),\
        mock.patch('osf.models.node.Node.add_addon'):
            addon_result = self.node_settings.add_niirdccore_addon(self.node, '2021-03-11')
            self.assertIsNone(addon_result)
            QuerySet.first.assert_called()
            self.node.add_addon.assert_not_called()

    def test_add_niirdccore_addon_not_contributor(self):
        with mock.patch('osf.models.node.Node.has_addon', return_value=False), \
        mock.patch('django.db.models.QuerySet.first', side_effect=mocked_addon_option),\
        mock.patch('osf.models.mixins.ContributorMixin.is_contributor', return_value=False),\
        mock.patch('osf.models.node.Node.add_addon'):
            addon_result = self.node_settings.add_niirdccore_addon(self.node, '2021-03-11')
            self.assertIsNone(addon_result)
            QuerySet.first.assert_called()
            self.node.add_addon.assert_not_called()

    def test_node_monitoring(self):
        self.node_settings.set_dmp_id('dummy')
        with mock.patch('addons.niirdccore.models.NodeSettings.dmp_update'):
            self.node_settings.node_monitoring(self.node, '2021-03-11')
            self.node_settings.dmp_update.assert_called()

    def test_node_monitoring_not_available(self):
        with mock.patch('website.settings.ADDONS_AVAILABLE_DICT', return_value=[]),\
        mock.patch('osf.models.node.Node.get_addon'):
            self.node_settings.node_monitoring(self.node, '2021-03-11')
            self.node.get_addon.assert_not_called()

    def test_node_monitoring_sender_is_none(self):
        self.node_settings.set_dmp_id('dummy')
        with mock.patch('osf.models.node.Node.get_addon', return_value=None),\
        mock.patch('addons.niirdccore.models.NodeSettings.dmp_update'):
            self.node_settings.node_monitoring(self.node, '2021-03-11')
            self.node_settings.dmp_update.assert_not_called()

    def test_node_monitoring_dmp_id_none(self):
        with mock.patch('addons.niirdccore.models.NodeSettings.dmp_update'):
            self.node_settings.node_monitoring(self.node, '2021-03-11')
            self.node_settings.dmp_update.assert_not_called()

    def test_dmp_update(self):
        self.node_settings.set_dmp_id('dummy')
        self.node_settings.set_dmr_api_key('dummy')
        with mock.patch('requests.put'):
            self.node_settings.dmp_update(self.node)
            requests.put.assert_called()

    # AddonList #
    def test_addonList_owner(self):
        self.addon_list.set_owner(self.node_settings)
        self.assertIs(type(self.addon_list.get_owner()), models.NodeSettings)

    def test_addonList_owner_error(self):
        with pytest.raises(ValueError):
            self.addon_list.set_owner(True)

    def test_addonList_node_id(self):
        self.addon_list.set_node_id('123')
        assert_equal(self.addon_list.get_node_id(), '123')

        max_length = TestNiirdccoreModels.generate_string(100)
        self.addon_list.set_node_id(max_length)
        assert_equal(self.addon_list.get_node_id(), max_length)


    def test_addonList_node_id_error(self):
        with pytest.raises(DataError):
            overflow = TestNiirdccoreModels.generate_string(101)
            self.addon_list.set_node_id(overflow)

    def test_addonList_addon_id(self):
        self.addon_list.set_addon_id('123')
        assert_equal(self.addon_list.get_addon_id(), '123')

        max_length = TestNiirdccoreModels.generate_string(50)
        self.addon_list.set_addon_id(max_length)
        assert_equal(self.addon_list.get_addon_id(), max_length)

    def test_addonList_addon_id_error(self):
        with pytest.raises(DataError):
            overflow = TestNiirdccoreModels.generate_string(51)
            self.addon_list.set_addon_id(overflow)

    def test_addonList_callback(self):
        self.addon_list.set_callback('123')
        assert_equal(self.addon_list.get_callback(), '123')

        max_length = TestNiirdccoreModels.generate_string(100)
        self.addon_list.set_callback(max_length)
        assert_equal(self.addon_list.get_callback(), max_length)

    def test_addonList_callback_error(self):
        with pytest.raises(DataError):
            overflow = TestNiirdccoreModels.generate_string(101)
            self.addon_list.set_node_id(overflow)
