from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
from pandas import DataFrame
import traceback

from methods import access
from methods import crypto
from methods.emoji import emoji
from methods import telegram_bot_methods
from methods import google_maps_methods
from methods import psql_methods
from methods import psql_cron_methods
from methods import reply




token = access.token()
api = access.api()

#bot = telebot.TeleBot(token)

application = Flask(__name__)  # Change assignment here

#главное меню делаем глобальной переменной
g_reply_markup_main = {'keyboard': [['Отчеты','Кошелек'],['Инвестиции','Дела']], 'resize_keyboard': True, 'one_time_keyboard': False}


# создаем webhook
@application.route("/set_webhook")
def webhook():
    url = api + token + '/setWebhook'
    params = {'url' : 'https://fin-budg-bot.herokuapp.com/main'
    }
    r = requests.post(url,
                      json=params)
    return "!", 200



# тестовый вывод
@application.route("/")  
def hello():
    return "Hello World!"

#тест крона
@application.route('/cron_test', methods=['GET', 'POST'])
def cron_test():
    #берем данные из get запроса
    n = request.args.get("n")
    text = str(n)
    chat_id = 84723474
    send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = None)

    return "!", 200



#рабочий крон cron-job.org
@application.route('/cron_woker_1', methods=['GET', 'POST'])
def cron_worker_1():
    try:
        #берем данные из get запроса
        model = request.args.get("model")
        #главное меню
        global g_reply_markup_main
        reply_markup_main = g_reply_markup_main
        r = psql_cron_methods.main_woker_1(model = model)

        if 'int' not in str(type(r)):
            if r['system_message'] == 'Have reports':
                list_messages = r['user_messages']
                for message in list_messages:
                    #отправляем сообщение
                    chat_id = str(message['chat_id'])
                    text = message['message']
                    send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup_main)



        return "!", 200
    except:
        #тест - для тестирования
        traceback.print_exc()
        return "!", 200




