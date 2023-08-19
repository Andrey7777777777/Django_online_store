from django.conf import settings
from rest_framework.serializers import ModelSerializer

from locations.fetch_coordinates import create_location
from locations.models import Location
from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    def create(self, validated_data):
        client_address = validated_data['address']
        locations = Location.objects.values_list('address', flat=True)
        if client_address not in locations.values_list('address', flat=True):
            lon, lat = create_location(validated_data['address'], settings.YANDEX_GEOCODER_API_KEY)
        else:
            lon = Location.objects.get(address=client_address).lon
            lat = Location.objects.get(address=client_address).lat
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
            lat=lat,
            lon=lon,
        )

        for products in validated_data['products']:
            order_item = OrderItem.objects.create(
                product=products['product'],
                quantity=products['quantity'],
                price=products['product'].price * products['quantity'],
                order=order
            )
        return order

    class Meta:
         model = Order
         fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

