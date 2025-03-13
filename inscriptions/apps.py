from django.apps import AppConfig


from django.apps import AppConfig

class InscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inscriptions'

    def ready(self):
        import inscriptions.signals  # Assurez-vous que l'import est bien indenté avec 4 espaces
