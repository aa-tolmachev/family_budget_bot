from methods import psql_methods


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


    #массивы значений последних состояний
    wallet_last_states = ['Кошелек', 'Траты факт - добавить', 'Траты план - добавить', 'Траты план - список']
    report_last_states = ['Отчеты']
    invest_last_states = []
    task_last_states = ['Дела']



    #определяем кошелек
    if 'Кошелек' in command or last_state in wallet_last_states:
        meta_path = 'Кошелек'
    
    #определяем отчеты
    elif 'Отчеты' in command or last_state in report_last_states:
        meta_path = 'Отчеты'

    #определяем инвестиции
    elif 'Инвестиции' in command or last_state in invest_last_states:
        meta_path = 'Инвестиции'

    #определяем дела
    elif 'Дела' in command or last_state in task_last_states:
        meta_path = 'Дела'

    return meta_path