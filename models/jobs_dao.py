from psycopg2 import DatabaseError

from models.main_dao import MainDao
from utilities import JOB_REQUESTS_STATE, JOB_STATE


class JobDao(MainDao):

    def get_requests_list(self, data):
        cursor = self.conn.cursor()
        query = 'select user_id, first_name, last_name, image, date ' \
                'from requests as R inner join users as U on R.student_id=U.user_id ' \
                'where job_id=%s ' \
                'order by date asc;'

        cursor.execute(query, (data['job_id'], ))
        requests_list = self.convert_to_list(cursor)
        if requests_list.__len__() == 0:
            return None
        else:
            return requests_list

    def get_student_requests_list(self, data):
        cursor = self.conn.cursor()
        query = 'select R.job_id, title, price, categories, date ' \
                'from (requests as R inner join jobs as J using(job_id)) inner join users as U on J.owner_id=U.user_id ' \
                'where R.student_id=%s and state=%s ' \
                'order by date asc;'
        cursor.execute(query, (data['student_id'], JOB_REQUESTS_STATE['open']))
        requests_list = self.convert_to_list(cursor)
        if requests_list.__len__() == 0:
            return None
        else:
            return requests_list

    def set_job_worker(self, data):
        try:
            cursor = self.conn.cursor()
            query = 'update jobs set student_id = %s, status = %s  where job_id=%s;'
            cursor.execute(query, (data['student_id'], JOB_STATE['in_process'], data['job_id']))
            if cursor.rowcount == 0:
                return False, None

            query = 'update requests set state = %s where job_id=%s;'
            cursor.execute(query, (JOB_REQUESTS_STATE['closed'], data['job_id']))

            if cursor.rowcount == 0:
                return False, None

            self.conn.commit()
            return True, None
        except DatabaseError as error:
            return None, error.pgerror
        finally:
            self.conn.close()

