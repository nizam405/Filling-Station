# Generated by Django 4.1.3 on 2023-01-27 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0012_alter_customer_options_alter_duecollection_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='duecollection',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='duesell',
            options={'ordering': ['-date']},
        ),
    ]
