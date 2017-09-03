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
        created_at = now_str()
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

