from django.apps import AppConfig
import foodcartapp.signals


class FoodcartappConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'foodcartapp'
