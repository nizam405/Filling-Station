# Generated by Django 4.1.3 on 2023-03-14 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0012_fixedasset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownersequity',
            name='month',
            field=models.CharField(choices=[(1, 'জানুয়ারি'), (2, 'ফেব্রুয়ারি'), (3, 'মার্চ'), (4, 'এপ্রিল'), (5, 'মে'), (6, 'জুন'), (7, 'জুলাই'), (8, 'আগস্ট'), (9, 'সেপ্টেম্বর'), (10, 'অক্টোবর'), (11, 'নভেম্বর'), (12, 'ডিসেম্বর')], default=3, max_length=20, verbose_name='মাস'),
        ),
    ]