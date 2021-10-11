import re

STUDENT_ACCOUNT = '1'
CLIENT_ACCOUNT = '2'
SUPERUSER_ACCOUNT = '3'

account_type = {
    'student': '1',
    'client': '2',
    'superuser': '3',
}

STATUS_CODE = {
    'ok': 200,
    'created': 201,
    'bad_request': 400,
    'unauthorized': 401,
    'not_found': 404,
}


def validate_password_info(req_json):
    expected_params = ['password', 'email']
    if req_json is None:
        return 'The following parameters are required: ' + concat_list_to_string(expected_params)

    for param in expected_params:
        if param not in req_json:
            return 'The following parameters are required: ' + concat_list_to_string(expected_params)
    if validate_email(req_json['email']) is None:
        return 'Email provided is not valid'
    return None


def validate_email(email):
    return re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b$', email)


def concat_list_to_string(list):
    return ', '.join(list)


def validate_user_info(data):
    expected_params = ['first_name', 'last_name', 'email', 'password', 'type', 'q_type1', 'q_type2', 'ans1', 'ans2']
    if data is None:
        return 'The following parameters are required: ' + concat_list_to_string(expected_params)

    for param in expected_params:
        if param not in data:
            return 'The following parameters are required: ' + concat_list_to_string(expected_params)

    if data['type'] == account_type['student'] and re.match(r'^.+@upr\.edu$', data['email']) is None:
        return 'A upr email is needed to register as student'

    if validate_email(data['email']) is None:
        return 'Email provided is not valid'

    return None


def validate_login_data(data):
    expected_params = ['email', 'password']
    if data is None:
        return 'The following parameters are required: ' + concat_list_to_string(expected_params)

    for param in expected_params:
        if param not in data:
            return 'The following parameters are required: ' + concat_list_to_string(expected_params)

    if validate_email(data['email']) is None:
        return 'Email provided is not valid'

    return None
