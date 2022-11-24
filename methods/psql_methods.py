import requests
from methods import access
from methods.emoji import emoji
import json
from datetime import datetime
from datetime import timedelta
from time import sleep
import psycopg2
from pandas import DataFrame
import pandas as pd
import numpy as np
import re

from dicts import meta_info

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

        #собираем данные от телеграмма
        if 'first_name' in json_update['message']['chat']:
            first_name = json_update['message']['chat']['first_name']
        else:
            first_name = None
            
        if 'last_name' in json_update['message']['chat']:
            last_name = json_update['message']['chat']['last_name']
        else:
            last_name = None

        if 'username' in json_update['message']['chat']:
            telegram_username = json_update['message']['chat']['username']
        else:
            telegram_username = None
        
        #регистрируем пользователя
        now = datetime.now()
        created_at = now_str()
        last_message_at = created_at
        cur.execute("INSERT INTO public.user (chat_id,first_name,last_name,created_at,last_message_at,telegram_username)  VALUES (%(chat_id)s, '%(first_name)s','%(last_name)s','%(created_at)s','%(last_message_at)s', '%(telegram_username)s')" % {'chat_id' : chat_id , 'first_name' : first_name , 'last_name' : last_name , 'created_at' : created_at , 'last_message_at' : last_message_at, 'telegram_username' : telegram_username} )
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
    message_at = now_str()
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
        reply_markup = {'keyboard': [['/start']], 'resize_keyboard': True, 'one_time_keyboard': False}

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

            text = emoji('банк') + 'Круто, личный кошелек создан! можем начинать!' + emoji('смайл_спокойствие') + '\n'
            text += 'для описания функций можешь использовать помощь -> /help'
            status = 200

        reply_markup = {'keyboard': [['/wallet_action']], 'resize_keyboard': True, 'one_time_keyboard': False}

    cur.close()

    
    response = {'status' : status
                ,'text' : text
                ,'reply_markup' : reply_markup
                }

    return response

#запись информация state_info_1
def insert_state_info(chat_id = None , state_info = None , state_id = None):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    #получаем время записи
    now = datetime.now()
    message_at = now_str()
    #если запись есть - записываем состояние
    if cur.statusmessage[-3:] != 'T 0':
        #обновляем запись в строчке последнего шага
        if state_id is None or state_id == 1:
            cur.execute("UPDATE public.state  SET state_info_1 = '%(state_info)s' WHERE chat_id  = %(chat_id)s" % {'state_info' : state_info, 'chat_id' : chat_id}  )
            conn.commit()
        elif state_id == 2:
            cur.execute("UPDATE public.state  SET state_info_2 = '%(state_info)s' WHERE chat_id  = %(chat_id)s" % {'state_info' : state_info, 'chat_id' : chat_id}  )
            conn.commit()
        elif state_id == 3:
            cur.execute("UPDATE public.state  SET state_info_3 = '%(state_info)s' WHERE chat_id  = %(chat_id)s" % {'state_info' : state_info, 'chat_id' : chat_id}  )
            conn.commit()
        elif state_id == 4:
            cur.execute("UPDATE public.state  SET state_info_4 = '%(state_info)s' WHERE chat_id  = %(chat_id)s" % {'state_info' : state_info, 'chat_id' : chat_id}  )
            conn.commit()
        elif state_id == 5:
            cur.execute("UPDATE public.state  SET state_info_5 = '%(state_info)s' WHERE chat_id  = %(chat_id)s" % {'state_info' : state_info, 'chat_id' : chat_id}  )
            conn.commit()
        cur.execute("UPDATE public.user  SET last_message_at = '%(message_at)s' WHERE chat_id  = %(chat_id)s" % {'message_at' : message_at, 'chat_id' : chat_id}  )
        conn.commit()

    cur.close()

    return '200'


def add_transaction_fact(chat_id = None , summa = None , dict_user_data = None):
    #проверяем корректность данных
    if 'float' not in str(type(summa)):
        return 400
    else:
        state_info_1 = dict_user_data['state_info_1']
        user_id = dict_user_data['user_id']
        personal_wallet_id = dict_user_data['personal_wallet_id']
        # создаем запрос
        cur = conn.cursor()
        #получаем время записи
        now = now_str()
        cur.execute("INSERT INTO public.transaction_fact (user_id,wallet_id,transaction_type,summa,date_fact) VALUES (%(user_id)s,%(wallet_id)s,'%(transaction_type)s' , %(summa)s , '%(date_fact)s')" % {'user_id' : user_id , 'wallet_id' : personal_wallet_id , 'transaction_type' : state_info_1 , 'summa' : summa , 'date_fact' : now}  )
        conn.commit()
        cur.close()

        return 200




