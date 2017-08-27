import requests
import access
from methods.emoji import emoji
import json
from datetime import datetime
from time import sleep
import psycopg2
from pandas import DataFrame


token = access.token()
api = access.api()
d_google_maps_api = access.google_maps_api_key()
PSQL_heroku_keys = access.PSQL_heroku_keys()

#создаем подключение к PSQL
conn = psycopg2.connect("dbname='%(dbname)s' port='%(port)s' user='%(user)s' host='%(host)s' password='%(password)s'" % PSQL_heroku_keys)



#текущая метка времени
def now_str():
    now = datetime.now()
    now_str = str(now.year)+str(now.month if now.month >= 10 else  '0'+str(now.month))+str(now.day if now.day >= 10 else  '0'+str(now.hour)) +' '+str(now.hour if now.hour >= 10 else  '0'+str(now.hour)) + str(now.minute if now.minute >= 10 else  '0'+str(now.minute)) + str(now.second if now.second >= 10 else  '0'+str(now.second))
    return now_str


#регистрируем нового пользователя
def new_user(chat_id = None , json_update = None):
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
        created_at = str(now.year)+str(now.month if now.month >= 10 else  '0'+str(now.month))+str(now.day if now.day >= 10 else  '0'+str(now.hour)) +' '+str(now.hour if now.hour >= 10 else  '0'+str(now.hour)) + str(now.minute if now.minute >= 10 else  '0'+str(now.minute)) + str(now.second if now.second >= 10 else  '0'+str(now.second))
        last_message_at = created_at
        cur.execute("INSERT INTO public.user (chat_id,first_name,last_name,created_at,last_message_at)  VALUES (%(chat_id)s, '%(first_name)s','%(last_name)s','%(created_at)s','%(last_message_at)s')" % {'chat_id' : chat_id , 'first_name' : first_name , 'last_name' : last_name , 'created_at' : created_at , 'last_message_at' : last_message_at} )
        conn.commit()
    cur.close()

    return '200'


#последний шаг пользователя
def last_state(chat_id = None , state = None ):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    #получаем время записи
    now = datetime.now()
    message_at = str(now.year)+str(now.month if now.month >= 10 else  '0'+str(now.month))+str(now.day if now.day >= 10 else  '0'+str(now.hour)) +' '+str(now.hour if now.hour >= 10 else  '0'+str(now.hour)) + str(now.minute if now.minute >= 10 else  '0'+str(now.minute)) + str(now.second if now.second >= 10 else  '0'+str(now.second))
    #если запись есть - записываем состояние
    if cur.statusmessage[-3:] != 'T 0':
        #обновляем запись в строчке последнего шага
        cur.execute("UPDATE public.state  SET current_state = '%(state)s' WHERE chat_id  = %(chat_id)s" % {'state' : state, 'chat_id' : chat_id}  )
        conn.commit()
        cur.execute("UPDATE public.user  SET last_message_at = '%(message_at)s' WHERE chat_id  = %(chat_id)s" % {'message_at' : message_at, 'chat_id' : chat_id}  )
        conn.commit()
    #если записи не было - создаем
    elif cur.statusmessage[-3:] == 'T 0':
        #создаем запись в строчке последнего шага
        cur.execute("INSERT INTO public.state (chat_id , current_state)  VALUES (%(chat_id)s, '%(state)s')" % {'chat_id' : chat_id , 'state' : state} )
        conn.commit()
        cur.execute("UPDATE public.user  SET last_message_at = '%(message_at)s' WHERE chat_id  = %(chat_id)s" % {'message_at' : message_at, 'chat_id' : chat_id}  )
        conn.commit()
    cur.close()

    return '200'

#создание кошелька
def make_wallet(chat_id = None  ):
    # создаем запрос
    cur = conn.cursor()
    #достаем информацию по пользователю
    cur.execute("SELECT * from public.user where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    df = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    #если по пользователю нет данных - просьба зарегистрироваться
    if df.shape[0] == 0:
        text = 'Сначала зарегистрируйтесь, иначе я не могу... /start'
        status = 200
    #если есть данные
    else:
        #если уже есть кошелек
        if df['personal_wallet_id'][0] is not None:
            text = 'У Вас уже есть кошелек, хотите его использовать?'
            status = 200
        #если нет кошелька создаем
        else:
            now = now_str()
            cur.execute("INSERT INTO public.wallet (balance,created_at,last_transaction_at) VALUES (0,'%(now_f)s','%(now_s)s')" % {'now_f' : now , 'now_s' : now}  )
            conn.commit()
            cur.execute("SELECT MAX(id) as id from public.wallet")
            df = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
            wallet_id = df['id'][0]
            cur.execute("UPDATE public.user  SET personal_wallet_id = '%(wallet_id)s' WHERE chat_id  = %(chat_id)s" % {'wallet_id' : wallet_id, 'chat_id' : chat_id}  )
            conn.commit()

            text = emoji('банк') + 'Круто, личный кошелек создан! можем его использовать!' + emoji('смайл_спокойствие')
            status = 200

    cur.close()

    reply_markup = {'keyboard': [['/wallet_action']], 'resize_keyboard': True, 'one_time_keyboard': False}
    response = {'status' : status
                ,'text' : text
                ,'reply_markup' : reply_markup
                }

    return response

#запись информация state_info_1
def insert_state_info_1(chat_id = None , state_info_one = None ):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    #получаем время записи
    now = datetime.now()
    message_at = str(now.year)+str(now.month if now.month >= 10 else  '0'+str(now.month))+str(now.day if now.day >= 10 else  '0'+str(now.hour)) +' '+str(now.hour if now.hour >= 10 else  '0'+str(now.hour)) + str(now.minute if now.minute >= 10 else  '0'+str(now.minute)) + str(now.second if now.second >= 10 else  '0'+str(now.second))
    #если запись есть - записываем состояние
    if cur.statusmessage[-3:] != 'T 0':
        #обновляем запись в строчке последнего шага
        cur.execute("UPDATE public.state  SET state_info_1 = '%(state_info_one)s' WHERE chat_id  = %(chat_id)s" % {'state_info_one' : state_info_one, 'chat_id' : chat_id}  )
        conn.commit()
        cur.execute("UPDATE public.user  SET last_message_at = '%(message_at)s' WHERE chat_id  = %(chat_id)s" % {'message_at' : message_at, 'chat_id' : chat_id}  )
        conn.commit()

    cur.close()

    return '200'

#запись информация state_info_1
def current_last_state(chat_id = None ):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT current_state from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )

    df = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    if df.shape[0] != 0:
        last_state = df['id'][0]
        status = 200
    else:
        last_state = 'unknown'
        status = 404

    cur.close()

    response = {'last_state' : last_state
                ,'status' : 
                }


    return response