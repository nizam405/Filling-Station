# Generated by Django 4.1.3 on 2022-12-14 01:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0002_rename_widthdraw_ownersequity_withdraw'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='owner',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='ownersequity',
            options={'ordering': ['date']},
        ),
    ]