# Generated by Django 4.1.3 on 2023-01-27 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Expenditure', '0006_alter_expendituregroup_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expenditure',
            options={'ordering': ['-date']},
        ),
    ]
