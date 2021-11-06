
#справочник кодов emoji по названию
def emoji(name = None):
	dict_emoji = {'тучка' : '\U0001F4A8'
			,'руки_аминь' : '\U0001F64F'
			,'руки_вверх' : '\U0001F64C'
			,'коктейль' : '\U0001F379'
			,'фанфары' : '\U0001F389'
			,'банкноты' : '\U0001F4B5'
			,'время' : '\U0001F55D'
			,'смайл_прищур' : '\U0001F60F'
			,'смайл_спокойствие'  : '\U0001F60C'
			,'смайл_подмигнуть'  : '\U0001F609'
			,'карандаш'  : '\U0000270F'
			,'банк'  : '\U0001F3E6'
			,'vhand' : '\U0000270C'
			,'less' : '\U0001F44C'
			,'more' : '\U0001F53A'
			,'thumbs_up' : '\U0001F44D'
            ,'фиолетовый дьяволенок' : '\U0001F608'
            ,'пар из ноздрей' : '\U0001F624'
	}

	try:
		emoji = dict_emoji[name]
	except:
		emoji = ''

	return emoji


    