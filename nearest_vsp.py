import requests
import pandas as pd
import numpy as np

from math import sin, cos, sqrt, acos, radians

MAX_DIST = 100

YA_KEY = ''
BASE_URL = r'https://geocode-maps.yandex.ru/1.x/'

GOOG_KEY = ''
BASE_URL_GOOG = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'

post_data = {}
post_data['apikey'] = YA_KEY

post_data['format'] = 'json'

cnt_adrs = 0
def get_geo_coordinates(adr):
    post_data['geocode'] = adr
    global cnt_adrs
    cnt_adrs += 1
    try:
        r = requests.get(BASE_URL, post_data)
        pos = r.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    except:
        pos = ''
    print(cnt_adrs, '-', adr)
    return pos


def get_geo_coordinates_google(adr):
    pos = ''
    global cnt_adrs
    cnt_adrs += 1
    try:
        r = requests.get(BASE_URL_GOOG.format(adr, GOOG_KEY))
        if r.status_code == 200:
            r = r.json()
            lng = r['results'][0]['geometry']['location']['lng']
            lat = r['results'][0]['geometry']['location']['lat']
            pos = str(lat) + ' ' + str(lng)
            print(cnt_adrs, '-', adr)
    except Exception as err:
        print(err)
    return pos


def get_distance_sph(pos0, pos1):
    r = 6371.0
    x1, y1 = pos0.split()
    x2, y2 = pos1.split()
    y1 = radians(float(y1))
    x1 = radians(float(x1))
    y2 = radians(float(y2))
    x2 = radians(float(x2))

    a = sin(y1) * sin(y2) + cos(y1) * cos(y2) * cos(x1 - x2)

    distance = r * acos(a)
    return distance


def main():

    vsps = pd.read_excel(r'D:\programming\solutions\find_nearest_vsp\2021-04-12\vsps.xlsx', 'vsps')
    targets = pd.read_excel(r'D:\programming\solutions\find_nearest_vsp\2021-04-26\targets.xlsx', 0)
    # vsps = vsps[vsps['cpo'] == 1]
    # vsps['pos'] = vsps.apply(lambda x: get_geo_coordinates(x['address_fact']), axis=1)
    vsps['pos'] = vsps.apply(
        lambda x: get_geo_coordinates_google(x['address_fact']) if x['pos'] == ''
        else x['pos'],
        axis=1)

    vsps.to_excel(r'D:\programming\solutions\find_nearest_vsp\2021-04-05\vsps.xlsx', index=False)

    targets['pos'] = targets.apply(lambda x: get_geo_coordinates_google(x['target']), axis=1)
    targets.to_excel(r'D:\programming\solutions\find_nearest_vsp\2021-04-26\targets.xlsx', index=False)

    vsps['dist'] = ''
    res = vsps[vsps['dist'] != '']
    res['target'] = ''
    res['bank'] = ''
    for i in range(len(targets)):

        vsps['dist'] = vsps.apply(
                lambda x: get_distance_sph(x['pos'], targets['pos'][i]) if not pd.isnull(x['pos']) or x['pos'] != '' else 9999, axis=1
                )

        dist = vsps[
            (vsps['dist'] <= MAX_DIST)
            & (vsps['Формат обслуживания'] != 'VIP')
        ].sort_values(
            ['Бизнес-формат подразделения', 'ЦПО', 'Штат', 'dist'],
            ascending=[True, False, False, True]
        ).head(100)

        # dist = vsps[
        #     (vsps['dist'] <= MAX_DIST)
        #     & (vsps['Формат обслуживания'] != 'VIP')
        #     ].sort_values(
        #     ['Штат'],
        #     ascending=[False]
        # ).head(2)

        dist['target'] = targets['target'][i]
        dist['bank'] = targets['bank'][i]

        res = res.append(dist, ignore_index=True)

    res.drop_duplicates('Полный номер ВСП', inplace=True)

    return res


def main2():
    vsps = pd.read_excel(r'D:\programming\solutions\find_nearest_vsp\New\чек.xlsx')
    vsps['coords'] = vsps['Адрес'].apply(get_geo_coordinates)
    target = 'Москва, пр-т Вернандского, д.87, корп. 2'
    coord_target = get_geo_coordinates(target)
    vsps['dist'] = vsps.apply(
        lambda x: get_distance_sph(x['coords'], coord_target) if not pd.isnull(x['coords']) else 9999, axis=1
    )
    vsps.to_excel(r'D:\programming\solutions\find_nearest_vsp\New\dist_new.xlsx')


if __name__ == '__main__':
    res = main()
    res.to_excel(r'D:\programming\solutions\find_nearest_vsp\2021-04-26\result_20210426.xlsx', index=False)
