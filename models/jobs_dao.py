from psycopg2 import DatabaseError

from models.main_dao import MainDao
from utilities import JOB_REQUESTS_STATE, JOB_STATE


class JobDao(MainDao):

    def create_job(self, data):
        cursor = self.conn.cursor()

        query = 'insert into address (street, city, zipcode)' \
                'values (%s, %s, %s) returning address_id;'
        cursor.execute(query, (data['street'], data['city'], data['zipcode']))
        add_id = cursor.fetchone()
        self.conn.commit()

        query = 'insert into jobs (owner_id, title, description, price, categories, address_id) ' \
                'values (%s, %s, %s, %s, %s, %s) returning job_id, owner_id, title, description, price, categories;'
        cursor.execute(query, (data['user_id'], data['title'], data['description'], data['price'], data['categories'],
                               add_id[0]))
        job_info = cursor.fetchone()
        job_id = job_info[0]
        self.conn.commit()

        self.set_job_days(job_id, data['d'], data['l'], data['m'], data['w'], data['j'], data['v'], data['s'])

        return job_info

    def set_job_days(self, job_id, dom, lun, mar, wed, jue, vie, sab):
        cursor = self.conn.cursor()
        query = 'insert into days (job_id, weekday) ' \
                'values (%s, %s);'
        if dom == '1':
            cursor.execute(query, (job_id, '1'))
        if lun == '1':
            cursor.execute(query, (job_id, '2'))
        if mar == '1':
            cursor.execute(query, (job_id, '3'))
        if wed == '1':
            cursor.execute(query, (job_id, '4'))
        if jue == '1':
            cursor.execute(query, (job_id, '5'))
        if vie == '1':
            cursor.execute(query, (job_id, '6'))
        if sab == '1':
            cursor.execute(query, (job_id, '7'))
        self.conn.commit()
        self.conn.close()

    def get_requests_list(self, data):
        cursor = self.conn.cursor()
        query = 'select user_id, first_name, last_name, image, date ' \
                'from requests as R inner join users as U on R.student_id=U.user_id ' \
                'where job_id=%s ' \
                'order by date asc;'

        cursor.execute(query, (data['job_id'],))
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
