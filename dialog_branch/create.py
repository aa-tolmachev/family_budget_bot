from methods import psql_methods


#создание кошелька для пользователя
def wallet_create(chat_id = None , command = None):
    r = psql_methods.last_state(chat_id,command)
    r = psql_methods.make_wallet(chat_id)
    text = r['text']

    return text