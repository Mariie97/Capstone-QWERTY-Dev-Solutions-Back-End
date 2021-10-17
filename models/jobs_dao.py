from psycopg2 import DatabaseError

from decorators import exception_handler
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
        except (Exception, DatabaseError) as error:
            return None, error.pgerror
        finally:
            self.conn.close()

    @exception_handler
    def get_job_details(self, data):
        cursor = self.conn.cursor()
        query = 'select owner_id, student_id, title, description, price, categories, status, date_posted, pdf, ' \
                'street, city, zipcode, O.first_name, O.last_name, O.image ' \
                'from jobs as J ' \
                'inner join users as O on J.owner_id=O.user_id ' \
                'inner join address as A on A.address_id=O.address_id ' \
                'where job_id=%s;'
        cursor.execute(query, (data['job_id'], ))
        details = cursor.fetchone()
        if details is None:
            return None, None

        if details[1] is not None:
            query = 'select first_name, last_name ' \
                    'from users ' \
                    'where user_id=%s;'
            cursor.execute(query, (details[1], ))
            details = details + cursor.fetchone()

        query = 'select weekday ' \
                'from days ' \
                'where job_id=%s;'
        cursor.execute(query, (data['job_id'], ))
        days = [row[0] for row in cursor.fetchall()]
        details = (details, days)

        return details, None

    @exception_handler
    def get_job_list_by_status(self, data):
        cursor = self.conn.cursor()
        query = 'select job_id, title, price, categories, date_posted ' \
                'from jobs ' \
                'where status=%s ' \
                'order by date_posted asc;'
        cursor.execute(query, (data['status'], ))
        requests_list = self.convert_to_list(cursor)
        if requests_list.__len__() == 0:
            return None, None
        else:
            return requests_list, None
