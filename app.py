from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json


import family_budget
import access
from methods.emoji import emoji


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
        #Тестовый блок, при получении сообщения пробрасываем json обратно, чтобы посмотреть, что получаем
        #json_str = str(json_update)
        

        #url = api + token + '/sendMessage'
        #params = {'chat_id' : 84723474
        #        ,'text' : json_update
        #}
        #r = requests.post(url,
        #                  json=params)





        #получаем id чата и текст сообщения
        chat_id = json_update['message']['chat']['id']
        command = json_update['message']['text']

        #в зависимости от команды выбираем действие
        if command[0] != '/':
            text = 'Неизвестная команда, для списка команд выбирите команду /help'

        else:
            if 'start' in command:
                text = emoji('фанфары') + 'Добрый день! \n' 
                text += 'Я планирую домашнего бюджета и напоминаю об операциях в течение месяца. \n'
                text += 'Я развиваюсь в свободное время, текущие команды можно увидеть в меню /help. \n'
                text += 'Либо сразу заведите свой кошелек и забудьте о том, чтобы держать бюджет семьи в голове!' + emoji('банкноты')
            elif 'help' in command:
                text = 'Раздел разрабатывается, тут всё понятно, заводи кошелек и стартуем!'
            else:
                text = 'Не понимаю...'
  

        #! переделать в функцию
        url = api + token + '/sendMessage'
        params = {'chat_id' : chat_id
                ,'text' : text
        }
        r = requests.post(url,
                          json=params)

        #family_budget.main()
            
        return "!", 200
    except:

        return "!", 200







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

