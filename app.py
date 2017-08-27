from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
from pandas import DataFrame


from methods import access
from methods.emoji import emoji
from methods import telegram_bot_methods
from methods import google_maps_methods
from methods import psql_methods




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

        #получаем id чата и текст сообщения
        chat_id = json_update['message']['chat']['id']
        command = json_update['message']['text']

        #в зависимости от команды выбираем действие
        if command[0] != '/':
            text = 'Не понимаю... Помочь? /help'

        else:
            if 'start' in command:
                r = psql_methods.new_user(chat_id , json_update)
                text = emoji('фанфары') + 'Добрый день! \n' 
                text += 'Я планирую домашний бюджет и напоминаю об операциях в течение месяца. \n'
                text += 'Я развиваюсь в свободное время, текущие команды можно увидеть в меню /help. \n'
                text += 'Либо сразу заведите свой кошелек и забудьте о том, чтобы держать бюджет семьи в голове!' + emoji('банкноты')
                reply_markup = {'keyboard': [['/help'],['/make_wallet']], 'resize_keyboard': True, 'one_time_keyboard': True}
            elif 'help' in command:
                r = psql_methods.last_state(chat_id,command)
                text = 'Привет!' +  emoji('фанфары') + '\n'
                text += 'Задачи кошелька: \n'
                text += '/make_wallet - создание кошелька \n'
                text += '/expense_add - добавить трату \n'
                text += '/expense_update - изменить/удалить трату \n'
                text += '/wallet_report - отчет по операциям \n'
                text += '/wallet_advice - совет'
            elif 'make_wallet' in command:
                r = psql_methods.last_state(chat_id,command)
                r = psql_methods.make_wallet(chat_id)
                text = r['text']
                reply_markup = r['reply_markup']
            elif 'wallet_action' in command:
                r = psql_methods.last_state(chat_id,command)
                text = 'Что нужно сделать с личным кошельком? \n'
                text += '/expense_add - добавить фактическую операцию'




            else:
                text = 'Неизвестная команда, для списка команд выбирите команду /help'
  
        #отправляем сообщение
        send_result = telegram_bot_methods.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup)




            
        return "!", 200
    except:

        return "!", 200







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

