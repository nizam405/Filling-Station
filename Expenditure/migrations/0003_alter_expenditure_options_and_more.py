# Generated by Django 4.1.3 on 2022-12-14 01:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Expenditure', '0002_alter_expenditure_detail'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expenditure',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='expendituregroup',
            options={'ordering': ['name']},
        ),
    ]
