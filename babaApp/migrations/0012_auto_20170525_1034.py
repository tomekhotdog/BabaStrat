# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-25 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0011_trade_direction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='close_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
