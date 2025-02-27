from django.apps import AppConfig



class CarRepairAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'car_repair_app'

    def ready(self):
        import car_repair_app.signals
