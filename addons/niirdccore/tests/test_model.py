from rest_framework import status as http_status
from flask import request
from django.db.utils import DataError
from django.db.transaction import TransactionManagementError
from django.db.models import Subquery

import random
import mock
import pytest
import unittest
from nose.tools import *  # noqa

from framework.auth import Auth
from osf.models.node import Node

from addons.base.tests.views import (
    OAuthAddonAuthViewsTestCaseMixin, OAuthAddonConfigViewsTestCaseMixin
)
from tests.base import OsfTestCase, get_default_metaschema
from osf_tests.factories import ProjectFactory, ProjectWithAddonFactory, UserFactory, InstitutionFactory
from admin.rdm_addons.utils import get_rdm_addon_option

from website.util import api_url_for
from addons.niirdccore import apps, models, views
from addons.niirdccore.tests.utils import NiirdccoreAddonTestCase
from addons.niirdccore.tests.factories import NiirdccoreNodeSettingsFactory

pytestmark = pytest.mark.django_db

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
        self.addon_list.delete()

        # super(TestNodeSettings, self).tearDown()
        self.node.delete()
        self.user.delete()

    # NodeSettings #
    def test_dmp_id_normal(self):
        self.node_settings.set_dmp_id('dmp_id')
        assert_equal(self.node_settings.get_dmp_id(), 'dmp_id')

        self.node_settings.set_dmp_id(111 > 100)
        self.assertTrue(self.node_settings.get_dmp_id())

        self.node_settings.set_dmp_id(None)
        self.assertIsNone(self.node_settings.get_dmp_id())

    def test_add_niirdccore_addon_normal(self):
        mock_node = mock.MagicMock(spec=Node, return_value=True)
        with mock.patch('osf.models.node.Node.has_addon', return_value=True):
            addon_result = self.node_settings.add_niirdccore_addon(mock_node, '2021-03-11')
            self.assertIsNone(addon_result)
            mock_node.add_addon.assert_not_called()


    # AddonList #
    def test_addonList_owner_normal(self):
        self.addon_list.set_owner(self.node_settings)
        self.assertIs(type(self.addon_list.get_owner()), models.NodeSettings)

    def test_addonList_owner_error(self):
        with pytest.raises(ValueError):
            self.addon_list.set_owner(True)

    def test_addonList_node_id_normal(self):
        self.addon_list.set_node_id('123')
        assert_equal(self.addon_list.get_node_id(), '123')

    def test_addonList_callback_normal(self):
        self.addon_list.set_callback('test.views.callback')
        assert_equal(self.addon_list.get_callback(), 'test.views.callback')
