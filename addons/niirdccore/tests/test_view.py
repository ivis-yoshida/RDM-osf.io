# # -*- coding: utf-8 -*-
# from rest_framework import status as http_status
# from flask import request
# from django.db.models import Subquery

# import mock
# import pytest
# from nose.tools import *  # noqa

# from framework.auth import Auth
# from addons.base.tests.views import (
#     OAuthAddonAuthViewsTestCaseMixin, OAuthAddonConfigViewsTestCaseMixin
# )
# from tests.base import OsfTestCase, get_default_metaschema
# from osf_tests.factories import ProjectFactory, UserFactory, InstitutionFactory
# from admin.rdm_addons.utils import get_rdm_addon_option

# from website.util import api_url_for
# from addons.niirdccore.tests.utils import NiirdccoreAddonTestCase
# from addons.niirdccore import apps, models, views

# # pytestmark = pytest.mark.django_db

# class TestNiirdccoreViews(NiirdccoreAddonTestCase,  OsfTestCase):

#     def setUp(self):
#         super(TestNiirdccoreViews, self).setUp()
#         self.set_node_settings(self.node_settings)

#     @mock.patch.object(models.AddonList, 'set_node_id')
#     @mock.patch.object(models.AddonList, 'set_addon_id')
#     @mock.patch.object(models.AddonList, 'set_callback')
#     @mock.patch.object(models.AddonList, 'set_owner')
#     # @mock.patch.object(apps.AddonAppConfig, 'node_settings', NodeFactory)
#     def test_niirdccore_apply_dmp_subscribe(self, mock_about, set_node_id, set_addon_id, set_callback):
#         mock_about.return_value = None
#         # super(TestNiirdccoreViews, self).test_niirdccore_apply_dmp_subscribe()

#         institution = InstitutionFactory()
#         self.user.affiliated_institutions.add(institution)
#         self.user.is_staff = True
#         self.user.save()

#         print(type(self))

#         rdm_addon_option = get_rdm_addon_option(institution.id, 'niirdccore')
#         rdm_addon_option.is_allowed = False
#         rdm_addon_option.save()

#         # url = self.project.api_url_for('niirdccore_dmp_notification')
#         # res = self.app.get(url, auth=self.user.auth)

#         # mock_node = ProjectFactory()
#         # mock_node.set_addon(self.node_settings)
#         mock_user = UserFactory()
#         mock_user.is_staff = True
#         mock_node = ProjectFactory(creator=self.user)

#         subscript = views.niirdccore_apply_dmp_subscribe(
#             auth=mock_user,
#             # auth=Auth(user=mock_user),
#             node=mock_node,
#             # node=self,
#             addon_id='test',
#             callback='test.callback')
#         assertIsNone(subscript)

#     #! mock sample (from: https://qiita.com/East-Da/items/211d06359a7573116eb7#%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E3%81%AE%E9%96%A2%E6%95%B0%E3%82%92mock%E3%81%99%E3%82%8B)
#     # def test_notification_mock_handler_200(mocker):
#     #     """
#     #     callback関数が200を返すようする。
#     #     """
#     #     status_code = 200
#     #     url = "https://hogehoge.com"
#     #     mocker.patch("views.niirdccore_dmp_notification._notification_handler", return_value=status_code)

#     #     assert sample1(url) == status_code

#     # def test_sample2_mock_requests_200(mocker):
#     #     """
#     #     sample2関数で実行されるrequests.getを置き換える。
#     #     また、返り値もMockでstatus_codeが200で返るように置き換える。
#     #     """
#     #     status_code = 200
#     #     url = "https://hogehoge.com"
#     #     response_mock = mocker.Mock()
#     #     response_mock.status_code = status_code
#     #     mocker.patch.object(requests, "get", return_value=response_mock)
#     #     assert sample2(url) == status_code

#     # @mock.patch('addons.niirdccore.views.niirdccore_dmp_notification._notification_handler', return_value=200)
#     # @mock.patch.object(request, 'json', return_value='dmp_record')
#     # @mock.patch.object(views.niirdccore_dmp_notification, 'addon_list', return_value=)
#     # @mock.patch.object(Subquery, 'objects.filter', return_value=[{'callback':'test'}])
#     def test_niirdccore_dmp_notification(self):
#         # mocker.patch("views.niirdccore_dmp_notification._notification_handler", return_value=status_code)

#         # with pytest.raises(KeyError):
#         #     with mock.patch('addons.niirdccore.models.AddonList') as addonList_mock:
#         #         addonList_mock.objects = mock.MagicMock(return_value=True)
#         #         addonList_mock.objects.filter = mock.MagicMock(return_value=True)
#         #         self.assertFalse(addonList_mock.objects.filter.called)


#         with mock.patch('addons.niirdccore.models.AddonList') as addonList_mock:
#             addonList_mock.objects = mock.MagicMock(return_value=True)
#             addonList_mock.objects.filter = mock.MagicMock(return_value=True)
#             self.assertFalse(addonList_mock.objects.filter.called)

#         # mock_addonList = mock.Mock()
#         # mock_addonList =
#         # mock.patch.object(models.AddonList.objects, 'filter', return_value=mock_addonList)

#         url = self.project.api_url_for('niirdccore_dmp_notification')
#         res = self.app.get(url, auth=self.user.auth)
#         assertIsNone(res)

#     # def test_jupyterhub_empty_services(self):
#     #     self.node_settings.set_services([])
#     #     self.node_settings.save()
#     #     url = self.project.api_url_for('jupyterhub_get_services')
#     #     res = self.app.get(url, auth=self.user.auth)
#     #     assert_equals(len(res.json['data']), 0)

#     # def test_jupyterhub_services(self):
#     #     self.node_settings.set_services([('jh1', 'https://jh1.test/')])
#     #     self.node_settings.save()
#     #     url = self.project.api_url_for('jupyterhub_get_services')
#     #     res = self.app.get(url, auth=self.user.auth)
#     #     import_url = 'https://jh1.test/rcosrepo/import/' + \
#     #                  self.node_settings.owner._id
#     #     assert_equals(len(res.json['data']), 1)
#     #     assert_equals(res.json['data'][0]['name'], 'jh1')
#     #     assert_equals(res.json['data'][0]['base_url'], 'https://jh1.test/')
#     #     assert_equals(res.json['data'][0]['import_url'], import_url)
