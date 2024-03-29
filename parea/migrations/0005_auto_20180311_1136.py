# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-11 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parea', '0004_auto_20180311_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalproject',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=120, verbose_name='Название проекта'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=120, unique=True, verbose_name='Название проекта'),
        ),
    ]