def add_transaction_plan(chat_id = None , summa = None , dict_user_data = None):
    #получаем данные из справочника
    once_name = dict_user_data['state_info_1']
    plan_name = dict_user_data['state_info_2']
    plan_date = dict_user_data['state_info_3']
    plan_type = dict_user_data['state_info_4']
    user_id = dict_user_data['user_id']
    personal_wallet_id = dict_user_data['personal_wallet_id']

    #проверяем наличие данных
    for state_info in [once_name , plan_name , plan_date , plan_type , user_id ,personal_wallet_id ]:
        if state_info is None:
            return 400
    #проверяем корректность данных
    if 'float' not in str(type(summa)):
        return 400
    else:
        # создаем запрос
        cur = conn.cursor()
        #получаем время записи
        cur.execute("INSERT INTO public.transaction_plan (user_id,wallet_id,transaction_type,transaction_name,summa,date_plan,flg_done) VALUES (%(user_id)s,%(wallet_id)s,'%(transaction_type)s','%(transaction_name)s' , %(summa)s , '%(date_plan)s' , False)" % {'user_id' : user_id , 'wallet_id' : personal_wallet_id , 'transaction_type' : plan_type , 'transaction_name' : plan_name , 'summa' : summa , 'date_plan' : plan_date}  )
        conn.commit()
        cur.close()

        return 200

def add_transaction_plan_month(chat_id = None , summa = None , dict_user_data = None):
    #получаем данные из справочника
    once_name = dict_user_data['state_info_1']
    plan_name = dict_user_data['state_info_2']
    plan_day = dict_user_data['state_info_3']
    plan_type = dict_user_data['state_info_4']
    user_id = dict_user_data['user_id']
    personal_wallet_id = dict_user_data['personal_wallet_id']

    #проверяем наличие данных
    for state_info in [once_name , plan_name , plan_day , plan_type , user_id ,personal_wallet_id ]:
        if state_info is None:
            return 400
    #проверяем корректность данных
    if 'float' not in str(type(summa)):
        return 400
    else:
        # создаем запрос
        cur = conn.cursor()
        #получаем время записи
        cur.execute("INSERT INTO public.month_transaction_plan (user_id,wallet_id,day,transaction_name,transaction_type,summa) VALUES (%(user_id)s,%(wallet_id)s, %(plan_day)s,'%(transaction_name)s','%(transaction_type)s' , %(summa)s  )" % {'user_id' : user_id , 'wallet_id' : personal_wallet_id , 'transaction_type' : plan_type , 'transaction_name' : plan_name , 'summa' : summa , 'plan_day' : plan_day}  )
        conn.commit()
        cur.close()

        return 200



def clear_state(chat_id = None ):


    # создаем запрос
    cur = conn.cursor()
    cur.execute("update public.state set state_info_1 = null , state_info_2 = null , state_info_3 = null , state_info_4 = null , state_info_5 = null where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )
    conn.commit()
    cur.close()

    return 200




#получение всей информации по пользователю
def user_data(chat_id = None ):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT current_state , state_info_1 , state_info_2 , state_info_3 , state_info_4 , state_info_5 from public.state where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )

    df = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    cur.execute("SELECT id , personal_wallet_id from public.user where chat_id = %(chat_id)s" % {'chat_id' : chat_id} )

    df_user = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])



    if df.shape[0] != 0:
        last_state = df['current_state'][0]
        state_info_1 = df['state_info_1'][0]
        state_info_2 = df['state_info_2'][0]
        state_info_3 = df['state_info_3'][0]
        state_info_4 = df['state_info_4'][0]
        state_info_5 = df['state_info_5'][0]
        user_id = df_user['id'][0]
        personal_wallet_id = df_user['personal_wallet_id'][0]
        status = 200
    else:
        last_state = 'unknown'
        state_info_1 = 'unknown'
        state_info_2 = 'unknown'
        state_info_3 = 'unknown'
        state_info_4 = 'unknown'
        state_info_5 = 'unknown'
        user_id = 'unknown'
        personal_wallet_id = 'unknown'
        status = 404

    cur.close()

    response = {'last_state' : last_state
                ,'state_info_1' : state_info_1
                ,'state_info_2' : state_info_2
                ,'state_info_3' : state_info_3
                ,'state_info_4' : state_info_4
                ,'state_info_5' : state_info_5
                ,'user_id' : user_id
                ,'personal_wallet_id' : personal_wallet_id
                ,'status' : status
                }


    return response

