from django.apps import AppConfig


class PeerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "peer"

    def ready(self):
        import peer.signals
