# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-30 18:20
from __future__ import unicode_literals

from django.db import migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('js_services', '0002_service_related'),
        ('aldryn_newsblog', '0033_auto_20181231_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='services',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='js_services.Service', verbose_name='services'),
        ),
    ]