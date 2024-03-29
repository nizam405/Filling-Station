# Generated by Django 4.1.3 on 2022-12-03 13:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CashBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.FloatField(default=0)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]
