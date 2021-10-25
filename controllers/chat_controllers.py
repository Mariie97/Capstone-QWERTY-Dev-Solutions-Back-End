from flask import jsonify

from models.chat_dao import ChatDao
from utilities import STATUS_CODE, format_date, generate_profile_pic_url


class ChatController:

    def __init__(self):
        self.dao = ChatDao()

    @staticmethod
    def build_msg_dict(data):
        return {
            'msg_id': data[0],
            'sender_id': data[1],
            'receiver_id': data[2],
            'job_id': data[3],
            'content': data[4],
            'date': format_date(data[5]),
        }

    def create_message(self, data):
        message, error_msg = self.dao.create_message(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        return jsonify(self.build_msg_dict(message)), STATUS_CODE['created']

    def get_job_messages(self, data):
        messages_list, error_msg = self.dao.get_job_messages(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if messages_list is None:
            return jsonify("No messages were found for job with id={id}".format(id=data['job_id'])), \
                   STATUS_CODE['not_found']

        list = []
        for row in messages_list:
            dict = self.build_msg_dict(row)
            dict.update({
                'sender_name': row[6],
                'sender_last': row[7],
                'sender_image': generate_profile_pic_url(row[8]) if row[8] is not None else None,
            })
            list.append(dict)

        return jsonify(list), STATUS_CODE['ok']

