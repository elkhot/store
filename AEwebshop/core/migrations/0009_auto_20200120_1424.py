# Generated by Django 2.2 on 2020-01-20 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200120_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=models.IntegerField(null=True),
        ),
    ]
