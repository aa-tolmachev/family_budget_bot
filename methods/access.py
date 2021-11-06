import os


#токен бота family_budget
def token():
    token = os.getenv('TELEGRAM_TOKEN')
    return token

#url телеграма
def api():
	api = 'https://api.telegram.org/bot'
	return api

#Google Maps Geocoding API
def google_maps_api_key():
	google_maps_api_key = 'AIzaSyD0hZtEuzOUmVo4R6qqiXAhTfRICNDv4yY'
	api = 'https://maps.googleapis.com/maps/api/geocode/json?'
	#пример - https://maps.googleapis.com/maps/api/geocode/json?address=пермь+гусарова+14&key=AIzaSyD0hZtEuzOUmVo4R6qqiXAhTfRICNDv4yY
	d_google_maps_api = {'api' : api
						,'google_maps_api_key' : google_maps_api_key}
	return d_google_maps_api

#heroku PSQL
def PSQL_heroku_keys():
	dbname = os.getenv('HEROKU_PSQL_DBNAME')
	port = '5432'
	user = os.getenv('HEROKU_PSQL_USER')
	host = os.getenv('HEROKU_PSQL_HOST')
	password = os.getenv('HEROKU_PSQL_PASS')

	PSQL_heroku_keys = {'dbname' : dbname
						, 'port' : port
						, 'user' : user
						, 'host' : host
						, 'password' : password
						}

	return PSQL_heroku_keys

