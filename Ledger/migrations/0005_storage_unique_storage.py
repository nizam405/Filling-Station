# Generated by Django 4.1.3 on 2023-01-27 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ledger', '0004_alter_customerbalance_options_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='storage',
            constraint=models.UniqueConstraint(fields=('year', 'month', 'product'), name='unique_storage'),
        ),
    ]