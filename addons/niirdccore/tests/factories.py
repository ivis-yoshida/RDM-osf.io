# -*- coding: utf-8 -*-
"""Factories for the Swift addon."""
import factory
from factory.django import DjangoModelFactory
from osf_tests.factories import ProjectFactory

from addons.niirdccore.models import NodeSettings


class NiirdccoreNodeSettingsFactory(DjangoModelFactory):
    class Meta:
        model =  NodeSettings

    owner = factory.SubFactory(ProjectFactory)
