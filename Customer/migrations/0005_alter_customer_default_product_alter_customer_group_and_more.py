# Generated by Django 4.1.3 on 2022-12-14 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0005_alter_purchase_options_alter_sell_options_and_more'),
        ('Customer', '0004_alter_customer_options_alter_duecollection_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='default_product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Product.product'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Customer.groupofcompany'),
        ),
        migrations.AlterField(
            model_name='duecollection',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Customer.customer'),
        ),
        migrations.AlterField(
            model_name='duesell',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Customer.customer'),
        ),
        migrations.AlterField(
            model_name='duesell',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Product.product'),
        ),
    ]