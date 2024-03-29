# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-23 09:52
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parea', '0019_auto_20180315_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprojectobject',
            name='sync_task_id',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='ID задачи синхронизации'),
        ),
        migrations.AddField(
            model_name='projectobject',
            name='sync_task_id',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='ID задачи синхронизации'),
        ),
        migrations.AlterField(
            model_name='historicalprojectobject',
            name='files_structure',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={'graphs': {}}),
        ),
        migrations.AlterField(
            model_name='projectobject',
            name='files_structure',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={'graphs': {}}),
        ),
    ]
