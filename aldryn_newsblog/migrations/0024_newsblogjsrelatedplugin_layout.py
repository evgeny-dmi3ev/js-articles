# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-02 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_newsblog', '0023_auto_20181002_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsblogjsrelatedplugin',
            name='layout',
            field=models.CharField(default='columns', max_length=30, verbose_name='layout'),
            preserve_default=False,
        ),
    ]