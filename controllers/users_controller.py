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

    def retrieve_questions(self, user_email):
        try:
            user = self.dao.retrieve_questions(user_email)
            return jsonify(self.security_questions_dict(user)), STATUS_CODE['ok']
        except IntegrityError as e:
            return jsonify(e.pgerror), STATUS_CODE['bad_request']
