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



#todo - переделать не на одного меня а массово на всех пользователей
#отчет дела за прошлый месяц как сделаны
def prev_month_complete_tasks():
    user_id = 13
    command = 'На текущий месяц'
    command = ''
    #формат ответа
    response = {'status' : 200
                ,'report' : 'delete_transaction_plan'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }


    # создаем запрос
    cur = conn.cursor()
    if command == 'На сегодня':
        cur.execute("select * from public.tasks where  user_id = %(user_id)s and date_task >= date_trunc('day', now()) and date_task < date_trunc('day', now()) +  interval '1 day'" % {  'user_id' : user_id} )
    elif command == 'На текущую неделю':
        cur.execute("select * from public.tasks where  user_id = %(user_id)s and date_task >= date_trunc('week', now()) and date_task < date_trunc('week', now()) + interval '7 day'" % {  'user_id' : user_id} )
    elif command == 'На текущий месяц':
        cur.execute("select * from public.tasks where  user_id = %(user_id)s and date_task >= date_trunc('month', now()) and date_task < date_trunc('month', now()) + interval '1 month'" % {  'user_id' : user_id} )
    else:
        cur.execute("select * from public.tasks where  user_id = %(user_id)s " % {  'user_id' : user_id} )


    df_plan_tasks = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description]).sort_values(by='date_task' , ascending=True)

    cur.close() 

    if df_plan_tasks.shape[0] == 0:
        response['text'] = command + ' дел нет.'
    else:
        text = command + ' следующие дела:\n\n'
        num = 1
        for row in df_plan_tasks.iterrows():
            text += str(num) + ': ' + row[1]['task'] + ' ' + row[1]['date_task'].strftime('%d.%m.%Y') + '\n'
            num += 1
            
            
        response['text'] = text


    text = command + ' следующие дела:\n\n'
    num = 1
    for row in df_plan_tasks.iterrows():
        text += str(num) + ': ' + row[1]['task'] + ' ' + row[1]['date_task'].strftime('%d.%m.%Y') + '\n'

        num += 1




    df_plan_tasks['YearMonth'] = pd.to_datetime(df_plan_tasks['date_task']).map(lambda dt: dt.replace(day=1))

    res = df_plan_tasks.groupby(['YearMonth'])['id'].count()
    res_6 = res.sort_index(ascending = False).head(6).sort_index(ascending = True)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')

    month_dict= {1:'Январь',
                2:'Февраль',
                3:'Март',
                4:'Апрель',
                5:'Май',
                6:'Июнь',
                7:'Июль',
                8:'Август',
                9:'Сентябрь',
                10:'Октябрь',
                11:'Ноябрь',
                12:'Декабрь'}


    res_6.index = [month_dict[x.month] for x in list(res_6.index)]


    from dateutil.relativedelta import relativedelta
    now_date = datetime.now()
    next_date = datetime.now()+ relativedelta(months=1)
    prev_date = datetime.now()- relativedelta(months=1)


    now_year = now_date.year
    now_month = now_date.month

    prev_year = prev_date.year
    prev_month = prev_date.month

    datetime(now_year, now_month , 1).isocalendar()[1]



    df_prev_month = df_plan_tasks[(df_plan_tasks['date_task'] >= datetime(prev_year, prev_month , 1))
                 & (df_plan_tasks['date_task'] < datetime(now_year, now_month , 1))][:]

    df_prev_month['n_week'] = [int(x.day / 7) + 1 for x in df_prev_month['date_task']]

    res = df_prev_month.groupby(['n_week'])['id'].count()


    cnt_missions = res.values
    name_bars = list(res.index)
    y_pos = np.arange(len(name_bars))


    plt.bar(y_pos, cnt_missions, color = (0.2, 0.9, 0.7, 0.8) ,  edgecolor='gray')



    plt.xlabel('неделя')
    plt.ylabel('выполнено дел')


    plt.ylim(0,50)


    plt.xticks(y_pos, name_bars)

    for a,b in zip(y_pos, cnt_missions): 
        plt.text(a - 0.1, b + 1, str(b) , fontsize=11 , color = 'darkgreen')


    plt.savefig('to1.png' ,facecolor='w', edgecolor='w')

    x = open('to1.png', 'rb')

    return x