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
            'type': data[4]
        }

    def create_user(self, user_info):
        dao = UserDao()
        try:
            user = dao.create_user(user_info)
            return jsonify(self.build_attr_dict(user)), 201
        except IntegrityError as e:
            return jsonify(e.pgerror), 400

    def get_user_info_dict(self, data):
        return {
            'user_id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'email': data[3],
            'type': data[4],
            'password': data[5],
            'image': data[6],
            'about': data[7],
            'cancellations': data[8],
            'address_id': data[9],
        }

    def get_user_info(self, userid):
        dao = UserDao()
        try:
            user = dao.get_user_info(userid)
            return jsonify(self.get_user_info_dict(user)), 201
        except IntegrityError as e:
            return jsonify(e.pgerror), 400
