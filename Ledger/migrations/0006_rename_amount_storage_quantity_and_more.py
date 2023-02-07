# Generated by Django 4.1.3 on 2023-02-06 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ledger', '0005_storage_unique_storage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storage',
            old_name='amount',
            new_name='quantity',
        ),
        migrations.AlterField(
            model_name='customerbalance',
            name='month',
            field=models.CharField(choices=[('1', 'জানুয়ারি'), ('2', 'ফেব্রুয়ারি'), ('3', 'মার্চ'), ('4', 'এপ্রিল'), ('5', 'মে'), ('6', 'জুন'), ('7', 'জুলাই'), ('8', 'আগস্ট'), ('9', 'সেপ্টেম্বর'), ('10', 'অক্টোবর'), ('11', 'নভেম্বর'), ('12', 'ডিসেম্বর')], default=1, max_length=20, verbose_name='মাস'),
        ),
        migrations.AlterField(
            model_name='groupofcompanybalance',
            name='amount',
            field=models.IntegerField(default=0, verbose_name='পরিমাণ'),
        ),
    ]
