# Generated by Django 4.1.3 on 2023-01-27 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0023_alter_storagereading_product_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductGroup',
        ),
    ]