from methods import psql_methods
from methods.emoji import emoji
from methods import telegram_bot_methods
from dicts import meta_info

from methods import reply

def main(command = None , chat_id = None, dict_user_data = None,json_update = None):

    text = 'Ну чего тебе надо от меня вообще не знаю...'
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


    #5 - Интеграции
    if 'integrations' in command:
        r = psql_methods.last_state(chat_id,command)
        text = 'Здесь хранятся все возможные интеграции с внешними сервисами' + '\n'
        text += 'здесь можно подключить или впоследствии отключить интеграции,' + '\n'
        text += 'жмакай по интересным кнопулькам и смотри возможные интеграции и зачем они нужны.' + emoji('карандаш')

        reply_markup = {'keyboard': [['ToDoist'],['меню']], 'resize_keyboard': True, 'one_time_keyboard': False}

    #5-> начало работы с интеграциями
    elif last_state == '/integrations':
        #5->1 выбрал ToDoist
        if command == 'ToDoist':
            r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 1)
            text = 'Интеграция с ToDoist ола-ла!!!' + emoji('фанфары') + emoji('фанфары')+ '\n'
            text += 'Удобство - я автоматически буду проверять ToDoist - напоминать тебе в удобное время, планировать задачи в течение дня, помогать приоритезировать. \n\n'

            text += 'Для интеграции нужно зарегистрировать свой токен \n'
            text += 'Заходи по ссылке и авторизуйся - https://todoist.com/app/today \n'
            text += 'скрин 1 - сверху справа зайди в интеграции \n'
            text += 'скрин 2 - в разделе интеграции найди API token - его нужно скопировать и отправить сюда сообщением. Если нужно обновить - также просто напиши его\n'

            full_path = './images/integration_todoist/todoist_1.png'
            send_result = telegram_bot_methods.send_photo(chat_id = chat_id, photo_path = full_path, photo_delete = False)
            full_path = './images/integration_todoist/todoist_2.png'
            send_result = telegram_bot_methods.send_photo(chat_id = chat_id, photo_path = full_path, photo_delete = False)
            reply_markup = {'keyboard': [['меню']], 'resize_keyboard': True, 'one_time_keyboard': True}
        


        #5->1->1 записываем токен для интеграции ToDoist
        elif state_info_1 == 'ToDoist' and state_info_2 is None:
            #r = psql_methods.insert_state_info(chat_id = chat_id , state_info = command , state_id = 2)
            r = psql_methods.add_external_app(chat_id = chat_id  , external_app = 'ToDoist' , external_app_token = command , dict_user_data = dict_user_data)
            text = 'Мой владыка задач ToDoist - токен записан (или обновлен если существовал)'
            reply_markup = reply_markup_main
            r = psql_methods.clear_state(chat_id = chat_id)
            r = psql_methods.last_state(chat_id,'/main')



    return text , reply_markup