#отчет о тратах в предыдущем месяце
def report_prev_expense(chat_id = None , user_id = None):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.transaction_fact where user_id = %(user_id)s" % {'user_id' : user_id} )

    df = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    cur.close()

    #Если данные за предыдущий месяц найдены
    if df.shape[0] != 0: 

        #получаем необходимые даты
        cur_year = datetime.now().year
        cur_month = datetime.now().month

        prev_year = cur_year if cur_month > 1 else cur_year -1
        prev_month = cur_month - 1 if cur_month > 1 else 12

        next_year = cur_year if cur_month < 12 else cur_year + 1
        next_month = cur_month + 1 if cur_month < 12 else 1

        #получаем df за текущий и предыдущий месяцы
        df_cur_month_expense = df[(df.date_fact >= pd.datetime(cur_year,cur_month,1)) & (df.date_fact < pd.datetime(next_year,next_month,1))][:] 
        df_prev_month_expense = df[(df.date_fact >= pd.datetime(prev_year,prev_month,1)) & (df.date_fact < pd.datetime(cur_year,cur_month,1))][:] 

        #отсортированные и сгрупированные траты в текущем и предыдущем месяце
        df_cur_month_expense_group = DataFrame(data = df_cur_month_expense.groupby(['transaction_type'])['summa'].sum() ).sort_values(by='summa' , ascending=False)
        df_prev_month_expense_group = DataFrame(data = df_prev_month_expense.groupby(['transaction_type'])['summa'].sum() ).sort_values(by='summa' , ascending=False)


        #заводм справочник популярных трат
        type_expand = ([])
        for row in df_prev_month_expense_group.iterrows():
            k  = 1
            type_expand.append(row[0])

        sum_expand = df_prev_month_expense_group.values.astype(float)
        all_sum = df_prev_month_expense_group['summa'].values.astype(float).sum()
           
        text = 'Ваши траты в прошлом месяце: \n' 
        for type , sum in zip(type_expand , sum_expand):
            text += type + ': ' + str(int(round(sum[0],0)))  + ' руб.\n'
            
        text += '\nИтого на сумму ' + str(int(round(all_sum,0))) + ' руб.\n'

    else:

        text = 'За прошлый месяц трат не найдено...' 


    response = {'text' : text
                ,'status' : 200
                }


    return response


