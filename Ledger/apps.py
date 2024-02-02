from django.apps import AppConfig


class LedgerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ledger'

    def ready(self):
        import Ledger.signals  # Import the signals module