# запуск основной функции
@application.route('/main', methods=['GET', 'POST'])
def main():
    try:
        json_update = json.loads(request.get_data())


        #Изначально для отправки кнопки пустые
        reply_markup = None
        #главное меню
        global g_reply_markup_main
        reply_markup_main = g_reply_markup_main

        #получаем id чата и текст сообщения
        chat_id = json_update['message']['chat']['id']
        command = json_update['message']['text']

        #получаем список трат
        keyboard_expense , list_expense_types = reply.list_expense_types()


        #получаем текущее состояние
        dict_user_data = psql_methods.user_data(chat_id)
        last_state = dict_user_data['last_state']
        state_info_1 = dict_user_data['state_info_1']
        state_info_2 = dict_user_data['state_info_2']
        state_info_3 = dict_user_data['state_info_3']
        state_info_4 = dict_user_data['state_info_4']
        state_info_5 = dict_user_data['state_info_5']
        user_id = dict_user_data['user_id']
        personal_wallet_id = dict_user_data['personal_wallet_id']


        #в зависимости от команды выбираем действие
        if 'start' in command:
            r = psql_methods.new_user(chat_id , json_update)
            text = emoji('фанфары') + 'Добрый день! \n' 
            text += 'Я веду домашний бюджет и напоминаю об операциях в течение месяца. \n'
            text += 'Я развиваюсь в свободное время, потом будет интереснее. \n'
            text += 'Сначала заведите свой кошелек и забудьте о том, чтобы держать бюджет семьи в голове!' + emoji('банкноты')
            reply_markup = {'keyboard': [['Создать кошелек']], 'resize_keyboard': True, 'one_time_keyboard': False}

        elif 'Создать кошелек' in command:
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.make_wallet(chat_id)
            text = r['text']
            #reply_markup = r['reply_markup']
            reply_markup = reply_markup_main

        elif 'help' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Привет!' +  emoji('фанфары') + '\n'
            text += 'Что я понимаю: \n'
            text += 'Кошелек - работа с кошельком, формирование фактических и плановых трат \n'
            text += 'Дела - запланированный перечень задач, планы, напоминание и тому подобное \n'
            text += 'Отчеты - различные отчеты с интересной информацией \n'
            text += 'Инвестиции - информация по курсам валют, личным вкладам, инвестиционным портфелям \n'
            reply_markup = reply_markup_main

        elif 'wallet_action' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Что нужно сделать с личным кошельком? \n'
            text += '/expense_add - добавить фактическую операцию'
            reply_markup = {'keyboard': [['/expense_add'],['/main']], 'resize_keyboard': True, 'one_time_keyboard': False}
        
        #возвращение в главное меню
        elif 'меню' in command:
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.clear_state(chat_id = chat_id)
            text = 'Окей!' + emoji('thumbs_up') + ' Что хотим сделать?'
            reply_markup = reply_markup_main


        ############################################################
        #################  Действия с советником  ##################
        ############################################################
        #1 кошелек
        #1->1 - выбор действия кошелька
        elif 'Кошелек' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Что сделать с кошельком?'
            reply_markup = {'keyboard': [['Траты факт - добавить'],['Траты план - добавить'],['Траты план - список']], 'resize_keyboard': True, 'one_time_keyboard': False}

        #1->1-> - выбор траты 
        elif last_state == 'Кошелек':
            #1->1->1 - добавление фактической траты
            if command == 'Траты факт - добавить':
                r = psql_methods.last_state(chat_id,command)
                text = 'Выберите тип траты'
                reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2 - добавление плановой траты
            if command == 'Траты план - добавить':
                r = psql_methods.last_state(chat_id,command)
                text = 'Это разовая трата или повторяется каждый месяц?'
                reply_markup = {'keyboard': [['Разовая'],['Каждый месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}
            #1->1->3 - список плановых трат
            if command == 'Траты план - список':
                r = psql_methods.last_state(chat_id,command)
                r = psql_methods.list_transaction_plan(chat_id, user_id)
                if r['system_message'] == 'Have reports':
                    text = r['text']
                    reply_markup = r['reply_markup']
                else:
                    r = psql_methods.last_state(chat_id,'/main')
                    text = 'В текущем месяце нет плановых трат...'
                    reply_markup = reply_markup_main



        #сценарий для фактической траты
        #1->1->1->1 - если пришел запрос на добавление траты по типу - спрашиваем сумму
        elif last_state == 'Траты факт - добавить':
            if command in list_expense_types:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'ОК! Введите сумму операции'
                reply_markup = None
            if state_info_1 in list_expense_types:
                command = command.replace(',','.')
                try:
                    summa = round(float(command),2)
                    r = psql_methods.add_transaction_fact(chat_id = chat_id , summa = summa , dict_user_data = dict_user_data)
                    if r == 200:
                        text = 'Операция добавлена!'
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')

                        reply_markup = reply_markup_main
                    if r == 400:
                        text = 'Ведутся какие-то работы... Повторите позже...'
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')

                        reply_markup = reply_markup_main
                except:
                    text = 'Введите цифрами...'
                    reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}



        #сценарий для плановой разовой траты
        #1->1->2->1
        elif last_state == 'Траты план - добавить':
            if command == 'Разовая':
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'Напишите, что за трата? я напомню Вам о ней.'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2->1->1
            elif state_info_1 == 'Разовая' and state_info_2 is None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
                text = 'Понял понял, в какую дату должна произойти трата? В формате -> 22.03.1990'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2->1->1->1
            elif state_info_1 == 'Разовая' and state_info_3 is None:

                date_list = command.split('.')
                error = 0
                date_plan = ''
                if len(date_list) != 3:
                    text = 'Некорректный формат, повторите ввод даты'   
                    reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                else:
                    for date_part in date_list:
                        try:
                            if int(date_part) < 10 and len(date_part)==1:
                                date_part = '0' + date_part
                                date_plan = date_part + date_plan
                            else:
                                date_plan = date_part + date_plan
                        except:
                            error = 1
                    
                    if error == 1:
                        text = 'Не могу разобрать... Проверьте формат и повторите ввод даты.'
                        reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                    else:
                        r = psql_methods.insert_state_info(chat_id = chat_id , state_info = date_plan , state_id = 3)
                        text = 'Записал! К какому типу трат относится?'

                        reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': False}
            #1->1->2->1->1->1->1
            elif state_info_1 == 'Разовая' and state_info_4 is None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 4)
                text = 'ОК! Введите сумму операции'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2->1->1->1->1->1
            elif state_info_1 == 'Разовая' and state_info_4 is not None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 5)
                command = command.replace(',','.')
                try:
                    summa = round(float(command),2)
                    r = psql_methods.add_transaction_plan(chat_id = chat_id , summa = summa , dict_user_data = dict_user_data)
                    
                    if r == 200:
                        text = 'Операция добавлена! Я напомню о ней за день!'
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')

                        reply_markup = reply_markup_main
                    if r == 400:
                        text = 'Ведутся какие-то работы... Повторите позже...'
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')

                        reply_markup = reply_markup_main
                except:
                    text = 'Введите цифрами...'
                    reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}




            #сценарий для плановой периодической траты
            elif command == 'Каждый месяц':
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'Напишите, что за трата? я буду напоминать Вам о ней каждый месяц.'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2->2->1
            elif state_info_1 == 'Каждый месяц' and state_info_2 is None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
                text = 'ОК! в какой день месяца нужно делать эту трату? 1 - 28'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2->2->1->1
            elif state_info_1 == 'Каждый месяц' and state_info_3 is None:

                error = 0
                try:
                    date_day = int(command)
                    if date_day > 28:
                        error = 1
                except:
                    date_day = 'unknown'
                    error = 1

                if error == 1:
                    text = 'Ну цифру напиши от 1 до 28'   
                    reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                else:

                    r = psql_methods.insert_state_info(chat_id = chat_id , state_info = date_day , state_id = 3)
                    text = 'Записал! К какому типу трат относится?'

                    reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': False}
            #1->1->2->2->1->1->1
            elif state_info_1 == 'Каждый месяц' and state_info_4 is None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 4)
                text = 'ОК! Введите сумму, которую необходимо тратить.'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->2->2->1->1->1->1
            elif state_info_1 == 'Каждый месяц' and state_info_4 is not None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 5)
                command = command.replace(',','.')
                try:
                    summa = round(float(command),2)
                    r = psql_methods.add_transaction_plan_month(chat_id = chat_id , summa = summa , dict_user_data = dict_user_data)
                    
                    if r == 200:
                        text = 'Операция добавлена! Я буду напоминать Вам о ней, поручитесь на меня!'
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')

                        reply_markup = reply_markup_main
                    if r == 400:
                        text = 'Ведутся какие-то работы... Повторите позже...'
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')

                        reply_markup = reply_markup_main
                except:
                    traceback.print_exc()
                    text = 'Введите цифрами...'
                    reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}



        #сценарий для работы с Траты план - список
        #1->1->3->
        elif last_state == 'Траты план - список':
            #1->1->3->1
            if command == 'Добавить':
                #переходим на сценарий 1->1->2
                r = psql_methods.last_state(chat_id,'Траты план - добавить')
                text = 'Это разовая трата или повторяется каждый месяц?'
                reply_markup = {'keyboard': [['Разовая'],['Каждый месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}
            #1->1->3->2
            if command == 'Удалить':
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'Ладушки-аладушки! Напишите номер плановой операции, которую нужно удалить, все сделаю!'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->3->2->1
            elif state_info_1 == 'Удалить' and state_info_2 is None:
                try:
                    delete_num = int(command)
                    r = psql_methods.delete_transaction_plan(chat_id, user_id ,delete_num)
                    text = r['text']
                    reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                except:
                    traceback.print_exc()
                    text = 'мммм, чего то не пойму... Введите существующий номер плановой операции, указанной в списке'
                    reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->3->3
            if command == 'Изменить':
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'Оки-доки! Напишите номер плановой операции, по которой нужно изменить дату!'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->3->3->1
            elif state_info_1 == 'Изменить' and state_info_2 is None:
                try:
                    change_num = int(command)
                    r = psql_methods.change_transaction_plan_1(chat_id, user_id ,change_num)
                    transaction_type = r['system_message']
                    text = r['text']
                    reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
                    if r['system_message'] != 'No report':
                        r = psql_methods.insert_state_info(chat_id = chat_id , state_info = change_num , state_id = 2)
                        r = psql_methods.insert_state_info(chat_id = chat_id , state_info = transaction_type , state_id = 3)
                except:
                    traceback.print_exc()
                    text = 'Блин, ну нет такого номера... Введите существующий номер плановой операции, указанной в списке'
                    reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            #1->1->3->3->2
            elif state_info_1 == 'Изменить' and state_info_3 is not None:
                if state_info_3 == 'once':
                    date_list = command.split('.')
                    error = 0
                    date_plan = ''
                    if len(date_list) != 3:
                        text = 'Некорректный формат, повторите ввод даты'   
                        reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                    else:
                        for date_part in date_list:
                            try:
                                if int(date_part) < 10 and len(date_part)==1:
                                    date_part = '0' + date_part
                                    date_plan = date_part + date_plan
                                else:
                                    date_plan = date_part + date_plan
                            except:
                                error = 1
                        
                        if error == 1:
                            text = 'Не могу разобрать... Проверьте формат и повторите ввод даты.'
                            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                        else:
                            r = psql_methods.change_transaction_plan_2(chat_id = chat_id, user_id = user_id , change_num = state_info_2 , type = state_info_3 , date_plan = date_plan)
                            text = 'Перенесено на ' + command + ' хозяин!'
                            reply_markup = reply_markup_main
                            r = psql_methods.clear_state(chat_id = chat_id)
                            r = psql_methods.last_state(chat_id,'/main')
                elif state_info_3 == 'monthly':
                    date_plan = int(command)
                    if date_plan > 28:
                        text = 'оу оу, Дата не влазит, введите от 1 до 28'   
                        reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                    else:
                        r = psql_methods.change_transaction_plan_2(chat_id = chat_id, user_id = user_id , change_num = state_info_2 , type = state_info_3 , date_plan = date_plan)
                        text = 'Перенесено на ' + command + ' хозяин!'
                        reply_markup = reply_markup_main
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')






        #2 - отчеты
        #отчеты по кошельку
        elif 'Отчеты' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Какой отчет построить?'
            reply_markup = {'keyboard': [['Траты - месяц назад'],['Траты - текущий месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}


        #если пришел запрос на какой-либо отчет - строим
        elif last_state == 'Отчеты':
            #выбираем отчет
            if command == 'Траты - месяц назад':
                r = psql_methods.last_state(chat_id,command)
                r = psql_methods.report_prev_expense(chat_id = chat_id , user_id = user_id)
                text = r['text']
                reply_markup = reply_markup_main
            elif command == 'Траты - текущий месяц':
                r = psql_methods.last_state(chat_id,command)
                r = psql_methods.report_cur_expense(chat_id = chat_id , user_id = user_id)
                text = r['text']
                reply_markup = reply_markup_main
            else:
                text = 'Ой нету ведь такого отчета, ну о чем Вы...'
                reply_markup = reply_markup_main




        #3 - курсы
        #здесь запосы к криптовалютам
        elif 'Инвестиции' in command:
            ETH_USD = crypto.crypto_curse()
            text = str(ETH_USD) + ' $ за дозу эфирчика...'
            reply_markup = reply_markup_main


        #4 - Дела
        elif 'Дела' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Да да, слушаю. Что с делами?'
            reply_markup = {'keyboard': [['Записать дело'],['Список дел']], 'resize_keyboard': True, 'one_time_keyboard': False}

        #4-> начало работы с делами
        elif last_state == 'Дела':
            #4->1 Записать дело - название
            if command == 'Записать дело':
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'Напишите, что за дело? Я запишу это, чтобы Вам не держать это в голове!'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            
            #4->1->1 указываем дату
            elif state_info_1 == 'Записать дело' and state_info_2 is None:
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
                text = 'Ясно-понятно, запомнил! Укажите, в какую дату необходимо сделать данное дело? В формате -> 22.03.1990'
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}


            #4->1->1->1 записываем!
            elif state_info_1 == 'Записать дело' and state_info_3 is None:
                date_list = command.split('.')
                error = 0
                date_plan = ''
                if len(date_list) != 3:
                    text = 'Некорректный формат, повторите ввод даты'   
                    reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                else:
                    for date_part in date_list:
                        try:
                            if int(date_part) < 10 and len(date_part)==1:
                                date_part = '0' + date_part
                                date_plan = date_part + date_plan
                            else:
                                date_plan = date_part + date_plan
                        except:
                            error = 1
                    
                    if error == 1:
                        text = 'Не могу разобрать... Проверьте формат и повторите ввод даты.'
                        reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                    else:
                        r = psql_methods.add_task(chat_id = chat_id  , date_plan = date_plan , dict_user_data = dict_user_data)
                        text = r['text']
                        reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')
            #4->2 Сисок дел - выбор
            elif command == 'Список дел':
                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
                text = 'На какой период интересует?'
                reply_markup = {'keyboard': [['На дату'],['На текущую неделю'],['На текущий месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}
            #4->2->1 Получаем данные
            elif state_info_1 == 'Список дел' and state_info_2 is None:
                text = 'аха, ниче не готово...'
                reply_markup = reply_markup_main
                #r = psql_methods.check_task(chat_id = chat_id  , date_plan = date_plan , dict_user_data = dict_user_data)
                #доработать
                r = psql_methods.clear_state(chat_id = chat_id)
                r = psql_methods.last_state(chat_id,'/main')



        #-> хз што это
        else:
            text = 'Неизвестная команда, для списка команд выбирите команду /help'
            reply_markup = reply_markup_main


        #отправляем сообщение
        send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup)




            
        return "!", 200
    except:

        #тест - для тестирования
        traceback.print_exc()



        return "!", 200







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

