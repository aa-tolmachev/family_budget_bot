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
        #json_str = str(json_params)
        #family_budget.main()

        url = api + token + '/sendMessage'
        params = {'chat_id' : 84723474
                ,'text' : 'привет'
        }
        r = requests.post(url,
                          json=params)
            
        return "!", 200
    except:

        return "!", 200







if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    #port = 443
    application.run(debug=False, port=port, host='0.0.0.0')



