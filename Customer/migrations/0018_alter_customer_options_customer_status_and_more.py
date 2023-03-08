# Generated by Django 4.1.3 on 2023-02-23 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0017_alter_customer_serial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['status', 'cust_type', 'group', 'serial', 'name']},
        ),
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.CharField(choices=[('active', 'সক্রিয়'), ('inactive', 'নিষ্ক্রিয়')], default=('active', 'সক্রিয়'), max_length=20, verbose_name='অবস্থা'),
        ),
        migrations.AddField(
            model_name='groupofcompany',
            name='status',
            field=models.CharField(choices=[('active', 'সক্রিয়'), ('inactive', 'নিষ্ক্রিয়')], default=('active', 'সক্রিয়'), max_length=20, verbose_name='অবস্থা'),
        ),
        migrations.AlterField(
            model_name='duecollection',
            name='customer',
            field=models.ForeignKey(limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Customer.customer', verbose_name='ক্রেতা'),
        ),
        migrations.AlterField(
            model_name='duesell',
            name='customer',
            field=models.ForeignKey(limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Customer.customer', verbose_name='ক্রেতা'),
        ),
    ]
