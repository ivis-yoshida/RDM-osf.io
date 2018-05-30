# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-29 19:46
from __future__ import unicode_literals

from django.db import migrations, models

from django.contrib.contenttypes.models import ContentType


def set_preprint_identifier_catetory_to_datacite(apps, *args, **kwargs):

    PreprintService = apps.get_model('osf', 'PreprintService')
    Identifier = apps.get_model('osf', 'Identifier')

    preprint_content_type = ContentType.objects.get_for_model(PreprintService)
    Identifier.objects.filter(content_type_id=preprint_content_type.id, category='doi').update(category='datacite_doi')

def return_preprint_identifier_category_to_doi(apps, *args, **kwargs):
    PreprintService = apps.get_model('osf', 'PreprintService')
    Identifier = apps.get_model('osf', 'Identifier')

    preprint_content_type = ContentType.objects.get_for_model(PreprintService)
    Identifier.objects.filter(content_type=preprint_content_type, category='datacite_doi').update(category='doi')


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0105_add_identifier_deleted_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identifier',
            name='category',
            field=models.CharField(max_length=20),
        ),
        migrations.RunPython(set_preprint_identifier_catetory_to_datacite, return_preprint_identifier_category_to_doi)
    ]
