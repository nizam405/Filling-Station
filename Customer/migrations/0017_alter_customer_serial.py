# Generated by Django 4.1.3 on 2023-02-14 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0016_alter_duesell_product_alter_duesell_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='serial',
            field=models.SmallIntegerField(default=100, verbose_name='ক্রম'),
        ),
    ]
