# Generated by Django 2.0.6 on 2018-07-01 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20180701_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=150),
        ),
        migrations.AlterField(
            model_name='fabricante',
            name='name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='fabricante',
            name='slug',
            field=models.SlugField(max_length=150),
        ),
    ]
