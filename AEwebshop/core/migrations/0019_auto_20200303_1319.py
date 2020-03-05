# Generated by Django 2.2 on 2020-03-03 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20200303_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='ar_category',
            field=models.CharField(choices=[('S', 'ملابس شبابيه'), ('SW', 'ملابس رياضية'), ('OW', 'ملابس للخروج'), ('NU', 'ارقام')], max_length=4),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport wear'), ('OW', 'Outwear'), ('NU', 'Numbers')], max_length=4),
        ),
    ]