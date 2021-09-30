from flask import Flask, jsonify, request
from controllers.main_controller import Controller
from flask_cors import CORS

from controllers.users_controller import UserController

app = Flask(__name__)

CORS(app)


@app.route('/api/users', methods=['POST', 'GET'])
def user_register():
    if request.method == 'POST':
        data = request.json
        return UserController().create_user(data)
    else:
        #Todo: Return a list with all users
        return jsonify('Ok')


@app.route('/index')
def index():
    return Controller().get_message()


if __name__=='__main__':
    app.run(debug=True)