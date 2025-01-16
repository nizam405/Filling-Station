from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0033_delete_changedproduct'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='amount',
            new_name='price',
        ),
        migrations.AlterField(
            model_name='purchase',
            name='price',
            field=models.FloatField(null=True, blank=False, verbose_name="মূল্য"),
        ),
        migrations.RenameField(
            model_name='sell',
            old_name='amount',
            new_name='price',
        ),
        migrations.AlterField(
            model_name='sell',
            name='price',
            field=models.FloatField(null=True, blank=False, verbose_name="মূল্য"),
        ),
    ]

