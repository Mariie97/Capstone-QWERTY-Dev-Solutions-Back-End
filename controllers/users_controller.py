from flask import jsonify
from psycopg2 import IntegrityError
#from psycopg2.errors import UniqueViolation

from models.users_dao import UserDao


class UserController:

    def build_attr_dict(self, data):
        return {
            'user_id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'email': data[3],
            'type': data[4],
        }

    def create_user(self, user_info):
        dao = UserDao()
        try:
            user = dao.create_user(user_info)
            return jsonify(self.build_attr_dict(user)), 201
        except IntegrityError as e:
            return jsonify(e.pgerror), 400

    def edit_user_dict(self, data):
        return {
            'user_id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'image': data[3],
            'about': data[4],
            'password': data[5],
            'address_id': data[6],
        }

    def edit_user(self, user_info):
        dao = UserDao()
        try:
            user = dao.edit_user(user_info)
            return jsonify(self.edit_user_dict(user)), 201
        except IntegrityError as e:
            return jsonify(e.pgerror), 400
