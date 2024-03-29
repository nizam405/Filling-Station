# Generated by Django 4.1.3 on 2023-03-10 01:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0011_ownersequity_profit'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixedAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='তারিখ')),
                ('name', models.CharField(max_length=255, verbose_name='নাম')),
                ('detail', models.CharField(blank=True, max_length=255, null=True, verbose_name='বিবরণ')),
                ('price', models.IntegerField(null=True, verbose_name='মূল্য')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
