import pandas as pd
import openpyxl as xl
import requests
import shutil
import os
import hashlib
import json

API_KEY = 'AIzaSyB0WYQHtEbYWgQbrT-6VNrNC_Myq13JXks'


url_2 = r'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={}&key={}'

url_0 = r'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={}&inputtype=textquery&key={}'
url_1 = 'https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields=formatted_address,name,formatted_phone_number,website&key={}'


search_keys = [
    # 'изделия из войлока',
    'валенки',
    # 'одежда из войлока',
    'утеплитель из войлока',
    # 'обувь из войлока',
    'войлок',
    # 'фетр',
    # 'шерсть',
    # 'шерстяные изделия',
    # 'шерстяная одежда',
]
cities = [
    'Нижегородская область',
    'Нижний Новгород',
    'Бор',
    'Кстово',
    'Дзержинск',
    'Лысково',
    'Арзамас',
    'Владимир',
    'Московская область',
    'Москва',
    'Владимирская область',
    'Казань',
    'Чебоксары',
    'Чувашия',
    'Татарстан',
]
with open(r'D:\programming\solutions\google_maps_find\cities.csv', 'r') as f:
    cities = f.read().split('\n')

places_id = set()
results = []

i = 0
f = open(r'D:\programming\solutions\google_maps_find\places_id.txt', 'w')
for search in search_keys:
    for city in cities:
        url = url_0.format(search + '+' + city, API_KEY)
        r = requests.get(url)

        if r.status_code != 200:
            continue

        r = r.json()
        for candidate in r['candidates']:
            place_id = candidate.get('place_id')
            if not place_id or place_id in places_id:
                continue
            i += 1
            print(i, '-', place_id)
            places_id.add(place_id)
            f.write(str(place_id) + '\n')
f.close()

i = 0
for place_id in places_id:
    r = requests.get(url_1.format(place_id, API_KEY))
    if r.status_code != 200:
        continue
    r = r.json()
    i += 1
    print('{} / {} -'.format(i, len(places_id)), r['result'].get('name'))
    results.append(r)

with open(r'D:\programming\solutions\google_maps_find\results.csv', 'w') as f:
    f.write('name|phone|website|address\n')
    for result in results:
        try:
            f.write('"{}"|"{}"|"{}"|"{}"\n'.format(
                result['result'].get('name'),
                result['result'].get('formatted_phone_number'),
                result['result'].get('website'),
                result['result'].get('formatted_address'),
            ))
        except Exception as err:
            print(err)
            continue
