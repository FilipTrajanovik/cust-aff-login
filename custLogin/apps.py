from django.apps import AppConfig


class CustloginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custLogin'

    def ready(self):
        import custLogin.signals