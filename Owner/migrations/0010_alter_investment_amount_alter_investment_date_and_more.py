# Generated by Django 4.1.3 on 2023-03-06 00:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0009_alter_investment_options_alter_withdraw_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='amount',
            field=models.IntegerField(null=True, verbose_name='পরিমাণ (টাকা)'),
        ),
        migrations.AlterField(
            model_name='investment',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='investment',
            name='detail',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='বিবরণ'),
        ),
        migrations.AlterField(
            model_name='investment',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Owner.owner', verbose_name='মালিক'),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='amount',
            field=models.IntegerField(null=True, verbose_name='পরিমাণ (টাকা)'),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='তারিখ'),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='detail',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='বিবরণ'),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Owner.owner', verbose_name='মালিক'),
        ),
        migrations.CreateModel(
            name='OwnersEquity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(choices=[('1', 'জানুয়ারি'), ('2', 'ফেব্রুয়ারি'), ('3', 'মার্চ'), ('4', 'এপ্রিল'), ('5', 'মে'), ('6', 'জুন'), ('7', 'জুলাই'), ('8', 'আগস্ট'), ('9', 'সেপ্টেম্বর'), ('10', 'অক্টোবর'), ('11', 'নভেম্বর'), ('12', 'ডিসেম্বর')], default=3, max_length=20, verbose_name='মাস')),
                ('year', models.IntegerField(choices=[(2022, '২০২২'), (2023, '২০২৩')], default=2023, verbose_name='বছর')),
                ('amount', models.IntegerField(null=True, verbose_name='পরিমাণ')),
                ('share', models.FloatField(default=0, verbose_name='শতাংশ')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Owner.owner', verbose_name='মালিক')),
            ],
            options={
                'ordering': ['-year', '-month', 'owner'],
            },
        ),
        migrations.AddConstraint(
            model_name='ownersequity',
            constraint=models.UniqueConstraint(fields=('year', 'month', 'owner'), name='unique_ownersequity'),
        ),
    ]
