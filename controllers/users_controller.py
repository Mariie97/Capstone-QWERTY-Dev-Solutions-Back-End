from flask import jsonify

from models.users_dao import UserDao
from utilities import STATUS_CODE, generate_profile_pic_url


class UserController:

    def __init__(self):
        self.dao = UserDao()

    @staticmethod
    def build_attr_dict(data):
        return {
            'user_id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'email': data[3],
            'type': data[4],
        }

    @staticmethod
    def security_questions_dict(data):
        return {
            'question_1': data[0],
            'question_2': data[1],
            'answer_1': data[2],
            'answer_2': data[3]
        }

    @staticmethod
    def clean_data(data):
        for param, value in data.items():
            if value == '':
                data[param] = None

    def create_user(self, user_info):
        user_exist, error_msg = UserDao().verify_user_exist(user_info)
        if user_exist:
            return jsonify('User already registered (email={email})'.format(email=user_info['email'])), \
                   STATUS_CODE['conflict']

        user, error_msg = self.dao.create_user(user_info)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        return jsonify(self.build_attr_dict(user)), STATUS_CODE['created']

    def login_user(self, credentials):
        user, error_msg = self.dao.login_user(credentials)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if user is None:
            return jsonify("Invalid credentials"), STATUS_CODE['unauthorized']

        user_info = {
            'user_id': user[0],
            'type': user[1],
        }
        return jsonify(user_info), STATUS_CODE['ok']

    @staticmethod
    def get_user_info_dict(data):
        return {
            'first_name': data[0],
            'last_name': data[1],
            'email': data[2],
            'image': generate_profile_pic_url(data[3]) if data[3] is not None else None,
            'about': data[4],
            'cancellations': data[5],
            'type': data[6],
            'street': data[8] if data[8] is not None else None,
            'city': data[9] if data[9] is not None else None,
            'zipcode': data[10] if data[10] is not None else None,
            'rate': data[11],
        }

    def get_all_users(self, data):
        users, error_msg = self.dao.get_all_users(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if users is None:
            return jsonify('No users found'), STATUS_CODE['not_found']

        result_list = []
        for row in users:
            obj = {
                'user_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'type': row[4],
            }
            result_list.append(obj)
        return jsonify(result_list), STATUS_CODE['ok']

    def retrieve_questions(self, user_email):
        user, error_msg = self.dao.retrieve_questions(user_email)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if user is None:
            return jsonify("User not found"), STATUS_CODE['not_found']

        return jsonify(self.security_questions_dict(user)), STATUS_CODE['ok']

    def edit_user(self, user_info):
        self.clean_data(user_info)
        user, error_msg = self.dao.edit_user(user_info)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if user is None:
            return jsonify('There is not user with id={id}'.format(id=user_info['user_id'])), \
                   STATUS_CODE['not_found']

        return jsonify("User ({id}) edited successfully!".format(id=user_info['user_id'])), STATUS_CODE['ok']

    def change_password(self, user_email):
        user, error_msg = self.dao.change_password(user_email)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if user is None:
            return jsonify("User not found"), STATUS_CODE['not_found']

        return jsonify({'email': user[0], 'password': user[1]}), STATUS_CODE['ok']

    def get_user_info(self, userid):
        user, error_msg = self.dao.get_user_info(userid)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if user is None:
            return jsonify("User not found"), STATUS_CODE['not_found']

        return jsonify(self.get_user_info_dict(user)), STATUS_CODE['ok']

    def delete_user(self, data):
        deleted, error_msg = self.dao.delete_user(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if not deleted:
            return jsonify("User with id={id} not found".format(id=data['user_id']))

        return jsonify("User deleted successfully!"), STATUS_CODE['ok']

