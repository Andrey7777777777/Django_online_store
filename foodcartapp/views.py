import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


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


@api_view(['POST'])
def register_order(request):
    try:
        order_info = request.data

        keys_to_check = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
        if not order_info['products'] or not isinstance(order_info['products'], list):
            return Response({'error': 'Список продуктов пуст'}, status=400)

        for product in order_info['products']:
            if not Product.objects.filter(id__contains=product['product']):
                return Response({
                    f'error: Недопустимый первичный ключ {product["product"]}'}, status=400)

        if not isinstance(order_info['firstname'], str):
            return Response({'error': 'В поле firstname положили список.'}, status=400)

        missing_keys =[key for key in keys_to_check if key not in order_info]
        if missing_keys:
            return Response({'error': f'Отсутствуют обязательные  ключи:{missing_keys}'}, status=400)

        empty_field =[key for key, value in order_info.items() if not value]
        if empty_field:
            return Response({'error': f'Это поле не может быть пустым:{empty_field}'}, status=400)

        for digit in range(5):
            if order_info['phonenumber'][digit] == '0':
                return Response({'error': 'phonenumber: Введен некорректный номер телефона'}, status=400)




        order = Order.objects.create(
            name=order_info['firstname'],
            family_name=order_info['lastname'],
            phone=order_info['phonenumber'],
            adress=order_info['address']
        )
        for products in order_info['products']:
            order_item = OrderItem.objects.create(
                product_id=products['product'],
                quantity=products['quantity'],
                order=order
            )
        return Response({'order_id': order.id}, status=201)
    except KeyError:
        return Response({'error': 'key not found'}, status=400)
