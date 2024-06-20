from django.db import models

class StorageQuerySet(models.QuerySet):
    def with_monthly_profit_upadate(self):
        for item in self:
            item.monthly_profit_update = item.quantity * item.product.monthly_profit_rate_update
        return self

class StorageManager(models.Manager):
    def get_queryset(self):
        return StorageQuerySet(self.model, using=self._db)

    def with_monthly_profit_upadate(self):
        return self.get_queryset().with_monthly_profit_upadate()