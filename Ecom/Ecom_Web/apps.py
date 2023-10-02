from django.apps import AppConfig


class EcomWebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ecom_Web'

    def ready(self):
        import Ecom_Web.signals  # Import your signal handler function