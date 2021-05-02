import requests
import bs4
import re
import time


headers = {
    'authority': 'www.avito.ru',
    'method': 'GET',
    # 'path': '/nizhniy_novgorod/produkty_pitaniya?localPriority=0&q=%D1%87%D0%B0%D0%B9',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'referer': 'https://google.com/',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0',
}

avito_category = [
    'produkty_pitaniya',
    'odezhda_obuv_aksessuary',
]

avito_regions = [
    'rossiya',
]

avito_urls = {
    'main': 'https://www.avito.ru/',
    'all_categoryes': 'https://www.avito.ru/rossiya?cd=1&q={}',
}

find_text = 'войлок'

session = requests.session()
session.headers = headers

response = session.get("https://www.avito.ru/")
time.sleep(2)

response = session.get('https://www.avito.ru/rossiya?cd=1&q={}'.format(find_text))

soup = bs4.BeautifulSoup(response.text, 'html.parser')

last_page = int(
    soup.find('div', attrs={'data-marker': 'pagination-button'}).
        find_all(attrs={'data-marker': re.compile('page.+')})[6].text
)

find_prods = []
current_page = 1

f = open('finds.csv', 'w', encoding='utf-8')
f.write('href;title;price;geo\n')

while True:
    products = soup.find('div', attrs={'data-marker': 'catalog-serp'})
    for prod in products.find_all('div', attrs={'data-marker': 'item'}):
        a_href = prod.find('a', attrs={'data-marker': 'item-title'}) or {}
        price = prod.find('meta', attrs={'itemprop': 'price'}) or {}
        geo = prod.find(attrs={'class': re.compile('geo-root.+')}) or ''
        line = prod.find(attrs={})
        if geo:
            geo = geo.span.span.text
        _ = {
            'href': a_href.get('href'),
            'title': a_href.get('title'),
            'price': price.get('content'),
            'geo': geo,
        }
        f.write('"{}";"{}";"{}";"{}"\n'.format(*_.values()))
        find_prods.append(_)
        print(len(find_prods), '-', _['title'])

    current_page += 1
    if current_page > last_page:
        break

    time.sleep(2)
    response = session.get(r'https://www.avito.ru/rossiya?cd=1&p={}&q={}'.format(str(current_page), find_text))
    if response.status_code != 200:
        print('Ups')
        break
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

f.close()
