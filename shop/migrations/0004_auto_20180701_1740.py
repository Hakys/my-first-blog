# Generated by Django 2.0.6 on 2018-07-01 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20180630_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=150, blank=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=150, blank=False),
        ),
        migrations.AlterField(
            model_name='fabricante',
            name='name',
            field=models.CharField(max_length=150, blank=False),
        ),
        migrations.AlterField(
            model_name='fabricante',
            name='slug',
            field=models.SlugField(max_length=150, blank=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_url',
            field=models.URLField(null=True, blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='product',
            name='ref',
            field=models.CharField(max_length=30, null=False, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=150, unique=True, null=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=150,  blank=False),
        ),
    ]
