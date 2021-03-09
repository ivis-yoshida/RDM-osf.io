# -*- coding: utf-8 -*-
from rest_framework import status as http_status

import mock
import pytest
from nose.tools import *  # noqa

from framework.auth import Auth
from addons.base.tests.views import (
    OAuthAddonAuthViewsTestCaseMixin, OAuthAddonConfigViewsTestCaseMixin
)
from tests.base import OsfTestCase, get_default_metaschema
from osf_tests.factories import ProjectFactory, NodeFactory, InstitutionFactory
from admin.rdm_addons.utils import get_rdm_addon_option

from website.util import api_url_for
from addons.niirdccore.tests.utils import NiirdccoreAddonTestCase
from addons.niirdccore import apps, models, views

pytestmark = pytest.mark.django_db

class TestNiirdccoreViews(NiirdccoreAddonTestCase,  OsfTestCase):
    client = models.NodeSettings

    def setUp(self):
        super(TestNiirdccoreViews, self).setUp()
        self.set_node_settings(self.node_settings)

    @mock.patch.object(models.AddonList, 'set_node_id')
    @mock.patch.object(models.AddonList, 'set_addon_id')
    @mock.patch.object(models.AddonList, 'set_callback')
    @mock.patch.object(models.AddonList, 'set_owner')
    def test_niirdccore_apply_dmp_subscribe(self):
        # mock_about.return_value = None
        # super(TestNiirdccoreViews, self).test_niirdccore_apply_dmp_subscribe()

        institution = InstitutionFactory()
        self.user.affiliated_institutions.add(institution)
        self.user.save()

        rdm_addon_option = get_rdm_addon_option(institution.id, 'niirdccore')
        rdm_addon_option.is_allowed = False
        rdm_addon_option.save()

        subscript = views.niirdccore_apply_dmp_subscribe(
            auth=self.user.auth,
            node=NodeFactory(),
            # node=self,
            addon_id='test',
            callback='test.callback')
        assertIsNone(subscript)
