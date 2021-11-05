
#токен бота family_budget
def token():
    token = '382244799:AAFfN3evzGDQaRevpW5xqZ1AEovvdRCWk-0'
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
	dbname = 'd5o1cfs1078sem'
	port = '5432'
	user = 'fmfezriwohjnuk'
	host = 'ec2-34-196-34-142.compute-1.amazonaws.com'
	password = 'e3b8eceda1fbb0847f06c835d9b0ea972bd738a1745e9f570ea3f1c6100734e1'

	PSQL_heroku_keys = {'dbname' : dbname
						, 'port' : port
						, 'user' : user
						, 'host' : host
						, 'password' : password
						}

	return PSQL_heroku_keys

