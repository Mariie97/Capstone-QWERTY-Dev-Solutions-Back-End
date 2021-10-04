from models.main_dao import MainDao
from flask import jsonify
import json

class Controller:

    def build_attr_dict(self, data_dict):
        return {
            'id': data_dict[0],
            'msg': data_dict[1],
        }

    def get_message(self):
        dao = MainDao()
        result = dao.get_message()

        result_list = []
        for row in result:
            obj = self.build_attr_dict(row)
            result_list.append(obj)
        
        return json.dumps(result)
