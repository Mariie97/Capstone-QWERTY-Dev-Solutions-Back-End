from flask import jsonify

from models.jobs_dao import JobDao
from utilities import STATUS_CODE, format_date, generate_profile_pic_url, JOB_CATEGORIES, format_price


class JobController:

    def __init__(self):
        self.dao = JobDao()

    @staticmethod
    def job_creation_dict(data):
        return {
            'job_id': data[0],
            'owner_id': data[1],
            'title': data[2],
            'description': data[3],
            'price': format_price(data[4]),
            'category': data[5]
        }

    def create_job(self, data):
        job, error_msg = self.dao.create_job(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        return jsonify(self.job_creation_dict(job)), STATUS_CODE['created']

    def add_job_request(self, data):
        request, error_msg = self.dao.add_job_request(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        dict = {
            'job_id': request[0],
            'student_id': request[1],
            'date': request[2],
            'state': request[3],
        }

        return jsonify(dict), STATUS_CODE['ok']

    def cancel_job_request(self, data):
        updated, error_msg = self.dao.cancel_job_request(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if updated is None:
            return jsonify('No request were found with the given criteria.'), STATUS_CODE['not_found']

        return jsonify('Request of student {user_id} for job {job_id} closed successfully!'.format(
            user_id=data['student_id'],
            job_id=data['job_id']
        )), STATUS_CODE['ok']

    def get_requests_list(self, data):
        requests, error_msg = self.dao.get_requests_list(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if requests is None:
            return jsonify('No requests were found'), STATUS_CODE['not_found']

        list = []
        for row in requests:
            request = {
                'user_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'image': generate_profile_pic_url(row[3]),
                'date': row[4],
            }
            list.append(request)
        return jsonify(list), STATUS_CODE['ok']

    def get_student_requests_list(self, data):
        requests, error_msg = self.dao.get_student_requests_list(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if requests is None:
            return jsonify("Student {id} has no requests.".format(id=data['student_id'])), STATUS_CODE['not_found']

        list = []
        for row in requests:
            request = {
                'job_id': row[0],
                'title': row[1],
                'price':  format_price(row[2]),
                'categories': JOB_CATEGORIES[row[3]],
                'date': row[4],
            }
            list.append(request)
        return jsonify(list), STATUS_CODE['ok']

    def set_job_worker(self, data):
        is_updated, error_msg = self.dao.set_job_worker(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if is_updated is None:
            return jsonify("Job {job_id} or related requests for that job could not be found".format(
                job_id=data['job_id'])),  STATUS_CODE['not_found']

        return jsonify("Job {job_id} updated successfully!".format(job_id=data['job_id'])), STATUS_CODE['ok']

    def get_job_details(self, data):
        details, error_msg = self.dao.get_job_details(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if details is None:
            return jsonify("Job with id={job_id} not found".format(job_id=data['job_id'])), STATUS_CODE['not_found']

        details_dict = {
            'owner_id': details[0][0],
            'student_id': details[0][1],
            'title': details[0][2],
            'description': details[0][3],
            'price':  format_price(details[0][4]),
            'categories': JOB_CATEGORIES[details[0][5]],
            'status': details[0][6],
            'date_posted': format_date(details[0][7]),
            'pdf': details[0][8],
            'street': details[0][9],
            'city': details[0][10],
            'zipcode': details[0][11],
            'owner_name': details[0][12],
            'owner_last': details[0][13],
            'owner_image': details[0][14] if details[0][14] is None else generate_profile_pic_url(details[0][14]),
            'owner_cancellations': details[0][15],
            'student_name': details[0][16] if details[0][1] is not None else None,
            'student_last': details[0][17] if details[0][1] is not None else None,
            'days': details[1],
            'users_requested': details[2],
            'owner_rating': details[3],
        }

        return jsonify(details_dict), STATUS_CODE['ok']

    def get_job_list_by_status(self, data):
        jobs_list, error_msg = self.dao.get_job_list_by_status(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if jobs_list is None:
            return jsonify("No jobs were found with the given criterias".format(status=data['status'])), \
                   STATUS_CODE['not_found']

        results = []
        for row in jobs_list:
            job = {
                'job_id': row[0],
                'title': row[1],
                'price':  format_price(row[2]),
                'categories': JOB_CATEGORIES[row[3]],
                'date_posted': format_date(row[4]),
                'city': row[5],
                'owner_id': row[6],
                'owner_first': row[7],
                'owner_last': row[8],
                'street': row[9],
                'zipcode': row[10],
            }
            results.append(job)

        return jsonify(results), STATUS_CODE['ok']

    def set_job_status(self, data):
        is_updated, error_msg = self.dao.set_job_status(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if not is_updated:
            return jsonify('Job with id={id} not found.'.format(id=data['job_id'])), STATUS_CODE['not_found']

        return jsonify("Job {job_id} updated successfully!".format(job_id=data['job_id'])), STATUS_CODE['ok']

    def add_job_ratings(self, data):
        rated, error_msg = self.dao.add_job_ratings(data)
        if error_msg is not None:
            return jsonify(error_msg), STATUS_CODE['bad_request']

        if rated is None:
            return jsonify('Could not add rates at this moment.'.format(id=data['job_id'])), STATUS_CODE['server_error']

        return jsonify('Rating added successfully!'), STATUS_CODE['created']
