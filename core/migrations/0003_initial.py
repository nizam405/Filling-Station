# Generated by Django 4.2.3 on 2024-11-03 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Core', '0002_delete_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(max_length=255, verbose_name='ব্যবসায় প্রতিষ্ঠানের নাম')),
                ('start_from_beginning', models.BooleanField(default=False, verbose_name='ব্যবসায়ের শুরু থেকে হিসাব রাখতে চাই')),
                ('start_date', models.DateField(verbose_name='হিসাব শুরুর তারিখ')),
            ],
            options={
                'get_latest_by': ['start_date'],
            },
        ),
    ]
