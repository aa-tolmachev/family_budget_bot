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



#текущая метка времени с минутой часами
def now_str():
    now = datetime.now()
    now_str = str(now.year)+str(now.month if now.month >= 10 else  '0'+str(now.month))+str(now.day if now.day >= 10 else  '0'+str(now.day)) +' '+str(now.hour if now.hour >= 10 else  '0'+str(now.hour)) + str(now.minute if now.minute >= 10 else  '0'+str(now.minute)) + str(now.second if now.second >= 10 else  '0'+str(now.second))
    return now_str

#завтрашная дата без часов минут
def tomorrow_str_func():
    tomorrow = datetime.now()+ timedelta(days=1)
    tomorrow_str = str(tomorrow.year)+str(tomorrow.month if tomorrow.month >= 10 else  '0'+str(tomorrow.month))+str(tomorrow.day if tomorrow.day >= 10 else  '0'+str(tomorrow.day)) 
    return tomorrow_str


#текущая дата без часов минут
def today_str_func():
    today = datetime.now()
    today_str = str(today.year)+str(today.month if today.month >= 10 else  '0'+str(today.month))+str(today.day if today.day >= 10 else  '0'+str(today.day)) 
    return today_str


#основная функция приема с worker_1
def main_woker_1( model = None):
    if model is None:
        return 400
    else:
        #формат ответа
        test_resp = {'status' : 200
                ,'report' : 'tomorrow_expense'
                ,'message' : 'Have reports'
                ,'tomorrow_messages' : [{'user_id' : 13 ,'chat_id' : 111111 ,'message' : 'лалалей'}
                                        , {'user_id' : 14 ,'chat_id' : 111112 ,'message' : 'налевай'}
                                        ]
                }
        #сообщение о завтрашних тратах - направляем на всех пользователей
        if model == 'tomorrow_expense':
            r = tomorrow_expense()
            return r
        #сообщение о задачах на сегодня - направляем на всех пользователей
        elif model == 'today_tasks':
            r = today_tasks()
            return r   


    return 200






#отчет - плановые траты на завтра -  tomorrow_expense
def tomorrow_expense():
    #формируем ответ
    response = {'status' : 200
                ,'report' : 'tomorrow_expense'
                ,'message' : 'No reports'
                ,'tomorrow_messages' : []
                }
    #получаем дату в строке завтрашнего дня
    tomorrow_str = tomorrow_str_func()
    tomorrow_day = int(tomorrow_str[-2:])

    # создаем запрос
    cur = conn.cursor()
    #смотрим, какие данные завтра есть
    cur.execute("SELECT * from public.transaction_plan where date_plan = '%(tomorrow_str)s'" % {'tomorrow_str' : tomorrow_str} )

    #получаем данные
    df_tomorrow_transaction_plan = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #получаем ежемесячные данные
    cur.execute("select * from public.month_transaction_plan where day = %(tomorrow_day)s" % { 'tomorrow_day' : tomorrow_day} )
    df_tomorrow_transaction_month = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #формируем итог
    df_tomorrow_transaction_plan = df_tomorrow_transaction_plan.append(df_tomorrow_transaction_month).reset_index()[:]

    if df_tomorrow_transaction_plan.shape[0] == 0:
        cur.close()
        return response
    else:
        cur.execute("select id , chat_id from public.user" )
        df_user = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        cur.close()

    #подгатавливаем лист завтрашних плановых операций
    tomorrow_messages = []
    #делаем выборку из пользователей, по кому завтра будет операция
    list_tomorrow_user_id = list(df_tomorrow_transaction_plan['user_id'].unique())
    df_tomorrow_user_id = df_user[df_user.id.isin(list_tomorrow_user_id)][:]

    #проходим по ним и заполняем листр завтрашних плановых операций
    for i,row in df_tomorrow_user_id.iterrows():
        #получаем данные пользователя
        user_id = row.id
        chat_id = row.chat_id
        #получаем сообщения по нему
        interest_info = df_tomorrow_transaction_plan[(df_tomorrow_transaction_plan.user_id == user_id)][['transaction_type','transaction_name','summa']][:]
        list_interest_info = list(interest_info.T.to_dict('list').values())
        
        text = 'Привет! Напоминаю, завтра есть запланированные траты: \n\n'
        num = 1
        for transaction_plan in list_interest_info:
            transaction_name = transaction_plan[1]
            summa = int(transaction_plan[2])
            text += str(num) + ': ' + transaction_name + ', Сумма: ' +str(summa)  + ' руб.\n'
            
            num += 1
            
        text += '\nНе забудьте решить эти вопросы, а то мало ли...'
            
        
        
        
        #формируем итоговый словарь по пользователю
        user_dict_tomorrow_messages = {'user_id' : user_id
                                      ,'chat_id' : chat_id
                                      ,'message' : text}
        #добавляем инфо
        tomorrow_messages.append(user_dict_tomorrow_messages)
        

    response['system_message'] = 'Have reports'
    response['user_messages'] = tomorrow_messages


    #реализовать обработку response в app и отправку сообщений пользователям
    return response



#отчет - плановые задачи на сегодня -  today_tasks
def today_tasks():
    #формируем ответ
    response = {'status' : 200
                ,'report' : 'today_tasks'
                ,'message' : 'No reports'
                ,'tomorrow_messages' : []
                }
    #получаем дату в строке завтрашнего дня
    today_str = today_str_func()


    # создаем запрос
    cur = conn.cursor()
    #смотрим, какие данные завтра есть
    cur.execute("SELECT * from public.tasks where date_task = '%(today_str)s'" % {'today_str' : today_str} )

    #получаем данные
    df_today_tasks = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])


    if df_today_tasks.shape[0] == 0:
        cur.close()
        return response
    else:
        cur.execute("select id , chat_id from public.user" )
        df_user = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        cur.close()


    #подгатавливаем лист с сообщениями
    list_messages = []
    #делаем выборку из пользователей, по кому нужно направить ответ
    list_user_id = list(df_today_tasks['user_id'].unique())
    df_user_id = df_user[df_user.id.isin(list_user_id)][:]


    #проходим по ним и заполняем листр завтрашних плановых операций
    for i,row in df_user_id.iterrows():
        #получаем данные пользователя
        user_id = row.id
        chat_id = row.chat_id
        #получаем сообщения по нему
        interest_info = df_today_tasks[(df_today_tasks.user_id == user_id)][['task']][:]
        list_interest_info = list(interest_info.T.to_dict('list').values())
        
        text = 'Сегодня есть запланированные дела: \n\n'
        num = 1
        for task_plan in list_interest_info:
            task_name = task_plan[0]
            text += str(num) + ': ' + task_name + '\n'
            
            num += 1
            
        text += '\n Удачи в сегодняшнем дне, ковбой!'
            
        
        
        
        #формируем итоговый словарь по пользователю
        user_dict_tomorrow_messages = {'user_id' : user_id
                                      ,'chat_id' : chat_id
                                      ,'message' : text}
        #добавляем инфо
        list_messages.append(user_dict_tomorrow_messages)
        

    response['system_message'] = 'Have reports'
    response['user_messages'] = list_messages


    #реализовать обработку response в app и отправку сообщений пользователям
    return response