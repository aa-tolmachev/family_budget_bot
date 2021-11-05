"""Flask App Project."""

from flask import Flask, jsonify
app = Flask(__name__)


# тестовый вывод
@app.route("/")  
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run()