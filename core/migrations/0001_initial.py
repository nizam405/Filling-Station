# Generated by Django 4.1.3 on 2022-12-03 05:11

import Core.functions
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=Core.functions.current_year)),
            ],
        ),
    ]
