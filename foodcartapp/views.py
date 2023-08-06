import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer


from .models import Product, Order, OrderItem


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
         fields = ['firstname', 'lastname', 'phonenumber', 'adress', 'products']


@api_view(['POST'])
def register_order(request):
    order_info = request.data
    serializer_order = OrderSerializer(data=order_info)
    serializer_order.is_valid(raise_exception=True)
    order = Order.objects.create(
        firstname=serializer_order.validated_data['firstname'],
        lastname=serializer_order.validated_data['lastname'],
        phonenumber=serializer_order.validated_data['phonenumber'],
        adress=serializer_order.validated_data['adress']
    )
    for products in serializer_order.validated_data['products']:
        order_item = OrderItem.objects.create(
            product=products['product'],
            quantity=products['quantity'],
            order=order
        )
    return Response({'id': order.id,
                     'firstname': serializer_order.validated_data['firstname'],
                     'lastname': serializer_order.validated_data['lastname'],
                     'phonenumber': serializer_order.validated_data['phonenumber'],
                     'adress': serializer_order.validated_data['adress']
                     })
