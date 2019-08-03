from methods import psql_methods
from methods.emoji import emoji

#первое знакомство с пользователем
def welcome(chat_id = None , json_update = None):
    r = psql_methods.new_user(chat_id , json_update)
    text = emoji('фанфары') + 'Добрый день! \n' 
    text += 'Я веду домашний бюджет и напоминаю об операциях в течение месяца. \n'
    text += 'Я развиваюсь в свободное время, потом будет интереснее. \n'
    text += 'Сначала заведите свой кошелек и забудьте о том, чтобы держать бюджет семьи в голове!' + emoji('банкноты')
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
    text += 'Инвестиции - информация по курсам валют, личным вкладам, инвестиционным портфелям \n'
    text += "Если что-то пошло не так - напиши 'меню' и ты вернешься на главное меню\n"

    return text