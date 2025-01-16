
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0023_alter_duesell_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='duesell',
            old_name='amount',
            new_name='price',
        ),
        migrations.AlterField(
            model_name='duesell',
            name='price',
            field=models.FloatField(null=True, blank=False, verbose_name="মূল্য"),
        ),
    ]
