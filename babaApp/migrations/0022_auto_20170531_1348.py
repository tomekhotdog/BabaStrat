# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-31 13:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0021_auto_20170531_1223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trade',
            name='market',
        ),
        migrations.AddField(
            model_name='trade',
            name='strategy',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='babaApp.Strategy'),
            preserve_default=False,
        ),
    ]
