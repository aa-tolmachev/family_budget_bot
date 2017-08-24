
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
	dbname = 'dbr3jigs1op5oo'
	port = '5432'
	user = 'muwrkppfuyldmk'
	host = 'ec2-54-227-252-202.compute-1.amazonaws.com'
	password = '4c4eabfcaf92f7289ccfc1a314d04a3c3806db72b1bf12fd5f0f40c410b14355'

	PSQL_heroku_keys = {'dbname' : dbname
						, 'port' : port
						, 'user' : user
						, 'host' : host
						, 'password' : password
						}

	return PSQL_heroku_keys

