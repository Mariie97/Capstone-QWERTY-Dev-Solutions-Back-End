from psycopg2 import DatabaseError

from decorators import exception_handler
from models.main_dao import MainDao
from utilities import JOB_REQUESTS_STATE, JOB_STATUS


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
            cursor.execute(query, (data['student_id'], JOB_STATUS['in_process'], data['job_id']))
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

    @exception_handler
    def set_job_status(self, data):
        cursor = self.conn.cursor()
        query = 'update jobs set status = %s where job_id=%s  returning student_id;'
        cursor.execute(query, (data['status'], data['job_id']))
        if cursor.rowcount == 0:
            return None, None

        student_id = cursor.fetchone()[0]
        if data['status'] == JOB_STATUS['posted'] and student_id is not None:
            query = 'update jobs set student_id = null where job_id=%s;'
            cursor.execute(query, (data['job_id'], ))

        self.conn.commit()
        return True, None

    @exception_handler
    def add_job_ratings(self, data):
        cursor = self.conn.cursor()
        query = 'insert into rates (job_id, user_id, value) values (%s, %s, %s);'
        cursor.execute(query, (data['job_id'], data['user_id'], data['value']))

        query = 'select count(*) ' \
                'from rates ' \
                'where job_id=%s;'
        cursor.execute(query, (data['job_id'], ))
        total_rates = cursor.fetchone()
        if total_rates is not None and int(total_rates[0]) == 2:
            job_status = {
                'job_id': data['job_id'],
                'status': JOB_STATUS['completed']
            }
            job_updated, error_msg = self.set_job_status(job_status)
            if error_msg is not None:
                return None, error_msg
        else:
            self.conn.commit()
        return True, None
