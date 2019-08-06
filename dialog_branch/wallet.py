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

    ############################################################
    #################  Действия с советником  ##################
    ############################################################
    #1 кошелек
    #1->1 - выбор действия кошелька
    if 'Кошелек' in command:
        r = psql_methods.last_state(chat_id,command)
        text = 'Что сделать с кошельком?'
        reply_markup = {'keyboard': [['Траты факт - добавить'],['Траты план - добавить'],['Траты план - список']], 'resize_keyboard': True, 'one_time_keyboard': False}

    #1->1-> - выбор траты 
    elif last_state == 'Кошелек':
        #1->1->1 - добавление фактической траты
        if command == 'Траты факт - добавить':
            r = psql_methods.last_state(chat_id,command)
            text = 'Выберите тип траты'
            reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2 - добавление плановой траты
        if command == 'Траты план - добавить':
            r = psql_methods.last_state(chat_id,command)
            text = 'Это разовая трата или повторяется каждый месяц?'
            reply_markup = {'keyboard': [['Разовая'],['Каждый месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}
        #1->1->3 - список плановых трат
        if command == 'Траты план - список':
            r = psql_methods.last_state(chat_id,command)
            r = psql_methods.list_transaction_plan(chat_id, user_id)
            if r['system_message'] == 'Have reports':
                text = r['text']
                reply_markup = r['reply_markup']
            else:
                r = psql_methods.last_state(chat_id,'/main')
                text = 'В текущем месяце нет плановых трат...'
                reply_markup = reply_markup_main



    #сценарий для фактической траты
    #1->1->1->1 - если пришел запрос на добавление траты по типу - спрашиваем сумму
    elif last_state == 'Траты факт - добавить':
        if command in list_expense_types:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'ОК! Введите сумму операции'
            reply_markup = None
        if state_info_1 in list_expense_types:
            command = command.replace(',','.')
            try:
                summa = round(float(command),2)
                r = psql_methods.add_transaction_fact(chat_id = chat_id , summa = summa , dict_user_data = dict_user_data)
                if r == 200:
                    text = 'Операция добавлена!'
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                    reply_markup = reply_markup_main
                if r == 400:
                    text = 'Ведутся какие-то работы... Повторите позже...'
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                    reply_markup = reply_markup_main
            except:
                text = 'Введите цифрами...'
                reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}



    #сценарий для плановой разовой траты
    #1->1->2->1
    elif last_state == 'Траты план - добавить':
        if command == 'Разовая':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'Напишите, что за трата? я напомню Вам о ней.'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2->1->1
        elif state_info_1 == 'Разовая' and state_info_2 is None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
            text = 'Понял понял, в какую дату должна произойти трата? В формате -> 22.03.1990'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2->1->1->1
        elif state_info_1 == 'Разовая' and state_info_3 is None:

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
                    r = psql_methods.insert_state_info(chat_id = chat_id , state_info = date_plan , state_id = 3)
                    text = 'Записал! К какому типу трат относится?'

                    reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': False}
        #1->1->2->1->1->1->1
        elif state_info_1 == 'Разовая' and state_info_4 is None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 4)
            text = 'ОК! Введите сумму операции'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2->1->1->1->1->1
        elif state_info_1 == 'Разовая' and state_info_4 is not None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 5)
            command = command.replace(',','.')
            try:
                summa = round(float(command),2)
                r = psql_methods.add_transaction_plan(chat_id = chat_id , summa = summa , dict_user_data = dict_user_data)
                
                if r == 200:
                    text = 'Операция добавлена! Я напомню о ней за день!'
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                    reply_markup = reply_markup_main
                if r == 400:
                    text = 'Ведутся какие-то работы... Повторите позже...'
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                    reply_markup = reply_markup_main
            except:
                text = 'Введите цифрами...'
                reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}




        #сценарий для плановой периодической траты
        elif command == 'Каждый месяц':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'Напишите, что за трата? я буду напоминать Вам о ней каждый месяц.'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2->2->1
        elif state_info_1 == 'Каждый месяц' and state_info_2 is None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
            text = 'ОК! в какой день месяца нужно делать эту трату? 1 - 28'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2->2->1->1
        elif state_info_1 == 'Каждый месяц' and state_info_3 is None:

            error = 0
            try:
                date_day = int(command)
                if date_day > 28:
                    error = 1
            except:
                date_day = 'unknown'
                error = 1

            if error == 1:
                text = 'Ну цифру напиши от 1 до 28'   
                reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
            else:

                r = psql_methods.insert_state_info(chat_id = chat_id , state_info = date_day , state_id = 3)
                text = 'Записал! К какому типу трат относится?'

                reply_markup = {'keyboard': keyboard_expense, 'resize_keyboard': True, 'one_time_keyboard': False}
        #1->1->2->2->1->1->1
        elif state_info_1 == 'Каждый месяц' and state_info_4 is None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 4)
            text = 'ОК! Введите сумму, которую необходимо тратить.'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->2->2->1->1->1->1
        elif state_info_1 == 'Каждый месяц' and state_info_4 is not None:
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 5)
            command = command.replace(',','.')
            try:
                summa = round(float(command),2)
                r = psql_methods.add_transaction_plan_month(chat_id = chat_id , summa = summa , dict_user_data = dict_user_data)
                
                if r == 200:
                    text = 'Операция добавлена! Я буду напоминать Вам о ней, поручитесь на меня!'
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                    reply_markup = reply_markup_main
                if r == 400:
                    text = 'Ведутся какие-то работы... Повторите позже...'
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')

                    reply_markup = reply_markup_main
            except:
                traceback.print_exc()
                text = 'Введите цифрами...'
                reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}



    #сценарий для работы с Траты план - список
    #1->1->3->
    elif last_state == 'Траты план - список':
        #1->1->3->1
        if command == 'Добавить':
            #переходим на сценарий 1->1->2
            r = psql_methods.last_state(chat_id,'Траты план - добавить')
            text = 'Это разовая трата или повторяется каждый месяц?'
            reply_markup = {'keyboard': [['Разовая'],['Каждый месяц']], 'resize_keyboard': True, 'one_time_keyboard': False}
        #1->1->3->2
        if command == 'Удалить':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'Ладушки-аладушки! Напишите номер плановой операции, которую нужно удалить, все сделаю!'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->3->2->1
        elif state_info_1 == 'Удалить' and state_info_2 is None:
            try:
                delete_num = int(command)
                r = psql_methods.delete_transaction_plan(chat_id, user_id ,delete_num)
                text = r['text']
                reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
                r = psql_methods.clear_state(chat_id = chat_id)
                r = psql_methods.last_state(chat_id,'/main')

            except:
                traceback.print_exc()
                text = 'мммм, чего то не пойму... Введите существующий номер плановой операции, указанной в списке'
                reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->3->3
        if command == 'Изменить':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'Оки-доки! Напишите номер плановой операции, по которой нужно изменить дату!'
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->3->3->1
        elif state_info_1 == 'Изменить' and state_info_2 is None:
            try:
                change_num = int(command)
                r = psql_methods.change_transaction_plan_1(chat_id, user_id ,change_num)
                transaction_type = r['system_message']
                text = r['text']
                reply_markup = reply_markup_main if r['reply_markup'] is None else r['reply_markup']
                if r['system_message'] != 'No report':
                    r = psql_methods.insert_state_info(chat_id = chat_id , state_info = change_num , state_id = 2)
                    r = psql_methods.insert_state_info(chat_id = chat_id , state_info = transaction_type , state_id = 3)
            except:
                traceback.print_exc()
                text = 'Блин, ну нет такого номера... Введите существующий номер плановой операции, указанной в списке'
                reply_markup =  {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        #1->1->3->3->2
        elif state_info_1 == 'Изменить' and state_info_3 is not None:
            if state_info_3 == 'once':
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
                        r = psql_methods.change_transaction_plan_2(chat_id = chat_id, user_id = user_id , change_num = state_info_2 , type = state_info_3 , date_plan = date_plan)
                        text = 'Перенесено на ' + command + ' хозяин!'
                        reply_markup = reply_markup_main
                        r = psql_methods.clear_state(chat_id = chat_id)
                        r = psql_methods.last_state(chat_id,'/main')
            elif state_info_3 == 'monthly':
                date_plan = int(command)
                if date_plan > 28:
                    text = 'оу оу, Дата не влазит, введите от 1 до 28'   
                    reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
                else:
                    r = psql_methods.change_transaction_plan_2(chat_id = chat_id, user_id = user_id , change_num = state_info_2 , type = state_info_3 , date_plan = date_plan)
                    text = 'Перенесено на ' + command + ' хозяин!'
                    reply_markup = reply_markup_main
                    r = psql_methods.clear_state(chat_id = chat_id)
                    r = psql_methods.last_state(chat_id,'/main')



    return text , reply_markup