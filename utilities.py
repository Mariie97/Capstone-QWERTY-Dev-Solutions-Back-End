import re

account_type = {
    'student': '1',
    'client': '2',
    'superuser': '3',
}

STATUS_CODE = {
    'created': 200,
    'not_found': 404,
    'bad_request': 400,
    'unauthorized': 400,
    'ok': 200,
}


def validate_email(email):
    return re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b$', email)


def validate_user_info(data):
    expected_params = ['first_name', 'last_name', 'email', 'password', 'type', 'q_type1', 'q_type2', 'ans1', 'ans2']
    for param in expected_params:
        if param not in data:
            concat_list = ', '.join(expected_params)
            return 'The following parameters are required: ' + concat_list

    if data['type'] == account_type['student'] and re.match(r'^.+@upr\.edu$', data['email']) is None:
        return 'A upr email is needed to register as student'

    if validate_email(data['email']) is None:
        return 'Email provided is not valid'

    return None


def validate_login_data(data):
    expected_params = ['email', 'password']
    for param in expected_params:
        if param not in data:
            concat_list = ', '.join(expected_params)
            return 'The following parameters are required: ' + concat_list

    if validate_email(data['email']) is None:
        return 'Email provided is not valid'

    return None