# Generated by Django 4.2.3 on 2024-09-11 13:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0023_alter_ownersequity_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.date(2024, 6, 30)),
            preserve_default=False,
        ),
    ]