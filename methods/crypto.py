import requests
from methods import access
import json
from datetime import datetime
from time import sleep





#функция получения курса эфира в долларах
def crypto_curse():

    crypto_price_dict = {}

    url = 'https://api.cryptonator.com/api/ticker/eth-usd'

    r = requests.get(url)
    
    dict_crypto_curse = json.loads(r.text)

    ETH_USD = round(float(dict_crypto_curse['ticker']['price']), 3)
    crypto_price_dict['ETH_USD'] = ETH_USD

    url = 'https://api.cryptonator.com/api/ticker/ltc-usd'

    r = requests.get(url)
    
    dict_crypto_curse = json.loads(r.text)

    LTC_USD = round(float(dict_crypto_curse['ticker']['price']), 3)
    crypto_price_dict['LTC_USD'] = LTC_USD

    url = 'https://api.cryptonator.com/api/ticker/eos-usd'

    r = requests.get(url)
    
    dict_crypto_curse = json.loads(r.text)

    EOS_USD = round(float(dict_crypto_curse['ticker']['price']), 3)
    crypto_price_dict['EOS_USD'] = EOS_USD


    return crypto_price_dict


