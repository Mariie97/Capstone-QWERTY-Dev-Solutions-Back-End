from datetime import timedelta, datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, \
    unset_jwt_cookies, get_jwt

from controllers.users_controller import UserController
from utilities import validate_user_info, validate_login_data, STATUS_CODE, SUPERUSER_ACCOUNT, CLIENT_ACCOUNT, \
    STUDENT_ACCOUNT

app = Flask(__name__)

CORS(app)
app.config['SECRET_KEY'] = '4451ae0bc6ad1a0004f0d48f3ed7f36f41c1a438c1289715'

jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = '8c01266947a861311f965636744d880bd588a2edd30aa3e7'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)


@app.after_request
def refresh_expiring_tokens(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@app.route("/api/login", methods=["POST"])
def authenticate():
    data = request.json
    error_msg = validate_login_data(data)
    if error_msg is None:
        response, status_code = UserController().login_user(data)
        if status_code == STATUS_CODE['ok']:
            access_token = create_access_token(identity=data['email'])
            set_access_cookies(response, access_token)
        return response, status_code
    else:
        return jsonify(error_msg), STATUS_CODE['bad_request']


@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify('Logout successful!')
    unset_jwt_cookies(response)
    return response


@app.route('/api/create_user', methods=['POST'])
def create_user():
    data = request.json
    error_msg = validate_user_info(data)
    if error_msg is None:
        return UserController().create_user(data)
    else:
        return jsonify(error_msg), STATUS_CODE['bad_request']


@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    if request.json is None or 'type' not in request.json:
        return jsonify('The following parameter is required: type'), STATUS_CODE['bad_request']

    if request.json['type'] not in [STUDENT_ACCOUNT, CLIENT_ACCOUNT, SUPERUSER_ACCOUNT]:
        return jsonify('Valid type: %s, %s, and %s' % (STUDENT_ACCOUNT, CLIENT_ACCOUNT, SUPERUSER_ACCOUNT)), \
               STATUS_CODE['bad_request']

    data = request.json
    return UserController().get_all_users(data)


if __name__ == '__main__':
    app.run(debug=True)
