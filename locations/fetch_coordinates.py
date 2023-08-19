import time

import requests
from locations.models import Location


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(base_url, params={
                "geocode": address,
                "apikey": apikey,
                "format": "json",
            })
            response.raise_for_status()
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']

            if not found_places:
                return None

            most_relevant = found_places[0]
            lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
            return lon, lat
        except requests.exceptions.HTTPError:
             time.sleep(2)
    return None, None


def create_location(address, apikey):
    lon, lat = fetch_coordinates(address, apikey)
    Location.objects.get_or_create(
        address=address,
        lat=lat,
        lon=lon,
    )
    return lon, lat