from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'Core'

    def ready(self):
        import Core.signals  # Import the signals module
