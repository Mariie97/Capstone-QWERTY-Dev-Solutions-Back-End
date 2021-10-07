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
            'type': data[4]
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
            'user_id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'password': data[3],
            'email': data[4],
            'image': data[5],
            'type': data[6],
            'about': data[7],
            'cancellations': data[8],
            'address_id': data[9],
        }

    def get_user_info(self, userid):
        try:
            user = self.dao.get_user_info(userid)
            return jsonify(self.get_user_info_dict(user)), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']
