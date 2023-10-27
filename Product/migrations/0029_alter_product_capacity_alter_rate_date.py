# Generated by Django 4.2.3 on 2023-07-16 14:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0028_remove_product_purchase_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='capacity',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='পরিমান'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, help_text='YYYY-MM-DD', verbose_name='কার্যকরের তারিখ (হইতে)'),
        ),
    ]