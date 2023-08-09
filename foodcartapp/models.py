from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum
from django.utils import timezone


class OrderQuerySet(models.QuerySet):
    def get_total_price(self):
        return self.annotate(
             total_price=models.Sum(models.F('products__quantity') * models.F('products__product__price'))
         )


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, blank=False, null=False)
    quantity = models.IntegerField('Колличество', validators=[MinValueValidator(0)], default=1, blank=False, null=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='products', blank=False, null=False)
    price = models.DecimalField('Цена', max_digits=8,
                                decimal_places=2,
                                validators=[MinValueValidator(0)],
                                blank=False,
                                null=False,
                                )


class Order(models.Model):
    lastname = models.CharField('Имя', max_length=50, blank=False, null=False)
    firstname = models.CharField('Фамилия', max_length=50, blank=False, null=False)
    phonenumber = PhoneNumberField('Телефон', blank=False, null=False)
    address = models.CharField('Адрес', max_length=300, blank=False, null=False)
    objects = OrderQuerySet.as_manager()
    ORDER_STATUS_CHOICES = [
        ('Новый', 'Новый'),
        ('Готовится', 'Готовитя'),
        ('В пути', 'В пути'),
        ('Доставлен', 'Доставлен')
    ]
    status = models.CharField('Статус заказа', max_length=50, choices=ORDER_STATUS_CHOICES, default='new', blank=False,)
    comment = models.TextField('Комментарий', max_length=300, blank=True, null=True)
    registered_at = models.DateTimeField('Дата регистрации заказа', default=timezone.now, blank=True, null=True)
    called_at = models.DateTimeField('Дата звонка', blank=True, null=True)
    delivered_at = models.DateTimeField('Дата доставки', blank=True, null=True)


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        unique_together = ['lastname', 'firstname', 'phonenumber', 'address']

    def __str__(self):
        return f"{self.lastname} {self.firstname} {self.address}"