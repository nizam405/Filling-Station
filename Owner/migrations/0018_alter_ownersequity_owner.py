# Generated by Django 4.2.3 on 2023-10-25 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0017_alter_ownersequity_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownersequity',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Owner.owner', verbose_name='মালিক'),
            preserve_default=False,
        ),
    ]