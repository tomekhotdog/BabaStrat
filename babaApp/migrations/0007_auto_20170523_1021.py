# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-23 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('babaApp', '0006_portfolio_trade_tradingsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='portfolio',
            name='current_value',
            field=models.FloatField(default=10000),
        ),
        migrations.AddField(
            model_name='trade',
            name='portfolio',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='babaApp.Portfolio'),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='start_value',
            field=models.FloatField(default=10000),
        ),
        migrations.AlterField(
            model_name='trade',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='trade',
            name='value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tradingsettings',
            name='close_position_loss_limit',
            field=models.FloatField(default=5),
        ),
        migrations.AlterField(
            model_name='tradingsettings',
            name='close_position_yield',
            field=models.FloatField(default=5),
        ),
        migrations.AlterField(
            model_name='tradingsettings',
            name='required_trade_confidence',
            field=models.FloatField(default=100),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='babaApp.User'),
        ),
        migrations.AddField(
            model_name='tradingsettings',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='babaApp.User'),
        ),
    ]
