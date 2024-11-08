from django.apps import AppConfig


class WalkappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'walkapp'

    def ready(self):
        import walkapp.signals