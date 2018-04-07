# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-14 21:51
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parea', '0018_auto_20180314_1951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalprojectobject',
            name='list1_id',
        ),
        migrations.RemoveField(
            model_name='historicalprojectobject',
            name='list2_id',
        ),
        migrations.RemoveField(
            model_name='historicalprojectobject',
            name='list3_id',
        ),
        migrations.RemoveField(
            model_name='projectobject',
            name='list1_id',
        ),
        migrations.RemoveField(
            model_name='projectobject',
            name='list2_id',
        ),
        migrations.RemoveField(
            model_name='projectobject',
            name='list3_id',
        ),
        migrations.AddField(
            model_name='historicalprojectobject',
            name='files_structure',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}),
        ),
        migrations.AddField(
            model_name='projectobject',
            name='files_structure',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}),
        ),
    ]