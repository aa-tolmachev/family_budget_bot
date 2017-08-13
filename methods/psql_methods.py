import requests
import access
import json
from datetime import datetime
from time import sleep
import psycopg2


token = access.token()
api = access.api()
d_google_maps_api = access.google_maps_api_key()
PSQL_heroku_keys = access.PSQL_heroku_keys()

#создаем подключение к PSQL
conn = psycopg2.connect("dbname='%(dbname)s' port='%(port)s' user='%(user)s' host='%(host)s' password='%(password)s'" % PSQL_heroku_keys)





#регистрируем нового пользователя
def new_user(chat_id = None):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    #если записи не было - создаем
    if cur.statusmessage[-3:] == 'T 0':
        #создаем запись в строчке последнего шага
        cur.execute("INSERT INTO public.state  VALUES (%(chat_id)s, '/start')" % {'chat_id' : chat_id} )
        conn.commit()
    cur.close()

    return '200'


#регистрируем нового пользователя
def last_state(chat_id = None , state = None):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    #если запись есть - записываем состояние
    if cur.statusmessage[-3:] == 'T 1':
        #обновляем запись в строчке последнего шага
        cur.execute("UPDATE public.state  SET current_state = '%(state)s' WHERE chat_id  = %(chat_id)s" % {'state' : state, 'chat_id' : chat_id}  )
        conn.commit()
    #если записи не было - создаем
    elif cur.statusmessage[-3:] == 'T 0':
        #создаем запись в строчке последнего шага
        cur.execute("INSERT INTO public.state  VALUES (%(chat_id)s, '%(state)s')" % {'chat_id' : chat_id , 'state' : state} )
        conn.commit()
    cur.close()

    return '200'

  