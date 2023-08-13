import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.db import transaction
from .fetch_coordinates import fetch_coordinates
from locations.fetch_coordinates import create_location
from locations.models import Location


from .models import Product, Order, OrderItem, RestaurantMenuItem, Restaurant


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
         model = Order
         fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    order_info = request.data
    locations = Location.objects.all()
    serializer_order = OrderSerializer(data=order_info)
    serializer_order.is_valid(raise_exception=True)
    client_address = serializer_order.validated_data['address']
    if client_address not in locations.values_list('address', flat=True):
        lon, lat = create_location(serializer_order.validated_data['address'], settings.YANDEX_GEOCODER_API_KEY)
    else:
        lon = Location.objects.get(address=client_address).lon
        lat = Location.objects.get(address=client_address).lat
    order = Order.objects.create(
        firstname=serializer_order.validated_data['firstname'],
        lastname=serializer_order.validated_data['lastname'],
        phonenumber=serializer_order.validated_data['phonenumber'],
        address=serializer_order.validated_data['address'],
        lat=lat,
        lon=lon,
    )

    for products in serializer_order.validated_data['products']:
        order_item = OrderItem.objects.create(
            product=products['product'],
            quantity=products['quantity'],
            price=products['product'].price * products['quantity'],
            order=order
        )

    return Response(serializer_order.data, status=201)
