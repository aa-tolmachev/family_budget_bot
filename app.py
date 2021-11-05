"""Flask App Project."""

from flask import Flask, jsonify
app = Flask(__name__)


# тестовый вывод
@app.route("/")  
def hello():
    return "Hello World!"


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0' , threaded=True)
