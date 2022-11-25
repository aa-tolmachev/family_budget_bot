from methods import psql_methods
from methods.emoji import emoji

from dicts import meta_info



#первое знакомство с пользователем
def welcome(chat_id = None , json_update = None):
    r = psql_methods.new_user(chat_id , json_update)
    text = emoji('фанфары') + 'Добрый день! \n' 
    text += 'Я веду домашний бюджет и напоминаю об делах и плановых тратах в течение месяца. \n'
    text += 'Я развиваюсь в свободное время, потом будет интереснее. \n'

    text += 'Например - вы можете ннаписать Дело и в нужную дату я буду вам напоминать о нем, чтобы не забыли \n'
    text += 'или вы можете ннаписать Плановую трату и за день я буду напоминать о ней. \n\n'

    text += 'Сначала заведите свой кошелек и начните получать удовольствие!' + emoji('банкноты')
    reply_markup = {'keyboard': [['Создать кошелек']], 'resize_keyboard': True, 'one_time_keyboard': False}

    return text , reply_markup


#справочная информация
def start_help(chat_id = None, command = None):
    r = psql_methods.last_state(chat_id,command)
    text = 'Привет!' +  emoji('фанфары') + '\n'
    text += 'Что я понимаю: \n'
    text += 'Кошелек - работа с кошельком, формирование фактических и плановых трат \n'
    text += 'Дела - запланированный перечень задач, планы, напоминание и тому подобное \n'
    text += 'Отчеты - различные отчеты с интересной информацией \n'
    text += "Если что-то пошло не так - напиши 'меню' и ты вернешься на главное меню\n"

    return text

#создание кошелька для пользователя
def wallet_create(chat_id = None , command = None):
    r = psql_methods.last_state(chat_id,command)
    r = psql_methods.make_wallet(chat_id)
    text = r['text']

    return text

#возврат в главное меню
def menu(chat_id=None , command=None):
    r = psql_methods.last_state(chat_id,command)
    r = psql_methods.clear_state(chat_id = chat_id)
    text = 'Окей!' + emoji('thumbs_up') + ' Что хотим сделать?'

    return text


#основная функция определения нужных движений далее
def main(command = None , chat_id = None , json_update = None, dict_user_data = None):


    #список стартовых команд 
    if 'start' in command:
        text , reply_markup = welcome(chat_id = chat_id , json_update = json_update)

    elif 'Создать кошелек' in command:
        text = wallet_create(chat_id = chat_id , command = command)
        reply_markup = meta_info.reply_markup_main


    return text , reply_markup