#отчет о тратах в текущем месяце
def report_cur_expense(chat_id = None , user_id = None):
    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.transaction_fact where user_id = %(user_id)s" % {'user_id' : user_id} )

    df = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    cur.close()

    #Если данные за предыдущий месяц найдены
    if df.shape[0] != 0: 
        #получаем необходимые даты
        cur_year = datetime.now().year
        cur_month = datetime.now().month

        prev_year = cur_year if cur_month > 1 else cur_year -1
        prev_month = cur_month - 1 if cur_month > 1 else 12

        next_year = cur_year if cur_month < 12 else cur_year + 1
        next_month = cur_month + 1 if cur_month < 12 else 1

        #получаем df за текущий и предыдущий месяцы
        df_cur_month_expense = df[(df.date_fact >= pd.datetime(cur_year,cur_month,1)) & (df.date_fact < pd.datetime(next_year,next_month,1))][:] 
        df_all_prev_month_expense = df[(df.date_fact < pd.datetime(cur_year,cur_month,1))][:] 

        #средние траты за все время по месяцам
        df_all_prev_month_expense_group = DataFrame(data = df_all_prev_month_expense.groupby(['transaction_type'])['summa'].sum() ).sort_values(by='summa' , ascending=False)

        df_all_prev_month_expense['year'] = df_all_prev_month_expense['date_fact'].dt.year
        df_all_prev_month_expense['month'] = df_all_prev_month_expense['date_fact'].dt.month
        df_all_prev_month_expense['yearmonth'] = df_all_prev_month_expense['year'].astype(str) +  df_all_prev_month_expense['month'].astype(str)

        df_all_prev_month_expense_group = DataFrame(df_all_prev_month_expense.groupby(['transaction_type' , 'yearmonth'])['summa'].sum() ).reset_index()
        df_all_prev_month_expense_group['summa'] = df_all_prev_month_expense_group['summa'].astype(float)
        if df_all_prev_month_expense_group.shape[0] == 0:
            df_all_prev_month_expense_group['transaction_type'] = None
        df_mean_expense = DataFrame(df_all_prev_month_expense_group.groupby(['transaction_type'])['summa'].mean()).reset_index()

        
        #отсортированные и сгрупированные траты в текущем и предыдущем месяце
        df_cur_month_expense_group = DataFrame(data = df_cur_month_expense.groupby(['transaction_type'])['summa'].sum() ).sort_values(by='summa' , ascending=False)


        #заводм справочник популярных трат
        type_expand = ([])
        for row in df_cur_month_expense_group.iterrows():
            k  = 1
            type_expand.append(row[0])

        #суммы трат
        sum_expand = df_cur_month_expense_group.values.astype(float)
        all_sum = df_cur_month_expense_group['summa'].values.astype(float).sum()

        text = 'Ваши траты в текущем месяце: \n' 
        for type , sum in zip(type_expand , sum_expand):
            if df_mean_expense[(df_mean_expense.transaction_type == type)].shape[0] == 0:
                mean_change = ''
            else:
                change = sum / df_mean_expense[(df_mean_expense.transaction_type == type)]['summa'].values[0]

                sign = 'less' if change < 1. else 'more'
                emoji_sign = emoji(sign) if sign == 'more' else emoji(sign) + 'меньше'
                str_change_vlue = str(int( (1. - change if sign == 'less' else change - 1.) * 100 ))
                mean_change = '(' + emoji_sign + ' на ' + str_change_vlue + '% ' + ')'
                #если str_change_vlue = 0, Зануляем
                mean_change = '' if str_change_vlue == '0' else mean_change
            
            text += type + ': ' + str(int(round(sum[0],0)))  + ' руб.' + mean_change + '\n'

        #разница в среднем
        mean_sum = df_mean_expense['summa'].values.sum()
        mean_sign = 'less' if mean_sum > all_sum else 'more'
        emoji_sign = emoji(mean_sign) if mean_sign == 'more' else emoji(mean_sign) + 'меньше'
        change_mean = all_sum - mean_sum if mean_sign == 'more' else mean_sum - all_sum
        text += '\nИтого на сумму ' + str(int(round(all_sum,0))) + ' руб.' + ' (' + emoji_sign + ' на ' + str(int(change_mean)) + ') ' + '\n'

    else:
        text = 'За текущий месяц трат не найдено...'


    response = {'text' : text
                ,'status' : 200
                }


    return response

