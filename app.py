"""Flask App Project."""
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
app = Flask(__name__)

#главное меню делаем глобальной переменной
g_reply_markup_main = meta_info.reply_markup_main


@app.route('/')
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run()

