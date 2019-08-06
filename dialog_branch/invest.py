from methods import psql_methods

from dicts import meta_info

from methods import reply

def main(command = None , chat_id = None, dict_user_data = None,json_update = None):

    text = 'непонимайт...'
    reply_markup = meta_info.reply_markup_main


    last_state = dict_user_data['last_state']
    state_info_1 = dict_user_data['state_info_1']
    state_info_2 = dict_user_data['state_info_2']
    state_info_3 = dict_user_data['state_info_3']
    state_info_4 = dict_user_data['state_info_4']
    state_info_5 = dict_user_data['state_info_5']
    user_id = dict_user_data['user_id']
    personal_wallet_id = dict_user_data['personal_wallet_id']

    reply_markup_main = meta_info.reply_markup_main

    #получаем список трат
    keyboard_expense , list_expense_types = reply.list_expense_types()

    #3 - курсы
    #здесь запосы к криптовалютам
    if 'Инвестиции' in command:
        crypto_price_dict = crypto.crypto_curse()

        text = str(crypto_price_dict['ETH_USD']) + ' $ за ETH... \n'
        text += str(crypto_price_dict['LTC_USD']) + ' $ за LTC... \n'
        text += str(crypto_price_dict['EOS_USD']) + ' $ за EOS... \n'

        reply_markup = reply_markup_main


    return text , reply_markup