from datetime import timedelta, datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, \
    unset_jwt_cookies, get_jwt

from config.config import JWT_SECRET_KEY, JWT_TOKEN_LOCATION, JWT_ACCESS_TOKEN_EXPIRES_DAYS, AWS_UPLOAD_FOLDER, \
    SECRET_KEY
from controllers.chat_controllers import ChatController
from controllers.jobs_controller import JobController
from controllers.users_controller import UserController
from utilities import validate_user_info, validate_login_data, STATUS_CODE, ADMIN_ACCOUNT, \
    CLIENT_ACCOUNT, STUDENT_ACCOUNT, validate_password_info, validate_email, upload_image_aws, validate_profile_data, \
    validate_assign_job_data, validate_job_rate, validate_job_status, validate_create_job, validate_message_data, \
    format_price, validate_job_requests, get_query_params

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
        data.update({'admin': 'admin' in request.args})
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


@app.route('/api/users/', methods=['GET'])
@jwt_required()
def get_users():
    data = {'deleted': False}

    if 'account_type' in request.args:
        if int(request.args['account_type']) not in [STUDENT_ACCOUNT, CLIENT_ACCOUNT, ADMIN_ACCOUNT]:
            return jsonify('Valid type: %s, %s, and %s' % (STUDENT_ACCOUNT, CLIENT_ACCOUNT, ADMIN_ACCOUNT)), \
                   STATUS_CODE['bad_request']

        data.update({'type': request.args['account_type']})

    if 'deleted' in request.args:
        data.update({'deleted': True})

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


@app.route('/api/request_job', methods=['POST'])
@jwt_required()
def add_job_request():
    error_msg = validate_job_requests(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    return JobController().add_job_request(data)


@app.route('/api/cancel_request', methods=['PUT'])
@jwt_required()
def cancel_job_request():
    error_msg = validate_job_requests(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    return JobController().cancel_job_request(data)


@app.route('/api/job_requests/<int:job_id>', methods=['GET'])
@jwt_required()
def job_requests_list(job_id):
    data = {'job_id': job_id}
    if len(request.args) > 0:
        get_query_params(request, data)
    return JobController().get_requests_list(data)


@app.route('/api/student_requests/<int:student_id>', methods=['GET'])
@jwt_required()
def jobs_requested_by_student(student_id):
    data = {'student_id': student_id}
    if len(request.args) > 0:
        get_query_params(request, data)
    return JobController().get_student_job_requested(data)


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


@app.route('/api/user_info/<int:user_id>', methods=['GET'])
@jwt_required()
def user_info(user_id):
    data = {'user_id': user_id}
    return UserController().get_user_info(data)


@app.route('/api/job_details/<int:job_id>', methods=['GET'])
@jwt_required()
def job_info(job_id):
    data = {'job_id': job_id}
    return JobController().get_job_details(data)


@app.route('/api/jobs_list/<int:status>', methods=['GET'])
@jwt_required()
def jobs_list(status):
    data = {'status': status}
    if len(request.args) > 0:
        get_query_params(request, data)
    return JobController().get_job_list_by_status(data)


@app.route('/api/create_job', methods=['POST'])
@jwt_required()
def create_job():
    error_msg = validate_create_job(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    data.update({
        'price': format_price(str(data['price']), True)
    })

    return JobController().create_job(data)


@app.route('/api/delete_user/<int:user_id>', methods=['POST'])
@jwt_required()
def delete_user(user_id):
    data = {'user_id': user_id}
    return UserController().delete_user(data)


@app.route('/api/job_status/<int:job_id>', methods=['PUT'])
@jwt_required()
def change_job_status(job_id):
    error_msg = validate_job_status(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    data.update({
        'job_id': job_id
    })
    return JobController().set_job_status(data)


@app.route('/api/rate_job/<int:job_id>', methods=['POST'])
@jwt_required()
def rate_job(job_id):
    error_msg = validate_job_rate(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    data.update({
        'job_id': job_id
    })

    return JobController().add_job_ratings(data)


@app.route('/api/add_message', methods=['POST'])
@jwt_required()
def add_message():
    error_msg = validate_message_data(request.json)
    if error_msg is not None:
        return jsonify(error_msg), STATUS_CODE['bad_request']

    data = request.json
    return ChatController().create_message(data)


@app.route('/api/retrieve_messages/<int:job_id>', methods=['GET'])
@jwt_required()
def retrieve_chat_messages(job_id):
    if 'user_id' not in request.args:
        return jsonify("Need to specify the user_id"), STATUS_CODE['bad_request']

    data = {
        'job_id': job_id,
        'user_id': request.args['user_id']
    }
    return ChatController().get_job_messages(data)


@app.route('/api/pdf/<int:job_id>', methods=['GET'])
def agreement_contract(job_id):
    if 'student_id' not in request.args or 'owner_id' not in request.args:
        return jsonify('student_id and owner_id needs to be specified'), STATUS_CODE['bad_request']

    data = {
        'job_id': job_id,
        'student_id': int(request.args['student_id']),
        'owner_id': int(request.args['owner_id']),
    }
    return JobController().get_contract(data)


if __name__ == '__main__':
    app.run(debug=True)