#Список плановых трат
def list_transaction_plan(chat_id = None  , user_id = None ):
    
    #формат ответа
    response = {'status' : 200
                ,'report' : 'transaction_plan'
                ,'system_message' : 'No report'
                ,'text' : 'NaN'
                ,'reply_markup' : 'NaN'
                }

    # создаем запрос
    cur = conn.cursor()

    now_strin = now_str()[:8]
    now_day = int(now_strin[-2:])
    now_month = int(now_strin[4:6])

    #смотрим, какие данные завтра есть
    cur.execute("SELECT * from public.transaction_plan where date_plan >= '%(now_strin)s' and Extract(month from date_plan) = %(now_month)s and user_id = %(user_id)s" % {'now_strin' : now_strin , 'user_id' : user_id , 'now_month' : now_month} )

    #получаем данные
    df_transaction_plan = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #получаем ежемесячные данные
    cur.execute("select * from public.month_transaction_plan where day >= %(now_day)s and user_id = %(user_id)s" % { 'now_day' : now_day , 'user_id' : user_id} )
    df_transaction_month = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #формируем итог
    df_transaction_plan = df_transaction_plan.append(df_transaction_month)

    #если ничего нет - возвращаем ответ
    if df_transaction_plan.shape[0] == 0:
        cur.close()
        return response
    else:
        cur.close()
        
    #достаем дни из разовых трат    
    if df_transaction_plan['date_plan'].dtypes != 'O':
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan'].dt.day
    else:
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan']

    #формируем единую метку дней
    day = []
    for day1 , day2 in zip (df_transaction_plan['day'].values , df_transaction_plan['day_month'].values):
        if np.isnan(day1):
            day.append(int(day2))
        else:
            day.append(int(day1))
            
    df_transaction_plan['day'] = day   


    df_transaction_plan.sort_values(by = ['day'] , inplace = True , ascending = True)

    df_transaction_plan.reset_index(inplace = True)

    df_transaction_plan.drop(labels = 'index' , axis = 1 , inplace = True)

    month_names = {1 : 'январь'
                  ,2 : 'февраль'
                  ,3 : 'март'
                  ,4 : 'апрель'
                  ,5 : 'май'
                  ,6 : 'июнь'
                  ,7 : 'июль'
                  ,8 : 'август'
                  ,9 : 'сентябрь'
                  ,10 : 'октябрь'
                  ,11 : 'ноябрь'
                  ,12 : 'декабрь'}

    text = 'Вот список запланированных трат на %(month_name)s:\n\n' % {'month_name' : month_names[now_month]}

    #формируем список
    for i,row in df_transaction_plan.iterrows():
        num = str(i+1)
        day = str(row['day'])
        transaction_name = str(row['transaction_name'])
        transaction_summa = str(int(row['summa']))
        text += num + ': ' + day + ' числа, ' + transaction_name + ', ' + transaction_summa + ' руб.\n'
        
        
    text += '\nЧто-то нужно сделать, Владыка?'
    reply_markup = {'keyboard': [['Изменить','Удалить'],['Добавить','меню']], 'resize_keyboard': True, 'one_time_keyboard': False}
    system_message = 'Have reports' 

    response['text'] = text
    response['reply_markup'] = reply_markup
    response['system_message'] = system_message

    return response




#Удаление плановой операции
def delete_transaction_plan(chat_id = None  , user_id = None , delete_num = None):
    
    #формат ответа
    response = {'status' : 200
                ,'report' : 'delete_transaction_plan'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }

    # создаем запрос
    cur = conn.cursor()

    now_strin = now_str()[:8]
    now_day = int(now_strin[-2:])
    now_month = int(now_strin[4:6])

    #смотрим, какие данные завтра есть
    cur.execute("SELECT * from public.transaction_plan where date_plan >= '%(now_strin)s' and Extract(month from date_plan) = %(now_month)s and user_id = %(user_id)s" % {'now_strin' : now_strin , 'user_id' : user_id , 'now_month' : now_month} )

    #получаем данные
    df_transaction_plan = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #получаем ежемесячные данные
    cur.execute("select * from public.month_transaction_plan where day >= %(now_day)s and user_id = %(user_id)s" % { 'now_day' : now_day , 'user_id' : user_id} )
    df_transaction_month = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #формируем итог
    df_transaction_plan = df_transaction_plan.append(df_transaction_month)

    #если ничего нет - возвращаем ответ
    if df_transaction_plan.shape[0] == 0:
        cur.close()
        return response
    else:
        cur.close()
        
    #достаем дни из разовых трат    
    if df_transaction_plan['date_plan'].dtypes != 'O':
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan'].dt.day
    else:
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan']

    #формируем единую метку дней
    day = []
    for day1 , day2 in zip (df_transaction_plan['day'].values , df_transaction_plan['day_month'].values):
        if np.isnan(day1):
            day.append(int(day2))
        else:
            day.append(int(day1))
            
    df_transaction_plan['day'] = day   


    df_transaction_plan.sort_values(by = ['day'] , inplace = True , ascending = True)

    df_transaction_plan.reset_index(inplace = True)

    df_transaction_plan.drop(labels = 'index' , axis = 1 , inplace = True)

    #выбираем нужный элемент
    if df_transaction_plan.shape[0] >= delete_num:
        dict_delete_plan = df_transaction_plan.iloc[delete_num-1]
        #если ежемесячная - удаляем ее, иначе разовую
        cur = conn.cursor()
        id_delete = dict_delete_plan['id']
        if np.isnan(dict_delete_plan['day_month']):
            cur.execute("delete from public.month_transaction_plan where id = %(id_delete)s" % {'id_delete' : id_delete} )
            conn.commit()
        else:
            cur.execute("delete from public.transaction_plan where id = %(id_delete)s" % {'id_delete' : id_delete} )
            conn.commit()
            
        cur.close()
        
        text = 'Плановая операция удалена сир!'
        reply_markup = None
            
        
    else:
        text = 'Легче ковбой, введи существующий номер операции'
        reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}

    response['text'] = text
    response['reply_markup'] = reply_markup

    return response




