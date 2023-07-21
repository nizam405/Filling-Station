# Generated by Django 4.2.3 on 2023-07-20 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0015_alter_ownersequity_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownersequity',
            name='amount',
            field=models.FloatField(null=True, verbose_name='পরিমাণ'),
        ),
        migrations.AlterField(
            model_name='ownersequity',
            name='profit',
            field=models.FloatField(default=0, verbose_name='মুনাফা'),
        ),
    ]
