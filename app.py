from flask import Flask
from flask import request


import family_budget


application = Flask(__name__)  # Change assignment here



@application.route("/")  # Change your route statements
def hello():
    return "Hello World!"





@application.route('/family_budget', methods=['GET', 'POST'])
def app_fb():
    try:
        #json_params = json.loads(request.get_data())

        family_budget.main()
        
        return 'END'
    except:

        return 'ERROR'



#if __name__ == "__main__":
#    application.run()
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')