#Изменение даты плановой операции 1
def change_transaction_plan_1(chat_id = None  , user_id = None , change_num = None):
    #формат ответа
    response = {'status' : 200
                ,'report' : 'change_transaction_plan'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }

    # создаем запрос
    cur = conn.cursor()

    now_strin = now_str()[:8]
    now_day = int(now_strin[-2:])
    now_month = int(now_strin[4:6])

    #смотрим, какие данные завтра есть
    cur.execute("SELECT * from public.transaction_plan where date_plan >= '%(now_strin)s' and Extract(month from date_plan) = %(now_month)s and user_id = %(user_id)s" % {'now_strin' : now_strin , 'user_id' : user_id , 'now_month' : now_month} )

    #получаем данные
    df_transaction_plan = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #получаем ежемесячные данные
    cur.execute("select * from public.month_transaction_plan where day >= %(now_day)s and user_id = %(user_id)s" % { 'now_day' : now_day , 'user_id' : user_id} )
    df_transaction_month = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #формируем итог
    df_transaction_plan = df_transaction_plan.append(df_transaction_month)

    #если ничего нет - возвращаем ответ
    if df_transaction_plan.shape[0] == 0:
        cur.close()
        return response
    else:
        cur.close()

    #достаем дни из разовых трат    
    if df_transaction_plan['date_plan'].dtypes != 'O':
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan'].dt.day
    else:
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan']

    #формируем единую метку дней
    day = []
    for day1 , day2 in zip (df_transaction_plan['day'].values , df_transaction_plan['day_month'].values):
        if np.isnan(day1):
            day.append(int(day2))
        else:
            day.append(int(day1))

    df_transaction_plan['day'] = day   


    df_transaction_plan.sort_values(by = ['day'] , inplace = True , ascending = True)

    df_transaction_plan.reset_index(inplace = True)

    df_transaction_plan.drop(labels = 'index' , axis = 1 , inplace = True)

    #выбираем нужный элемент
    if df_transaction_plan.shape[0] >= change_num:
        dict_change_plan = df_transaction_plan.iloc[change_num-1]
        if np.isnan(dict_change_plan['day_month']):
            text = 'Так так, посмотрим. Эта ежемесячная операция, укажите, в какой день напоминать от 1 до 28'
            reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            response['system_message'] = 'monthly'
        else:
            text = 'Хм, разовая операция, на какую дату перенести? В формате -> 22.03.1990'
            reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True} 
            response['system_message'] = 'once'
            
    else:
        text = 'А у тебя не очень хорошо с целыми числами... Введи существующий номер операции'
        reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        
        

    response['text'] = text
    response['reply_markup'] = reply_markup

    return response


