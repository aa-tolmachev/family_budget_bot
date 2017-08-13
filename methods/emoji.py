
#справочник кодов emoji по названию
def emoji(name = None):
	dict_emoji = {'тучка' : '\U0001F4A8'
			,'руки_аминь' : '\U0001F64F'
			,'руки_вверх' : '\U0001F64C'
			,'коктейль' : '\U0001F379'
			,'фанфары' : '\U0001F389'
			,'банкноты' : '\U0001F4B5'
			,'время' : '\U0001F55D'
	}

	try:
		emoji = dict_emoji[name]
	except:
		emoji = ''

	return emoji


    