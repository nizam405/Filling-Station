# Generated by Django 4.1.3 on 2023-01-23 00:42

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0020_delete_storage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.CharField(choices=[('Loose', 'লুস'), ('Pack', 'প্যাক')], default=('Pack', 'প্যাক'), max_length=20, verbose_name='ধরন'),
        ),
        migrations.CreateModel(
            name='StorageReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('tank_deep', models.FloatField(default=0, verbose_name='ট্যাংক ডিপ')),
                ('lorry_load', models.FloatField(default=0, verbose_name='লোড')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Product.product', verbose_name='মাল')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]
