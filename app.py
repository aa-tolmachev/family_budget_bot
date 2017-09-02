from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
from pandas import DataFrame


from methods import access
from methods import crypto
from methods.emoji import emoji
from methods import telegram_bot_methods
from methods import google_maps_methods
from methods import psql_methods
from methods import reply




token = access.token()
api = access.api()

#bot = telebot.TeleBot(token)

application = Flask(__name__)  # Change assignment here




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




# запуск основной функции
@application.route('/main', methods=['GET', 'POST'])
def main():
    try:
        json_update = json.loads(request.get_data())


        #Изначально для отправки кнопки пустые
        reply_markup = None
        #главное меню
        reply_markup_main = {'keyboard': [['/expense_add'],['/report'],['/crypto_ETH_USD']], 'resize_keyboard': True, 'one_time_keyboard': False}

        #получаем id чата и текст сообщения
        chat_id = json_update['message']['chat']['id']
        command = json_update['message']['text']

        #получаем список трат
        keyboard_expense , list_expense_types = reply.list_expense_types()

        #получаем текущее состояние
        dict_user_data = psql_methods.user_data(chat_id)
        last_state = dict_user_data['last_state']
        state_info_1 = dict_user_data['state_info_1']
        user_id = dict_user_data['user_id']
        personal_wallet_id = dict_user_data['personal_wallet_id']


        #в зависимости от команды выбираем действие
        if 'start' in command:
            r = psql_methods.new_user(chat_id , json_update)
            text = emoji('фанфары') + 'Добрый день! \n' 
            text += 'Я веду домашний бюджет и напоминаю об операциях в течение месяца. \n'
            text += 'Я развиваюсь в свободное время, текущие команды можно увидеть в меню /help. \n'
            text += 'Либо сразу заведите свой кошелек и забудьте о том, чтобы держать бюджет семьи в голове!' + emoji('банкноты')
            reply_markup = {'keyboard': [['/help'],['/make_wallet']], 'resize_keyboard': True, 'one_time_keyboard': False}
        elif 'help' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Привет!' +  emoji('фанфары') + '\n'
            text += 'Задачи кошелька: \n'
            text += '/make_wallet - создание кошелька \n'
            text += '/expense_add - добавить трату \n'
            text += '/expense_update - изменить/удалить трату \n'
            text += '/wallet_report - отчет по операциям \n'
            text += '/wallet_advice - совет'
            reply_markup = None
        elif 'make_wallet' in command:
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.make_wallet(chat_id)
            text = r['text']
            #reply_markup = r['reply_markup']
            reply_markup = reply_markup_main
        elif 'wallet_action' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Что нужно сделать с личным кошельком? \n'
            text += '/expense_add - добавить фактическую операцию'
            reply_markup = {'keyboard': [['/expense_add'],['/main']], 'resize_keyboard': True, 'one_time_keyboard': False}
        elif 'expense_add' in command:
            r = psql_methods.last_state(chat_id,command)
            text = 'Выберите тип траты'
            reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': True}
       
        #если пришел запрос на добавление траты по типу - спрашиваем сумму
        elif last_state == '/expense_add':
            if command in list_expense_types:
                r = psql_methods.insert_state_info_1(chat_id = chat_id , state_info_one = command)
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
                    reply_markup = None


        #отчеты по кошельку
        elif 'report' in command:
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.report_prev_expense(chat_id = chat_id , user_id = user_id)
            text = r['text']
            reply_markup = reply_markup_main




        #возвращение в главное меню
        elif 'main' in command:
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.clear_state(chat_id = chat_id)
            text = 'Что хотим сделать?'
            reply_markup = reply_markup_main

        #здесь запосы к криптовалютам
        elif 'crypto_ETH_USD' in command:
            ETH_USD = crypto.crypto_curse()
            text = str(ETH_USD) + ' $ за дозу эфирчика...'
            reply_markup = reply_markup_main




        else:
            text = 'Неизвестная команда, для списка команд выбирите команду /help'
            reply_markup = reply_markup_main


        #отправляем сообщение
        send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup)




            
        return "!", 200
    except:

        #тест - для тестирования
        import traceback
        traceback.print_exc()



        return "!", 200







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