#Изменение даты плановой операции 2
def change_transaction_plan_2(chat_id = None  , user_id = None , change_num = None , type = None , date_plan = None):
    change_num = int(change_num)

    #формат ответа
    response = {'status' : 200
                ,'report' : 'change_transaction_plan'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }

    # создаем запрос
    cur = conn.cursor()

    now_strin = now_str()[:8]
    now_day = int(now_strin[-2:])
    now_month = int(now_strin[4:6])

    #смотрим, какие данные завтра есть
    cur.execute("SELECT * from public.transaction_plan where date_plan >= '%(now_strin)s' and Extract(month from date_plan) = %(now_month)s and user_id = %(user_id)s" % {'now_strin' : now_strin , 'user_id' : user_id , 'now_month' : now_month} )

    #получаем данные
    df_transaction_plan = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #получаем ежемесячные данные
    cur.execute("select * from public.month_transaction_plan where day >= %(now_day)s and user_id = %(user_id)s" % { 'now_day' : now_day , 'user_id' : user_id} )
    df_transaction_month = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    #формируем итог
    df_transaction_plan = df_transaction_plan.append(df_transaction_month)

    #если ничего нет - возвращаем ответ
    if df_transaction_plan.shape[0] == 0:
        cur.close()
        return response
    else:
        cur.close()

    #достаем дни из разовых трат    
    if df_transaction_plan['date_plan'].dtypes != 'O':
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan'].dt.day
    else:
        df_transaction_plan['day_month'] = df_transaction_plan['date_plan']

    #формируем единую метку дней
    day = []
    for day1 , day2 in zip (df_transaction_plan['day'].values , df_transaction_plan['day_month'].values):
        if np.isnan(day1):
            day.append(int(day2))
        else:
            day.append(int(day1))

    df_transaction_plan['day'] = day   


    df_transaction_plan.sort_values(by = ['day'] , inplace = True , ascending = True)

    df_transaction_plan.reset_index(inplace = True)

    df_transaction_plan.drop(labels = 'index' , axis = 1 , inplace = True)

    dict_change_plan = df_transaction_plan.iloc[change_num-1]
        

    if np.isnan(dict_change_plan['day_month']):
        cur = conn.cursor()
        id_change = dict_change_plan['id']
        cur.execute("update public.month_transaction_plan set day = %(date_plan)s where id = %(id_change)s" % {'date_plan' : int(date_plan) , 'id_change' : id_change} )
        conn.commit()
        cur.close()
    else:
        cur = conn.cursor()
        id_change = dict_change_plan['id']
        cur.execute("update public.transaction_plan set date_plan = '%(date_plan)s' where id = %(id_change)s" % {'date_plan' : date_plan , 'id_change' : id_change} )
        conn.commit()
        cur.close()
        
        

    return response



def add_task(chat_id = None  , date_plan = None , dict_user_data = None):

    # создаем запрос
    cur = conn.cursor()
    #формат ответа
    response = {'status' : 200
                ,'report' : 'add_task'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }
    try:
        #получаем входные данные
        task_name = dict_user_data['state_info_2']
        user_id = dict_user_data['user_id']
        
        #проверяем, важность этого дела, если первый символ без пробела '!' значит дело важное, иначе нет
        is_main_task = task_name.replace(' ','')[0] == "!"

        #стандартный ответ
        response['text'] = 'Записано! Я напомню Вам о данном деле, можете не переживать.'

        #проверяем если задача сегодня
        if date_plan == 'сегодня':
            date_plan = today_str_func()
            response['text'] = 'Оки-доки - не забудь сегодня только сделать ' + emoji('смайл_прищур') 

        #получаем время записи
        #если дело важное записываем флаг flg_main = True иначе flg_main = False
        if is_main_task:
            cur.execute("INSERT INTO public.tasks (user_id ,task , date_task , flg_done, flg_main) VALUES (%(user_id)s,'%(task_name)s','%(date_plan)s',False,True)" % {'user_id' : user_id , 'task_name' : task_name , 'date_plan' : date_plan }  )
        else:
            cur.execute("INSERT INTO public.tasks (user_id ,task , date_task , flg_done, flg_main) VALUES (%(user_id)s,'%(task_name)s','%(date_plan)s',False,False)" % {'user_id' : user_id , 'task_name' : task_name , 'date_plan' : date_plan }  )
        conn.commit()
        cur.close()
        
    except:
        cur.close()
        response['text'] = 'Что-то пошло не так, не получилось записать...'


    return response

