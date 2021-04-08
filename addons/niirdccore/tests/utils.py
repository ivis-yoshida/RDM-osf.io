# -*- coding: utf-8 -*-
from addons.base.tests.base import OAuthAddonTestCaseMixin, AddonTestCase
from tests.base import OsfTestCase
from addons.niirdccore.tests.factories import NiirdccoreNodeSettingsFactory
from addons.niirdccore.models import NodeSettings

class NiirdccoreAddonTestCase(AddonTestCase):
    ADDON_SHORT_NAME       = 'niirdccore'
    OWNERS                 = ['node']
    NODE_USER_FIELD        = None
    ExternalAccountFactory = None
    Provider               = None
    Serializer             = None
    client                 = None
    NodeSettingsFactory    = NiirdccoreNodeSettingsFactory
    NodeSettingsClass      = NodeSettings

    def set_node_settings(self, settings):
        # super(NiirdccoreAddonTestCase, self).set_node_settings(settings)
        return

    def set_user_settings(self, settings):
        return
