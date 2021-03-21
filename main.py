import sys
from io import BytesIO
from find_spn_param import find_spn
import requests
from PIL import Image, ImageDraw, ImageFont
import math

# Пусть наше приложение предполагает запуск:
# python main.py Москва, улица Тимура Фрунзе, 11к8
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = ",".join([toponym_longitude, toponym_lattitude])
search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    # ...
    pass
# Преобразуем ответ в json-объект
json_response = response.json()
s = ''
for i in range(len(json_response["features"])):
    try:
        chem = json_response["features"][i]["properties"]['CompanyMetaData']['Hours']['text']
        organization = json_response["features"][i]
        point = organization["geometry"]["coordinates"]
        org_point = "{0},{1}".format(point[0], point[1])
        if 'круглосуточно' in chem:
            s += "~{0},pm2dgm".format(org_point)
        else:
            s += "~{0},pm2dbm".format(org_point)
    except Exception:
        s += "~{0},pm2grm".format(org_point)

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    "l": "map",
    'pt': ",".join([toponym_longitude, toponym_lattitude]) + ',ya_ru~' + s[1:]
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

im = Image.open(BytesIO(
    response.content)).convert('RGB')
im.show()