def check_task(chat_id = None  , command = None , dict_user_data = None):
    # создаем запрос
    cur = conn.cursor()
    #формат ответа
    response = {'status' : 200
                ,'report' : 'check_task'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }
    try:
        #получаем входные данные
        user_id = dict_user_data['user_id']
        #получаем данные
        if command == 'На сегодня':
            cur.execute("select * from public.tasks where  user_id = %(user_id)s and date_task >= date_trunc('day', now()) and date_task < date_trunc('day', now()) +  interval '1 day'" % {  'user_id' : user_id} )
        elif command == 'На текущую неделю':
            cur.execute("select * from public.tasks where  user_id = %(user_id)s and date_task >= date_trunc('week', now()) and date_task < date_trunc('week', now()) + interval '7 day'" % {  'user_id' : user_id} )
        elif command == 'На текущий месяц':
            cur.execute("select * from public.tasks where  user_id = %(user_id)s and date_task >= date_trunc('month', now()) and date_task < date_trunc('month', now()) + interval '1 month'" % {  'user_id' : user_id} )

        df_plan_tasks = DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description]).sort_values(by='date_task' , ascending=True)

        cur.close()

        #смотрим df по запросу и готовим текст
        if df_plan_tasks.shape[0] == 0:
            response['text'] = command + ' дел нет.'
        else:
            text = command + ' следующие дела:\n\n'
            num = 1
            for row in df_plan_tasks.iterrows():
                if command != 'На сегодня':
                    date_row_task = row[1]['date_task'].strftime('%d.%m.%Y')
                else:
                    date_row_task = ''
                text += str(num) + ': ' + row[1]['task'] + ' ' + date_row_task + '\n'
                num += 1

            #здесь добавить предложение что-то сделать
            response['text'] = text
            response['reply_markup'] = meta_info.markup_non_important_to_tommorow




    except:
        cur.close()
        response['text'] = 'Что-то пошло не так, не получилось записать...'

    return response



def move_to_tomorrow(chat_id = None , dict_user_data = None):


    #получаем дату в строке завтрашнего дня
    tomorrow_str = tomorrow_str_func()
    #получаем дату в строке завтрашнего дня
    today_str = today_str_func()



    # создаем запрос
    cur = conn.cursor()
    #формат ответа
    response = {'status' : 200
                ,'report' : 'move_to_tomorrow'
                ,'system_message' : 'No report'
                ,'text' : None
                ,'reply_markup' : None
                }
    try:
        #получаем входные данные
        user_id = dict_user_data['user_id']
        
        
        #помечаем их как невыполненные
        cur.execute("update tasks set flg_done = False where user_id = %(user_id)s and date_task = '%(today_str)s' and flg_main is False" % {'user_id' : user_id  , 'tomorrow_str' : tomorrow_str , 'today_str' : today_str})
        conn.commit()

        #переносим все неважные дела на завтра
        cur.execute("update tasks set date_task = '%(tomorrow_str)s' where user_id = %(user_id)s and date_task = '%(today_str)s' and flg_main is False" % {'user_id' : user_id  , 'tomorrow_str' : tomorrow_str , 'today_str' : today_str})
        conn.commit()



        cur.close()
        response['text'] = 'Неважные дела пересены на завтра, расслабтесь сегодня! ' + emoji('руки_вверх') + emoji('руки_вверх') + emoji('руки_вверх')
    except:
        cur.close()
        response['text'] = 'Что-то пошло не так, не получилось записать...'


    return response




#запись информации по токену для todoist
def add_external_app(chat_id = None  , external_app = None , external_app_token = None , dict_user_data = None):
    
    user_id = dict_user_data['user_id']

    # создаем запрос
    cur = conn.cursor()
    #проверяем, что пользователя ранее не было
    cur.execute("SELECT * from public.external_token where user_id = %(user_id)s and external_app = '%(external_app)s'" % {'user_id' : user_id , 'external_app':external_app} )
    #получаем время записи
    now = datetime.now()
    message_at = now_str()
    #если запись есть - обновляем токен
    if cur.statusmessage[-3:] != 'T 0':
        #обновляем токен
        cur.execute("UPDATE public.external_token  SET external_app_token = '%(external_app_token)s' , date_update = '%(message_at)s' WHERE user_id  = %(user_id)s and external_app = '%(external_app)s'" % {'external_app_token' : external_app_token, 'user_id' : user_id , 'message_at':message_at , 'external_app':external_app}  )
        conn.commit()
    #есле ранее не было такого аппа у пользователя или пользователя вообще то записываем
    else:
        cur.execute("INSERT INTO public.external_token (user_id , external_app,external_app_token,date_update)  VALUES (%(user_id)s, '%(external_app)s','%(external_app_token)s','%(message_at)s')" % {'external_app_token' : external_app_token, 'user_id' : user_id , 'message_at':message_at , 'external_app':external_app}  )
        conn.commit()



    cur.close()

    return '200'

