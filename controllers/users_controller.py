from flask import jsonify
from psycopg2 import IntegrityError

from models.users_dao import UserDao
from utilities import STATUS_CODE


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
            'address_id': data[0],
            'user_id': data[1],
            'first_name': data[2],
            'last_name': data[3],
            'password': data[4],
            'email': data[5],
            'image': data[6],
            'type': data[7],
            'about': data[8],
            'cancellations': data[9],
            'street': data[10],
            'city': data[11],
            'zipcode': data[12],
            'rate': data[13]
        }

    def get_all_users(self, data):
        users = self.dao.get_all_users(data)
        result_list = []
        for row in users:
            obj = {
                'first_name': row[0],
                'last_name': row[1],
                'email': row[2],
            }
            result_list.append(obj)
        return jsonify(result_list), STATUS_CODE['ok']

    def clean_data(self, data):
        for param, value in data.items():
            if value == '':
                data[param] = None

    def edit_user(self, user_info):
        try:
            self.clean_data(user_info)
            user = self.dao.edit_user(user_info)
            if user is None:
                return jsonify('There is not user with id={id}'.format(id=user_info['user_id'])), \
                       STATUS_CODE['not_found']
            else:
                return jsonify("User ({id}) edited successfully!".format(id=user_info['user_id'])), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']

    def get_user_info(self, userid):
        try:
            user = self.dao.get_user_info(userid)
            if user is None:
                return jsonify("User not found"), STATUS_CODE['not_found']
            else:
                return jsonify(self.get_user_info_dict(user)), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']
