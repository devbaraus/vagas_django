from django.apps import AppConfig


class EmpregaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "emprega"

    def ready(self):
        import emprega.signals