import re

from methods import psql_methods

from dialog_branch import *
import dialog_branch as dibr

from dicts import meta_info


#определяем мета направление, предопределяющее все дальнейшие последовательныые движения
def meta(chat_id = None , command = None ,dict_user_data= None):

    meta_path = 'unknown'

    last_state = dict_user_data['last_state']
    state_info_1 = dict_user_data['state_info_1']
    state_info_2 = dict_user_data['state_info_2']
    state_info_3 = dict_user_data['state_info_3']
    state_info_4 = dict_user_data['state_info_4']
    state_info_5 = dict_user_data['state_info_5']
    user_id = dict_user_data['user_id']
    personal_wallet_id = dict_user_data['personal_wallet_id']


    #массивы значений комманд
    primary_commands = ['help' , 'меню']
    primary_commands = "(.*" + ".*)|(.*".join(primary_commands) + ".*)"

    start_commands = ['start' , 'Создать кошелек' ]
    start_commands = "(.*" + ".*)|(.*".join(start_commands) + ".*)"

    #массивы значений последних состояний
    wallet_last_states = ['Кошелек', 'Траты факт - добавить', 'Траты план - добавить', 'Траты план - список']
    report_last_states = ['Отчеты']
    invest_last_states = []
    task_last_states = ['Дела']

    #определяем первоочередные команды из любого места
    if re.match(primary_commands, command):
        meta_path = 'primary'

    #определяем стартовые команды команды из любого места
    elif re.match(start_commands, command):
        meta_path = 'start'

    #определяем кошелек
    elif 'Кошелек' in command or last_state in wallet_last_states:
        meta_path = 'wallet'
    
    #определяем отчеты
    elif 'Отчеты' in command or last_state in report_last_states:
        meta_path = 'report'

    #определяем инвестиции
    elif 'Инвестиции' in command or last_state in invest_last_states:
        meta_path = 'invest'

    #определяем дела
    elif 'Дела' in command or last_state in task_last_states:
        meta_path = 'task'

    return meta_path



#направляем на нужную ветку диалога
def make_dialog_branch(meta_path= None, chat_id= None, command= None , dict_user_data= None , json_update = None):

    #-> хз што это
    text = 'Неизвестная команда, для списка команд выбирите команду /help'
    reply_markup = meta_info.reply_markup_main


    #смотрим по веткам разговора
    if meta_path == 'start':
        text , reply_markup = dibr.start.main(command = command , chat_id = chat_id , json_update = json_update , dict_user_data =dict_user_data)
    elif meta_path == 'primary':
        text , reply_markup = dibr.primary.main(command = command , chat_id = chat_id , json_update = json_update , dict_user_data = dict_user_data)
    elif meta_path == 'wallet':
        text , reply_markup = dibr.wallet.main(command = command , chat_id = chat_id , json_update = json_update, dict_user_data = dict_user_data)
    elif meta_path == 'report':
        text , reply_markup = dibr.report.main(command = command , chat_id = chat_id , json_update = json_update, dict_user_data = dict_user_data)
    elif meta_path == 'invest':
        text , reply_markup = dibr.invest.main(command = command , chat_id = chat_id , json_update = json_update, dict_user_data = dict_user_data)
    elif meta_path == 'task':
        text , reply_markup = dibr.task.main(command = command , chat_id = chat_id , json_update = json_update, dict_user_data = dict_user_data)

    return text , reply_markup









