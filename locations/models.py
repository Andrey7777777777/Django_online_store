from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField('Адрес', max_length=300, blank=False, null=False, unique=True)
    lat = models.FloatField('Широта', null=True)
    lon = models.FloatField('Долгота', null=True)
    request_date = models.DateTimeField('Дата запроса', default=timezone.now)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        ordering = ['request_date']
