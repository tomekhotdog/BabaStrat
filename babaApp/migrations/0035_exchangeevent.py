# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-24 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0034_auto_20170624_1114'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=100)),
                ('probability', models.FloatField(default=0)),
            ],
        ),
    ]
