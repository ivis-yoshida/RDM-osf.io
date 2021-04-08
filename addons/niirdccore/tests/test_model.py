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

# pytestmark = pytest.mark.django_db

class TestNiirdccoreModels(NiirdccoreAddonTestCase, unittest.TestCase):

    def setUp(self):
        super(TestNiirdccoreModels, self).setUp()
        self.set_node_settings(self.node_settings)
        # self.dummy_project = ProjectWithAddonFactory(addon='niirdccore')
        self.addon_list = models.AddonList()

################################ NodeSettings ###################################
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


################################ AddonList #######################################
    def test_addonList_owner_normal(self):
        self.addon_list.set_owner(self.node_settings)
        self.assertIs(type(self.addon_list.get_owner()), models.NodeSettings)

    def test_addonList_owner_error(self):
        with pytest.raises(ValueError):
            self.addon_list.set_owner(True)

    def test_addonList_node_id_normal(self):
        self.addon_list.set_node_id('123')
        assert_equal(self.addon_list.get_node_id(), '123')

        # set Max length
        # self.addon_list.set_node_id(
        #     '0000000000\
        #     1111111111\
        #     2222222222\
        #     3333333333\
        #     4444444444'
        # )
        # assert_equal(
        #     self.addon_list.get_node_id(),
        #     '0000000000\
        #     1111111111\
        #     2222222222\
        #     3333333333\
        #     4444444444'
        # )

    # def test_addonList_node_id_error(self):
    #     with pytest.raises(DataError):
    #         self.addon_list.set_node_id(
    #         '0000000000\
    #         1111111111\
    #         2222222222\
    #         3333333333\
    #         4444444444\
    #         5'
    #     )

    #     with pytest.raises(TransactionManagementError):
    #         self.addon_list.set_node_id(True)
    #         self.addon_list.set_node_id(11111)
    #         self.addon_list.set_node_id(111.11)

    def test_addonList_addon_id_normal(self):
        self.addon_list.set_addon_id('55555')
        assert_equal(self.addon_list.get_addon_id(), '55555')

        # set max length
        # self.addon_list.set_addon_id(
        #     '00000000001111111111222222222233333333334444444444'
        # )

        # assert_equal(self.addon_list.get_addon_id(), '00000000001111111111222222222233333333334444444444')

    # def test_addonList_addon_id_error(self):
    #     with pytest.raises(DataError):
    #         self.addon_list.set_addon_id(
    #             '000000000011111111112222222222333333333344444444445'
    #         )

    #     with pytest.raises(TransactionManagementError):
    #         self.addon_list.set_node_id(True)
    #         self.addon_list.set_node_id(11111)
    #         self.addon_list.set_node_id(111.11)

    # def test_addonList_callback_normal(self):
    #     self.addon_list.set_callback('test.views.callback')
    #     assert_equal(self.addon_list.get_callback(), 'test.views.callback')

    #     # set Max length
    #     self.addon_list.set_callback(
    #         '0000000000111111111122222222223333333333444444444455555555556666666666777777777788888888889999999999'
    #     )
    #     assert_equal(
    #         self.addon_list.get_callback(),
    #         '0000000000111111111122222222223333333333444444444455555555556666666666777777777788888888889999999999'
    #     )

    # def test_addonList_callback_error(self):
    #     with pytest.raises(DataError):
    #         self.addon_list.set_callback(
    #         '00000000001111111111222222222233333333334444444444555555555566666666667777777777888888888899999999990'
    #     )

    #     with pytest.raises(TransactionManagementError):
    #         self.addon_list.set_callback(True)
    #         self.addon_list.set_callback(11111)
    #         self.addon_list.set_callback(111.11)
