# Generated by Django 2.0.4 on 2018-05-21 02:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_auto_20180521_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 21, 2, 1, 7, 173121), verbose_name='Última Actualización'),
        ),
    ]
