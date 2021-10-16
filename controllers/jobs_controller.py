from flask import jsonify

from models.jobs_dao import JobDao
from utilities import STATUS_CODE, convert_date_to_string


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
        is_updated, error_msg = self.dao.set_job_worker(data)
        if is_updated is None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if not is_updated:
            return jsonify("Job {job_id} or related requests for that job could not be found".format(
                job_id=data['job_id'])),  STATUS_CODE['not_found']

        return jsonify("Job {job_id} updated successfully!".format(job_id=data['job_id'])), STATUS_CODE['ok']

    def get_job_list_by_status(self, data):
        jobs_list, error_msg = self.dao.get_job_list_by_status(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if jobs_list is None:
            return jsonify("No jobs were found with status={status}.".format(status=data['status'])), \
                   STATUS_CODE['not_found']

        results = []
        for row in jobs_list:
            job = {
                'job_id': row[0],
                'title': row[1],
                'price': row[2],
                'categories': row[3],
                'date_posted': convert_date_to_string(row[4]),
            }
            results.append(job)

        return jsonify(results), STATUS_CODE['ok']
