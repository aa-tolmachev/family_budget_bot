from flask import Flask
from flask import request
from flask import make_response
import os
from telegram.ext import Updater


import family_budget


application = Flask(__name__)  # Change assignment here




# тестовый вывод
@application.route("/")  
def hello():
    return "Hello World!"




# тестовый запуск
@application.route('/family_budget', methods=['GET', 'POST'])
def app_fb():
    try:
        #json_params = json.loads(request.get_data())

        family_budget.main()
        
        return 'END'
    except:

        return 'ERROR'





if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))


    TOKEN = "382244799:AAFfN3evzGDQaRevpW5xqZ1AEovvdRCWk-0"
    PORT = int(os.environ.get('PORT', '5000'))
    updater = Updater(TOKEN)
    # add handlers
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://family-budget-.herokuapp.com/382244799:AAFfN3evzGDQaRevpW5xqZ1AEovvdRCWk-0")
    updater.idle()
    application.run(debug=False, port=port, host='0.0.0.0')

