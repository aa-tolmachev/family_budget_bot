from methods import psql_methods
from methods.emoji import emoji

from dicts import meta_info



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
def main(command = None , chat_id = None , json_update = None):


    #список первоочередных команд из любой точки
    if 'help' in command:
        text = start_help(chat_id = chat_id , command = command)
        reply_markup = meta_info.reply_markup_main

    elif 'меню' in command:
        text = menu(chat_id = chat_id , command = command)
        reply_markup = meta_info.reply_markup_main

    return text , reply_markup


