# Generated by Django 4.2.3 on 2024-09-11 13:48

import Transaction.functions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0024_owner_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='owner',
            name='date_created',
            field=models.DateField(default=Transaction.functions.last_balance_date),
        ),
    ]