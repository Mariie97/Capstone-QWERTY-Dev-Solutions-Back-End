from flask import Flask, jsonify
from controllers.mainController import Controller
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

@app.route('/index')
def index():
    return Controller().get_message()

if __name__=='__main__':
    app.run(debug=True)