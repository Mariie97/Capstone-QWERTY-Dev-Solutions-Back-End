from flask import Flask, jsonify, request
from controllers.main_controller import Controller
from flask_cors import CORS

from controllers.users_controller import UserController
from utilities import validate_user_info

app = Flask(__name__)

CORS(app)


@app.route('/api/users', methods=['POST', 'GET'])
def user_register():
    if request.method == 'POST':
        data = request.json
        error_msg = validate_user_info(data)
        if error_msg is None:
            return UserController().create_user(data)
        else:
            return jsonify(error_msg), 400
    else:
        #Todo: Return a list with all users
        return jsonify('Ok')


@app.route('/index')
def index():
    return Controller().get_message()

@app.route('/api/user_info', methods=['GET'])
def user_info():
    data = request.json
    return UserController().get_user_info(data)

if __name__=='__main__':
    app.run(debug=True)