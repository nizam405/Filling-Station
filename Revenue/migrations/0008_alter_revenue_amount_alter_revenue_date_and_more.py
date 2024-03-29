# Generated by Django 4.1.3 on 2023-01-29 14:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Revenue', '0007_alter_revenue_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revenue',
            name='amount',
            field=models.IntegerField(default=0, verbose_name='টাকা'),
        ),
        migrations.AlterField(
            model_name='revenue',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='revenue',
            name='detail',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='বিবরণ'),
        ),
        migrations.AlterField(
            model_name='revenue',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Revenue.revenuegroup', verbose_name='আয়ের খাত'),
        ),
    ]
