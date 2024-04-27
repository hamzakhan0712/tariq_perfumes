from django.apps import AppConfig


class TariquePerfumesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tarique_perfumes_app'

    def ready(self):
        import tarique_perfumes_app.signals