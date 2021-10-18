from flask import jsonify
from psycopg2 import IntegrityError

from models.users_dao import UserDao
from utilities import STATUS_CODE, generate_profile_pic_url


class UserController:

    def __init__(self):
        self.dao = UserDao()

    def build_attr_dict(self, data):
        return {
            'user_id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'email': data[3],
            'type': data[4],
        }

    def security_questions_dict(self, data):
        return {
            'question_1': data[0],
            'question_2': data[1],
            'answer_1': data[2],
            'answer_2': data[3]
        }

    def create_user(self, user_info):
        try:
            user = self.dao.create_user(user_info)
            return jsonify(self.build_attr_dict(user)), STATUS_CODE['created']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']

    def login_user(self, credentials):
        user = self.dao.login_user(credentials)
        if user:
            dict = {
                'user_id': user[0],
                'type': user[1],
            }
            return jsonify(dict), STATUS_CODE['ok']
        else:
            return jsonify("Invalid credentials"), STATUS_CODE['unauthorized']

    def get_user_info_dict(self, data):
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
        users = self.dao.get_all_users(data)
        result_list = []
        for row in users:
            obj = {
                'user_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
            }
            result_list.append(obj)
        return jsonify(result_list), STATUS_CODE['ok']

    def clean_data(self, data):
        for param, value in data.items():
            if value == '':
                data[param] = None

    def retrieve_questions(self, user_email):
        try:
            user = self.dao.retrieve_questions(user_email)
            if user is None:
                return jsonify("User not found"), STATUS_CODE['not_found']
            else:
                return jsonify(self.security_questions_dict(user)), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']

    def edit_user(self, user_info):
        try:
            self.clean_data(user_info)
            user, error_msg = self.dao.edit_user(user_info)
            if user is None:
                return jsonify('There is not user with id={id}'.format(id=user_info['user_id'])), \
                       STATUS_CODE['not_found']
            else:
                return jsonify("User ({id}) edited successfully!".format(id=user_info['user_id'])), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']

    def change_password(self, user_email):
        try:
            user = self.dao.change_password(user_email)
            if user is None:
                return jsonify("User not found"), STATUS_CODE['not_found']
            else:
                return jsonify({'email': user[0], 'password': user[1]}), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']

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

