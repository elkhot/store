# Generated by Django 2.2 on 2020-01-21 15:09

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200120_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='country',
            field=django_countries.fields.CountryField(default='Egypt', max_length=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='customer_name',
            field=models.CharField(default='Said', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='email',
            field=models.EmailField(default='elkhot@gmail.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=models.IntegerField(default='00201026680536'),
            preserve_default=False,
        ),
    ]
