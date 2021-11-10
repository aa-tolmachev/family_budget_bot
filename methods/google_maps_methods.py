import requests
from methods import access
import json
from datetime import datetime
from time import sleep

token = access.token()
api = access.api()
d_google_maps_api = access.google_maps_api_key()



global last_update_id
last_update_id = 0


#функция нахождения гео адреса
def google_maps_geo_find(address = None , d_google_maps_api = None):
    url = d_google_maps_api['api']
    key = d_google_maps_api['google_maps_api_key']

    list_address = address.split(' ')

    address_request = ''
    for element in list_address:
        address_request = address_request + element + '+'
    address_request = address_request[:-1]

    url = url + 'address=' + address_request + '&key=' + key

    r = requests.get(url)

    d_geo_info = r.json()

    d_looked_geo = {'status' : 'bad request'
                    ,'geo_info' : None}
    if d_geo_info['status'] == 'OK':
        geo_info = d_geo_info['results'][0]['geometry']['location']
        d_looked_geo['status'] = 'OK'
        d_looked_geo['geo_info'] = geo_info


    return d_looked_geo


