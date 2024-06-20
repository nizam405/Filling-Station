# Generated by Django 4.2.3 on 2024-01-27 05:27

import Transaction.functions
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0031_alter_purchase_date_alter_rate_date_alter_sell_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rate',
            options={'get_latest_by': 'date', 'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='ChangedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=Transaction.functions.next_to_last_balance_date)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.product')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]