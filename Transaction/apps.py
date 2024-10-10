from django.apps import AppConfig


class TransactionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Transaction'

    def ready(self):
        import Transaction.signals  # Import the signals module
