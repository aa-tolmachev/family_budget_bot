import requests
import access
from methods.emoji import emoji
import json
from datetime import datetime
from datetime import timedelta
from time import sleep
import psycopg2
from pandas import DataFrame
import pandas as pd





token = access.token()
api = access.api()
d_google_maps_api = access.google_maps_api_key()
PSQL_heroku_keys = access.PSQL_heroku_keys()

#создаем подключение к PSQL
conn = psycopg2.connect("dbname='%(dbname)s' port='%(port)s' user='%(user)s' host='%(host)s' password='%(password)s'" % PSQL_heroku_keys)



#текущая метка времени
def now_str():
    now = datetime.now()
    now_str = str(now.year)+str(now.month if now.month >= 10 else  '0'+str(now.month))+str(now.day if now.day >= 10 else  '0'+str(now.day)) +' '+str(now.hour if now.hour >= 10 else  '0'+str(now.hour)) + str(now.minute if now.minute >= 10 else  '0'+str(now.minute)) + str(now.second if now.second >= 10 else  '0'+str(now.second))
    return now_str


#основная функция приема с worker_1
def main_woker_1( model = None):
    if model is None:
        return 400
    else:
        #сообщение о завтрашних тратах
        if model == 'tomorrow_expense':
            r = tomorrow_expense()


    return 200






#отчет - плановые траты на завтра -  tomorrow_expense
def tomorrow_expense():
    #скопировать из test
    x = 1


    return 200



#заглушка
def test( model = None):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.user where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    #если записи не было - создаем
    if cur.statusmessage[-3:] == 'T 0':
        #создаем запись в строчке последнего шага
        cur.execute("INSERT INTO public.state (chat_id , current_state)  VALUES (%(chat_id)s, '/start')" % {'chat_id' : chat_id} )
        conn.commit()

        #регистрируем пользователя
        first_name = json_update['message']['chat']['first_name']
        last_name = json_update['message']['chat']['last_name']
        now = datetime.now()
        created_at = now_str()
        last_message_at = created_at
        cur.execute("INSERT INTO public.user (chat_id,first_name,last_name,created_at,last_message_at)  VALUES (%(chat_id)s, '%(first_name)s','%(last_name)s','%(created_at)s','%(last_message_at)s')" % {'chat_id' : chat_id , 'first_name' : first_name , 'last_name' : last_name , 'created_at' : created_at , 'last_message_at' : last_message_at} )
        conn.commit()
    cur.close()

    return 200