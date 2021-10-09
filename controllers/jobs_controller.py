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

    def get_student_requests_list(self, data):
        requests = self.dao.get_student_requests_list(data)
        if requests is None:
            return jsonify("Student {id} has no requests.".format(id=data['student_id'])), STATUS_CODE['not_found']
        else:
            list = []
            for row in requests:
                request = {
                    'job_id': row[0],
                    'title': row[1],
                    'price': row[2],
                    'categories': row[3],
                    'date': row[4],
                }
                list.append(request)
            return jsonify(list), STATUS_CODE['ok']

    def set_job_worker(self, data):
        is_updated = self.dao.set_job_worker(data)
        if is_updated is None:
            return jsonify("Could not update the job at this moment"), STATUS_CODE['server_error']

        if not is_updated:
            return jsonify("Job {job_id} or related requests for that job could not be found".format(
                job_id=data['job_id'])),  STATUS_CODE['not_found']

        return jsonify("Job {job_id} updated successfully!".format(job_id=data['job_id'])), STATUS_CODE['ok']

