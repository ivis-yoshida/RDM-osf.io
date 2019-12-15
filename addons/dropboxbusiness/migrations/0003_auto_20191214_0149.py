# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-12-14 01:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addons_dropboxbusiness', '0002_auto_20191212_0913'),
    ]

    operations = [
        migrations.AddField(
            model_name='nodesettings',
            name='fileaccess_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dropboxbusiness_fileaccess_option', to='osf.RdmAddonOption'),
        ),
        migrations.AddField(
            model_name='nodesettings',
            name='management_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dropboxbusiness_management_option', to='osf.RdmAddonOption'),
        ),
    ]
