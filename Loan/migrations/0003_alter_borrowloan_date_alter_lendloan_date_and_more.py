# Generated by Django 4.2.3 on 2023-10-25 08:48

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Loan', '0002_remove_borrowloan_loan_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowloan',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, help_text='YYYY-MM-DD', verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='lendloan',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, help_text='YYYY-MM-DD', verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='refundborrowedloan',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, help_text='YYYY-MM-DD', verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='refundborrowedloan',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='Loan.borrowloan', verbose_name='হাওলাদ'),
        ),
        migrations.AlterField(
            model_name='refundlendedloan',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, help_text='YYYY-MM-DD', verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='refundlendedloan',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='Loan.lendloan', verbose_name='হাওলাদ'),
        ),
    ]
