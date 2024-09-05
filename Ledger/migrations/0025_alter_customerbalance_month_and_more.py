# Generated by Django 4.1.3 on 2024-09-05 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ledger', '0024_alter_customerbalance_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerbalance',
            name='month',
            field=models.IntegerField(choices=[(1, 'জানুয়ারি'), (2, 'ফেব্রুয়ারি'), (3, 'মার্চ'), (4, 'এপ্রিল'), (5, 'মে'), (6, 'জুন'), (7, 'জুলাই'), (8, 'আগস্ট'), (9, 'সেপ্টেম্বর'), (10, 'অক্টোবর'), (11, 'নভেম্বর'), (12, 'ডিসেম্বর')], default=8, verbose_name='মাস'),
        ),
        migrations.AlterField(
            model_name='groupofcompanybalance',
            name='month',
            field=models.IntegerField(choices=[(1, 'জানুয়ারি'), (2, 'ফেব্রুয়ারি'), (3, 'মার্চ'), (4, 'এপ্রিল'), (5, 'মে'), (6, 'জুন'), (7, 'জুলাই'), (8, 'আগস্ট'), (9, 'সেপ্টেম্বর'), (10, 'অক্টোবর'), (11, 'নভেম্বর'), (12, 'ডিসেম্বর')], default=8, verbose_name='মাস'),
        ),
        migrations.AlterField(
            model_name='profit',
            name='month',
            field=models.IntegerField(choices=[(1, 'জানুয়ারি'), (2, 'ফেব্রুয়ারি'), (3, 'মার্চ'), (4, 'এপ্রিল'), (5, 'মে'), (6, 'জুন'), (7, 'জুলাই'), (8, 'আগস্ট'), (9, 'সেপ্টেম্বর'), (10, 'অক্টোবর'), (11, 'নভেম্বর'), (12, 'ডিসেম্বর')], default=8, verbose_name='মাস'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='month',
            field=models.IntegerField(choices=[(1, 'জানুয়ারি'), (2, 'ফেব্রুয়ারি'), (3, 'মার্চ'), (4, 'এপ্রিল'), (5, 'মে'), (6, 'জুন'), (7, 'জুলাই'), (8, 'আগস্ট'), (9, 'সেপ্টেম্বর'), (10, 'অক্টোবর'), (11, 'নভেম্বর'), (12, 'ডিসেম্বর')], default=8, verbose_name='মাস'),
        ),
    ]
