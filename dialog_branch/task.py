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

    #4 - Дела
    if 'Дела' in command:
        r = psql_methods.last_state(chat_id,command)
        text = 'Да да, слушаю. Что с делами?'
        reply_markup = {'keyboard': [['Записать дело'],['Список дел']], 'resize_keyboard': True, 'one_time_keyboard': False}

    #4-> начало работы с делами
    elif last_state == 'Дела':
        #4->1 Записать дело - название
        if command == 'Записать дело':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'Напишите, что за дело? Я запишу это, чтобы Вам не держать это в голове! Укажите "!" в начале и я пойму, что это очень важное дело.'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        
        #4->1->1 указываем дату
        elif state_info_1 == 'Записать дело' and state_info_2 is None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
            text = 'Ясно-понятно, запомнил! Укажите, в какую дату необходимо сделать данное дело? В формате -> 22.03.1990'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}


        #4->1->1->1 записываем!
        elif state_info_1 == 'Записать дело' and state_info_3 is None:
            date_list = command.split('.')
            error = 0
            date_plan = ''
            if len(date_list) != 3:
                text = 'Некорректный формат, повторите ввод даты'   
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            else:
                for date_part in date_list:
                    try:
                        if int(date_part) < 10 and len(date_part)==1:
                            date_part = '0' + date_part
                            date_plan = date_part + date_plan
                        else:
                            date_plan = date_part + date_plan
                    except:
                        error = 1
                
                if error == 1:
                    text = 'Не могу разобрать... Проверьте формат и повторите ввод даты.'
                    reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                else:
                    r = psql_methods.add_task(chat_id = chat_id  , date_plan = date_plan , dict_user_data = dict_user_data)
                    text = r['text']
                    reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')
        #4->2 Сисок дел - выбор
        elif command == 'Список дел':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'На какой период интересует?'
            reply_markup = {'keyboard': [['На сегодня'],['На текущую неделю'],['На текущий месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}
        #4->2->1 Получаем данные
        elif state_info_1 == 'Список дел' and state_info_2 is None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
            r = psql_methods.check_task(chat_id = chat_id  , command = command , dict_user_data = dict_user_data)
            text = r['text']
            reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
            #доработать
            r = psql_methods.clear_state(chat_id = chat_id)
            r = psql_methods.last_state(chat_id,'/main')


    return text , reply_markup