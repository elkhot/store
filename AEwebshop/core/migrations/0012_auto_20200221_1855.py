# Generated by Django 2.2 on 2020-02-21 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20200121_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='apartment_address',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street_address',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip',
            field=models.CharField(max_length=100, null=True),
        ),
    ]