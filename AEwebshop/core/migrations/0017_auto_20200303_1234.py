# Generated by Django 2.2 on 2020-03-03 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20200303_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ref_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
