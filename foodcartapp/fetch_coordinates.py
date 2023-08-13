import time

import requests
from environs import Env


def fetch_coordinates(apikey, address):
    env = Env()
    env.read_env()
    apikey = env.str("YANDEX_GEOCODER_API_KEY")
    base_url = "https://geocode-maps.yandex.ru/1.x"
    while True:
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