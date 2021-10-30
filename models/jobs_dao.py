from psycopg2 import DatabaseError

from decorators import exception_handler
from models.main_dao import MainDao
from utilities import JOB_REQUESTS_STATE, WEEK_DAYS, JOB_STATUS


class JobDao(MainDao):

    @exception_handler
    def create_job(self, data):
        cursor = self.conn.cursor()

        query = 'insert into address (street, city, zipcode)' \
                'values (%s, %s, %s) returning address_id;'
        cursor.execute(query, (data['street'], data['city'], data['zipcode']))
        add_id = cursor.fetchone()

        query = 'insert into jobs (owner_id, title, description, price, categories, address_id) ' \
                'values (%s, %s, %s, %s, %s, %s) returning job_id, owner_id, title, description, price, categories;'
        cursor.execute(query, (data['user_id'], data['title'].title(), data['description'], data['price'],
                               data['categories'], add_id[0]))
        job_info = cursor.fetchone()
        job_id = job_info[0]

        self.set_job_days(job_id, data['d'], data['l'], data['m'], data['w'], data['j'], data['v'], data['s'])
        self.conn.commit()
        return job_info, None

    def set_job_days(self, job_id, dom, lun, mar, wed, jue, vie, sab):
        cursor = self.conn.cursor()
        query = 'insert into days (job_id, weekday) ' \
                'values (%s, %s);'
        if dom == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['domingo']))
        if lun == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['lunes']))
        if mar == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['martes']))
        if wed == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['miercoles']))
        if jue == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['jueves']))
        if vie == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['viernes']))
        if sab == '1':
            cursor.execute(query, (job_id, WEEK_DAYS['sabado']))

    @exception_handler
    def add_job_request(self, data):
        cursor = self.conn.cursor()
        query = 'insert into requests (job_id, student_id) values (%s, %s) returning job_id, student_id, date, state;'
        cursor.execute(query, (data['job_id'], data['student_id']))
        request = cursor.fetchone()
        self.conn.commit()
        return request, None

    @staticmethod
    def close_job_requests(cursor, job_id):
        query = 'update requests set state = %s where job_id=%s and state=%s;'
        cursor.execute(query, (JOB_REQUESTS_STATE['closed'], job_id, JOB_REQUESTS_STATE['open']))

    @exception_handler
    def cancel_job_request(self, data):
        cursor = self.conn.cursor()
        query = 'update requests set state = %s where job_id=%s and student_id=%s and state=%s;'
        cursor.execute(query, (JOB_REQUESTS_STATE['closed'], data['job_id'], data['student_id'],
                       JOB_REQUESTS_STATE['open']))
        if cursor.rowcount == 0:
            return None, None

        self.conn.commit()
        return True, None

    @exception_handler
    def get_requests_list(self, data):
        cursor = self.conn.cursor()
        query = 'select user_id, first_name, last_name, image, date ' \
                'from requests as R inner join users as U on R.student_id=U.user_id ' \
                'where job_id=%s ' \
                'order by date asc;'

        cursor.execute(query, (data['job_id'], ))
        requests_list = self.convert_to_list(cursor)
        if len(requests_list) == 0:
            return None, None

        return requests_list, None

    @exception_handler
    def get_student_requests_list(self, data):
        cursor = self.conn.cursor()
        query = 'select R.job_id, title, price, categories, date ' \
                'from (requests as R inner join jobs as J using(job_id)) inner join users as U on J.owner_id=U.user_id ' \
                'where R.student_id=%s and state=%s ' \
                'order by date asc;'
        cursor.execute(query, (data['student_id'], JOB_REQUESTS_STATE['open']))
        requests_list = self.convert_to_list(cursor)
        if len(requests_list) == 0:
            return None, None

        return requests_list, None

    @exception_handler
    def set_job_worker(self, data):
        cursor = self.conn.cursor()
        query = 'update jobs set student_id = %s, status = %s  where job_id=%s;'
        cursor.execute(query, (data['student_id'], JOB_STATUS['in_process'], data['job_id']))
        if cursor.rowcount == 0:
            return None, None

        self.close_job_requests(cursor, data['job_id'])
        if cursor.rowcount == 0:
            return None, None

        self.conn.commit()
        return True, None

    @exception_handler
    def get_job_details(self, data):
        # TODO: This must be able to return all job without considering the status?
        cursor = self.conn.cursor()
        query = 'select owner_id, student_id, title, description, price, categories, status, date_posted, pdf, ' \
                'street, city, zipcode, O.first_name, O.last_name, O.image, O.cancellations ' \
                'from jobs as J ' \
                'inner join users as O on J.owner_id=O.user_id ' \
                'inner join address as A on A.address_id=J.address_id ' \
                'where job_id=%s'
        cursor.execute(query, (data['job_id'], ))
        details = cursor.fetchone()
        if details is None:
            return None, None

        student_id = details[1]
        if student_id is not None:
            query = 'select first_name, last_name ' \
                    'from users ' \
                    'where user_id=%s;'
            cursor.execute(query, (details[1], ))
            details = details + cursor.fetchone()

        query = 'select weekday ' \
                'from days ' \
                'where job_id=%s ' \
                'order by weekday asc;'
        cursor.execute(query, (data['job_id'], ))
        days = [row[0] for row in cursor.fetchall()]

        query = 'select student_id, state ' \
                'from requests ' \
                'where job_id=%s ' \
                'order by student_id asc;'
        cursor.execute(query, (data['job_id'], ))
        requests = self.convert_to_list(cursor)

        owner_id = details[0]
        owner_rating = self.get_user_ratings(owner_id, cursor)

        details = (details, days, requests, owner_rating)

        return details, None

    @exception_handler
    def get_job_list_by_status(self, data):
        filters = ''
        limit = ''
        params = [data['status']]

        if 'owner_id' in data:
            filters = 'and owner_id=%s '
            params.append(data['owner_id'])

        if 'month' in data:
            filters = 'and date_part(\'month\', date_posted)=%s '
            params.append(data['month'])

        if 'year' in data:
            filters = filters + 'and date_part(\'year\', date_posted)=%s '
            params.append(data['year'])

        if 'category' in data:
            filters = filters + 'and categories=%s '
            params.append(data['category'])

        if 'city' in data:
            filters = filters + 'and city=%s '
            params.append(data['city'])

        if 'minPrice' in data:
            filters = filters + 'and price>=%s '
            params.append(data['minPrice'])

        if 'maxPrice' in data:
            filters = filters + 'and price<=%s '
            params.append(data['maxPrice'])

        if 'limit' in data:
            limit = 'limit %s'
            params.append(data['limit'])

        cursor = self.conn.cursor()
        query = 'select job_id, title, price, categories, date_posted, city ' \
                'from jobs natural inner join address ' \
                'where status=%s {filters}' \
                'order by date_posted desc ' \
                '{limit};'.format(filters=filters, limit=limit)
        cursor.execute(query, params)

        requests_list = self.convert_to_list(cursor)
        if len(requests_list) == 0:
            return None, None

        return requests_list, None

    @exception_handler
    def set_job_status(self, data):
        cursor = self.conn.cursor()
        query = 'update jobs set status = %s where job_id=%s  returning student_id, owner_id;'
        cursor.execute(query, (data['status'], data['job_id']))
        if cursor.rowcount == 0:
            return None, None

        student_id, owner_id = cursor.fetchone()

        status = str(data['status'])
        # Student cancel the job
        if status == JOB_STATUS['posted'] and student_id is not None:
            query = 'update jobs set student_id = null where job_id=%s;'
            cursor.execute(query, (data['job_id'], ))

            query = 'update users set cancellations=cancellations + 1 where user_id=%s'
            cursor.execute(query, (student_id, ))

        # Job's owner cancel the job
        elif status == JOB_STATUS['cancelled']:
            query = 'update users set cancellations=cancellations + 1 where user_id=%s'
            cursor.execute(query, (owner_id,))

            self.close_job_requests(cursor, data['job_id'])

        # Admin delete the job
        elif status == JOB_STATUS['deleted']:
            self.close_job_requests(cursor, data['job_id'])

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
