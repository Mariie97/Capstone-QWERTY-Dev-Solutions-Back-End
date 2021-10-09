from flask import jsonify

from models.jobs_dao import JobDao
from utilities import STATUS_CODE


class JobController:

    def __init__(self):
        self.dao = JobDao()

    def get_requests_list(self, data):
        requests = self.dao.get_requests_list(data)
        list = []
        for row in requests:
            request = {
                'user_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'image': row[3],
                'date': row[4],
            }
            # TODO: generate image URL, from AWS bucket
            # request['image'] =
            list.append(request)
        return jsonify(list), STATUS_CODE['ok']
