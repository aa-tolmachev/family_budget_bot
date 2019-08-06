from methods import psql_methods

from dicts import meta_info

from methods import reply

def main(command = None , chat_id = None, dict_user_data = None):

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


   #2 - отчеты
    #отчеты по кошельку
    if 'Отчеты' in command:
        r = psql_methods.last_state(chat_id,command)
        text = 'Какой отчет построить?'
        reply_markup = {'keyboard': [['Траты - месяц назад'],['Траты - текущий месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}


    #если пришел запрос на какой-либо отчет - строим
    elif last_state == 'Отчеты':
        #выбираем отчет
        if command == 'Траты - месяц назад':
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.report_prev_expense(chat_id = chat_id , user_id = user_id)
            text = r['text']
            reply_markup = reply_markup_main
        elif command == 'Траты - текущий месяц':
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.report_cur_expense(chat_id = chat_id , user_id = user_id)
            text = r['text']
            reply_markup = reply_markup_main
        else:
            text = 'Ой нету ведь такого отчета, ну о чем Вы...'
            reply_markup = reply_markup_main


    return text , reply_markup