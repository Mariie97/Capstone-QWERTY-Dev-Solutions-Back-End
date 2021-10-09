from models.main_dao import MainDao
from utilities import JOB_REQUESTS_STATE


class JobDao(MainDao):

    def get_requests_list(self, data):
        cursor = self.conn.cursor()
        query = 'select user_id, first_name, last_name, image, date ' \
                'from requests as R inner join users as U on R.student_id=U.user_id ' \
                'where job_id=%s ' \
                'order by date asc;'

        cursor.execute(query, (data['job_id'], ))
        requests_list = []
        for row in cursor:
            requests_list.append(row)
        return requests_list

    def set_job_worker(self, data):
        cursor = self.conn.cursor()
        query = 'update jobs set student_id = %s where job_id=%s;'
        cursor.execute(query, (data['student_id'], data['job_id']))
        if cursor.rowcount == 0:
            return False

        query = 'update requests set state = %s where job_id=%s;'
        cursor.execute(query, (JOB_REQUESTS_STATE['closed'], data['job_id']))

        if cursor.rowcount == 0:
            return False

        self.conn.commit()
        return True
