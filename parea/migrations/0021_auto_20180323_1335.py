# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-23 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parea', '0020_auto_20180323_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprojectobject',
            name='synced',
            field=models.CharField(blank=True, default=False, max_length=50, null=True, verbose_name='Синхронизировано'),
        ),
        migrations.AddField(
            model_name='projectobject',
            name='synced',
            field=models.CharField(blank=True, default=False, max_length=50, null=True, verbose_name='Синхронизировано'),
        ),
    ]
