from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coloby.cowork"

    def ready(self):
        import coloby.cowork.signals