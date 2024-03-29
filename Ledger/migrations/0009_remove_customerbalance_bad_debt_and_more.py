# Generated by Django 4.1.3 on 2023-02-22 00:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0017_alter_customer_serial'),
        ('Ledger', '0008_customerbalance_bad_debt_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerbalance',
            name='bad_debt',
        ),
        migrations.RemoveField(
            model_name='groupofcompanybalance',
            name='bad_debt',
        ),
        migrations.CreateModel(
            name='BadDebt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(choices=[('1', 'জানুয়ারি'), ('2', 'ফেব্রুয়ারি'), ('3', 'মার্চ'), ('4', 'এপ্রিল'), ('5', 'মে'), ('6', 'জুন'), ('7', 'জুলাই'), ('8', 'আগস্ট'), ('9', 'সেপ্টেম্বর'), ('10', 'অক্টোবর'), ('11', 'নভেম্বর'), ('12', 'ডিসেম্বর')], max_length=20, verbose_name='মাস')),
                ('year', models.IntegerField(choices=[(2022, '২০২২'), (2023, '২০২৩')], default=2023, verbose_name='বছর')),
                ('amount', models.IntegerField(default=0, verbose_name='পরিমাণ')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Customer.customer', verbose_name='পার্টি')),
            ],
            options={
                'ordering': ['-year', '-month', 'customer'],
            },
        ),
    ]
