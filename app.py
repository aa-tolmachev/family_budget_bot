from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
from pandas import DataFrame
import numpy as np
import traceback
from ast import literal_eval

from methods import access
from methods import crypto
from methods.emoji import emoji
from methods import telegram_bot_methods
from methods import google_maps_methods
from methods import psql_methods
from methods import psql_cron_methods
from methods import reply

from dicts import meta_info

from dialog_branch import *
import dialog_branch as dibr

from router import *
import router as router



token = access.token()
api = access.api()

#bot = telebot.TeleBot(token)

application = Flask(__name__)  # Change assignment here

#главное меню делаем глобальной переменной
g_reply_markup_main = meta_info.reply_markup_main


# создаем webhook
@application.route("/set_webhook")
def webhook():
    url = api + token + '/setWebhook'
    print(url)
    
    params = {'url' : 'https://finbudget-bot.herokuapp.com/main'
    }
    r = requests.post(url,
                      json=params)

    print(r.status_code)
    print(r.text)
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
                    reply_markup_main = g_reply_markup_main

                    #отправляем сообщение
                    chat_id = str(message['chat_id'])
                    text = message['message']
                    #проверяем, есть ли кастомные кнопки
                    if 'reply_markup' in message.keys():
                        reply_markup_main = message['reply_markup']

                    send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup_main)
                    #если к сообщению есть картинка, отправляем картинку
                    if 'photo_path' in message.keys():
                        photo_path = message['photo_path']
                        send_result = telegram_bot_methods.send_photo(chat_id = chat_id, photo_path = photo_path)

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

        print(json_update)


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


        #определяем направление ветки разговора
        meta_path = router.route.meta(chat_id = chat_id , command = command ,dict_user_data= dict_user_data)

        #направляем на запуск ветки разговора
        text , reply_markup = router.route.make_dialog_branch(meta_path= meta_path, chat_id= chat_id, command= command , dict_user_data= dict_user_data , json_update = json_update)

        #отправляем сообщение
        send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup)
  
        return "!", 200
    except:

        #тест - для тестирования
        traceback.print_exc()

        return "!", 200







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0' , threaded=True)
