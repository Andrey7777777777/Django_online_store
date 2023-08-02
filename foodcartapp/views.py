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
        if not order_info['products']:
            raise ValueError
        print(order_info)
        if isinstance(order_info['products'], list) == False:
            raise AssertionError

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
    except AssertionError:
        return Response({'error': 'product key null or not a list'}, status=400)
    except ValueError:
        return Response({'error': 'list is empty'}, status=400)
    except KeyError:
        return Response({'error': 'key not found'}, status=400)
