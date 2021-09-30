from flask import jsonify

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
        user = dao.create_user(user_info)
        return jsonify(self.build_attr_dict(user)), 201

