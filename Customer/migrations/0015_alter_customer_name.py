# Generated by Django 4.1.3 on 2023-01-29 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0014_alter_customer_short_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='নাম'),
        ),
    ]