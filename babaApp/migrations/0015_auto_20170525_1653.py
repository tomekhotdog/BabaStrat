# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-25 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0014_framework_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='framework',
            name='symbol',
            field=models.CharField(max_length=30, verbose_name=' '),
        ),
    ]