# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-01 00:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0022_auto_20170531_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='market_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='strategy',
            name='framework',
            field=models.TextField(default='.'),
        ),
    ]
