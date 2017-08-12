from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import requests

import os

TOKEN = "382244799:AAFfN3evzGDQaRevpW5xqZ1AEovvdRCWk-0"
PORT = int(os.environ.get('PORT', '5000'))
updater = Updater(TOKEN)
# add handlers
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Iма")


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
    
start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text, echo)
                         
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://fam-budg-bot.herokuapp.com/" + TOKEN)
updater.idle()