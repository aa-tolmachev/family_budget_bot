from flask import Flask
from flask import request
import requests
from flask import make_response
import os
#import telebot


import family_budget
import access


token = access.token()
api = access.api()
#bot = telebot.TeleBot(token)

application = Flask(__name__)  # Change assignment here

# создаем webhook
@application.route("/set_webhook")
def webhook():
    url = api + token + '/setWebhook'
    params = {'url' : 'https://fam-budg-bot.herokuapp.com/main'
    }
    r = requests.post(url,
                      json=params)
    return "!", 200




# тестовый вывод
@application.route("/")  
def hello():
    return "Hello World!"




# тестовый запуск
@application.route('/main', methods=['GET', 'POST'])
def main():
    try:
        #json_params = json.loads(request.get_data())

        family_budget.main()
        
        return 'END'
    except:

        return 'ERROR'







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

