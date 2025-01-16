# Generated by Django 4.2.17 on 2025-01-13 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0035_consumestock_excess_initialstock_purchaserate_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='purchase',
            index=models.Index(fields=['product', 'date', 'purchase_rate'], name='Product_pur_product_c1877e_idx'),
        ),
        migrations.AddIndex(
            model_name='sell',
            index=models.Index(fields=['product', 'date', 'selling_rate'], name='Product_sel_product_e1b9d4_idx'),
        ),
    ]
