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


@app.route('/api/edit', methods=['PUT'])
def user_edit():
    if request.method == 'PUT':
        data = request.json
        return UserController().edit_user(data)
    else:
        return jsonify('ok')


@app.route('/index')
def index():
    return Controller().get_message()


if __name__=='__main__':
    app.run(debug=True)