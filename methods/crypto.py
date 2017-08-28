import requests
import access
import json
from datetime import datetime
from time import sleep





#функция получения курса эфира в долларах
def crypto_curse():

    url = 'https://api.cryptonator.com/api/ticker/eth-usd'

    r = requests.get(url)
    
    dict_crypto_curse = json.loads(r.text)

    ETH_USD = round(float(dict_crypto_curse['ticker']['price']), 3)



    return ETH_USD


