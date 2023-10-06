from django.apps import AppConfig



class AdminpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminpanel'

    def ready(self):
        import adminpanel.signals  # Import your signal handler function