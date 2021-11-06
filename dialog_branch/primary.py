from methods import psql_methods
from methods.emoji import emoji
from methods import telegram_bot_methods

from dicts import meta_info



#список доступных интеграций
def integrations(chat_id = None, command = None):
    r = psql_methods.last_state(chat_id,command)
    text = 'Сейчас у нас появилась интеграция с ToDoist ола-ла!!!' + emoji('фанфары') + emoji('фанфары')+ '\n'
    text += 'Удобство - я автоматически буду проверять ToDoist - напоминать тебе в удобное время, планировать задачи в течение дня, помогать приоритезировать. \n\n'

    text += 'Для интеграции нужно зарегистрировать свой токен \n'
    text += 'Заходи по ссылке и авторизуйся - https://todoist.com/app/today \n'
    text += 'скрин 1 - сверху справа зайди в интеграции \n'
    text += 'скрин 2 - в разделе интеграции найди API token - его нужно скопировать и отправить мне (как позже)\n'

    full_path = './images/integration_todoist/todoist_1.png'
    send_result = telegram_bot_methods.send_photo(chat_id = chat_id, photo_path = photo_path)
    full_path = './images/integration_todoist/todoist_2.png'
    send_result = telegram_bot_methods.send_photo(chat_id = chat_id, photo_path = photo_path)

    return text
    


#справочная информация
def start_help(chat_id = None, command = None):
    r = psql_methods.last_state(chat_id,command)
    text = 'Привет!' +  emoji('фанфары') + '\n'
    text += 'Что я понимаю: \n'
    text += 'Кошелек - работа с кошельком, формирование фактических и плановых трат \n'
    text += 'Дела - запланированный перечень задач, планы, напоминание и тому подобное \n'
    text += 'Отчеты - различные отчеты с интересной информацией \n'
    text += 'Инвестиции - информация по курсам валют, личным вкладам, инвестиционным портфелям \n'
    text += "Если что-то пошло не так - напиши 'меню' и ты вернешься на главное меню\n"

    return text


#возврат в главное меню
def menu(chat_id=None , command=None):
    r = psql_methods.last_state(chat_id,command)
    r = psql_methods.clear_state(chat_id = chat_id)
    text = 'Окей!' + emoji('thumbs_up') + ' Что хотим сделать?'

    return text


#основная функция определения нужных движений далее
def main(command = None , chat_id = None , json_update = None, dict_user_data = None):


    #список первоочередных команд из любой точки
    if 'help' in command:
        text = start_help(chat_id = chat_id , command = command)
        reply_markup = meta_info.reply_markup_main

    #список доступных интеграций
    elif 'integrations' in command:
        text = integrations(chat_id = chat_id , command = command)
        reply_markup = meta_info.reply_markup_main

    elif 'меню' in command:
        text = menu(chat_id = chat_id , command = command)
        reply_markup = meta_info.reply_markup_main

    return text , reply_markup



