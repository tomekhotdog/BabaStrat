# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-03 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0028_auto_20170603_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='framework_extension',
            field=models.TextField(default='.'),
        ),
    ]