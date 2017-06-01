# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-31 12:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0019_auto_20170531_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategy',
            name='market',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='babaApp.Market'),
        ),
        migrations.AlterField(
            model_name='trade',
            name='market',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='babaApp.Market'),
        ),
        migrations.AlterField(
            model_name='tradingsettings',
            name='strategy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='babaApp.Strategy'),
        ),
    ]