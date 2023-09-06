from django.db.models.signals import pre_save
from django.dispatch import receiver

from foodcartapp.models import Order


@receiver(pre_save, sender=Order)
def update_order_status(sender, instance, **kwargs):
    if instance.pk:
        current_order = Order.objects.filter(pk=instance.pk).first()
    if current_order and current_order.restaurateur != instance.restaurateur:
        if instance.status == 'Новый':
            instance.status = 'Готовится'
    elif instance.status == 'Готовится' and instance.restaurateur is None:
        instance.status = 'Новый'