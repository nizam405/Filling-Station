# Generated by Django 4.1.3 on 2023-03-06 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Expenditure', '0009_alter_expendituregroup_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenditure',
            name='amount',
            field=models.IntegerField(null=True, verbose_name='টাকা'),
        ),
    ]
