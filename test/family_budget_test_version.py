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
def send_message(chat_id = None , text = '/help -> список возможных команд'):
    url = api + token + '/sendMessage'
    params = {'chat_id' : chat_id
            ,'text' : text
    }
    r = requests.post(url,
                      json=params)


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










#основная функция
def main():
    
    #указываем текущую дату время для записи обновлений в лог файл
    s_now = str(datetime.isoformat(datetime.today()))
    s_now = s_now.replace('.',':')
    s_now = s_now.replace(':','-')
    #определяем путь файла
    path = 'updates/' + s_now + '.json' 

    
    #собираем все обновления
    d_updates = get_updates()

    #создаем файл для записи и записываем
    #with open(path , 'w') as free_file:
    #    json.dump(d_updates , free_file , indent = 2 , ensure_ascii=False )

    d_message = get_message()
    
    chat_id = d_message['chat_id']
    message_text = d_message['message_text']
    update_id = d_message['update_id']

    global last_update_id

    if update_id != last_update_id:
        if message_text == '/help':
            text = '/loc'
        else:
            text = '/help -> список возможных команд'

        send_message(chat_id = chat_id , text = text)


        
        d_looked_geo = google_maps_geo_find(address = 'пермь аркадия гайдара 8б' , d_google_maps_api = d_google_maps_api)

        if d_looked_geo['status'] == 'OK':
            lat = d_looked_geo['geo_info']['lat']
            lng = d_looked_geo['geo_info']['lng']
            send_location(chat_id = chat_id , longitude = lng , latitude = lat)



        last_update_id = update_id

        







    

#запускаем выполнение основной функции
#if __name__ == '__main__':
#    main()