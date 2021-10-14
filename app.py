from datetime import timedelta, datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, \
    unset_jwt_cookies, get_jwt

from config.config import JWT_SECRET_KEY, JWT_TOKEN_LOCATION, JWT_ACCESS_TOKEN_EXPIRES_DAYS, AWS_UPLOAD_FOLDER, \
    SECRET_KEY
from controllers.jobs_controller import JobController
from controllers.users_controller import UserController
from utilities import SUPERUSER_ACCOUNT, CLIENT_ACCOUNT, STUDENT_ACCOUNT, validate_assign_job_data, \
    validate_password_info, validate_email, validate_user_info, validate_login_data, STATUS_CODE, upload_image_aws, \
from utilities import validate_user_info, validate_login_data, STATUS_CODE, SUPERUSER_ACCOUNT, CLIENT_ACCOUNT, \
    STUDENT_ACCOUNT, validate_email, validate_password_info
from utilities import validate_user_info, validate_login_data, STATUS_CODE, upload_image_aws, generate_profile_pic_url, \
    validate_profile_data

app = Flask(__name__)

CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = AWS_UPLOAD_FOLDER

jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=JWT_ACCESS_TOKEN_EXPIRES_DAYS)


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


@app.route('/api/edit_user/<int:user_id>', methods=['PUT'])
@jwt_required()
def user_edit(user_id):
    data = request.form.copy()
    error_msg = validate_profile_data(data)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data.update({
        'user_id': user_id,
        'image_key': None
    })

    if 'image' in request.files and request.files['image'].content_type is not None:
        image = request.files['image']
        data['image_key'] = upload_image_aws(data['user_id'], image)
    return UserController().edit_user(data)


@app.route('/api/change_password', methods=['GET', 'PUT'])
def change_password():
    if request.method == 'GET':
        if 'email' not in request.args:
            return jsonify("Email not specify"), STATUS_CODE['bad_request']

        data = request.args
        is_valid = validate_email(data['email'])
        if is_valid is not None:
            return UserController().retrieve_questions(data)
        else:
            return jsonify('Email provided is not valid'), STATUS_CODE['bad_request']
    else:
        data = request.json
        error_msg = validate_password_info(data)
        if error_msg is None:
            return UserController().change_password(data)
        else:
            return jsonify(error_msg), STATUS_CODE['bad_request']


@app.route('/api/job_requests', methods=['GET'])
@jwt_required()
def job_requests_list():
    if request.json is None or 'job_id' not in request.json:
        return jsonify('The following parameter is required: job_id'), STATUS_CODE['bad_request']

    data = request.json
    return JobController().get_requests_list(data)


@app.route('/api/student_requests', methods=['GET'])
@jwt_required()
def student_requests_list():
    if request.json is None or 'student_id' not in request.json:
        return jsonify('The following parameter is required: student_id'), STATUS_CODE['bad_request']

    data = request.json
    return JobController().get_student_requests_list(data)


@app.route('/api/assign_job', methods=['PUT'])
@jwt_required()
def assign_job_worker():
    error_msg = validate_assign_job_data(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    return JobController().set_job_worker(data)


@app.route('/api/is_valid_token', methods=['GET'])
@jwt_required()
def verify_is_auth():
    return jsonify('User is authenticated!'), STATUS_CODE['ok']


if __name__ == '__main__':
    app.run(debug=True)
