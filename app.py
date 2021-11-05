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


application = Flask(__name__)  # Change assignment here

# тестовый вывод
@application.route("/")  
def hello():
    return "Hello World!"


if __name__ == '__main__':
    application.run()