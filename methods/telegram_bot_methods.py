import requests
import access
import json
from datetime import datetime
from time import sleep

token = access.token()
api = access.api()
d_google_maps_api = access.google_maps_api_key()



global last_update_id
last_update_id = 0


#функция сбора всхе обновлений в боте
def get_updates():
    url = api + token + '/getUpdates'
    r = requests.get(url)
    return r.json()


#функция сбора последнего сообщения в боте
def get_message():
    data = get_updates()
    chat_id = data['result'][-1]['message']['chat']['id']
    message_text = data['result'][-1]['message']['text']
    update_id = data['result'][-1]['update_id']

    #засовываем в словарик
    d_message = {'chat_id' : chat_id
                ,'message_text' : message_text
                ,'update_id' : update_id
    }

    return d_message


#функция отправки одного сообщения
def send_message(chat_id = None , text = '/help -> список возможных команд' , reply_markup = None):
    url = api + token + '/sendMessage'
    
    #если не направляем кнопки
    if reply_markup is None:
        params = {'chat_id' : chat_id
                ,'text' : text
        }
    #если хотим отправить кнопки
    else:
        params = {'chat_id' : chat_id
        ,'text' : text
        ,'reply_markup': reply_markup
        }
    r = requests.post(url,
                      json=params)

    send_result = '200'

    return send_result


#функция отправки локации
def send_location(chat_id = None , longitude = None , latitude = None):
    if chat_id is None or longitude is None or latitude is None:
        pass
    else:
        url = api + token + '/sendLocation'
        params = {'chat_id' : chat_id
                ,'latitude' : latitude
                ,'longitude' : longitude
        }
        r = requests.post(url,
                          json=params)

    send_result = '200'
    
    return send_result


