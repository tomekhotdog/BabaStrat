# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0030_auto_20170622_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategy',
            name='framework',
            field=models.TextField(default='.'),
        ),
    ]
