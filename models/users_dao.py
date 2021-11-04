from decorators import exception_handler
from models.main_dao import MainDao
from utilities import ADMIN_ACCOUNT, STUDENT_ACCOUNT, CLIENT_ACCOUNT


class UserDao(MainDao):

    @exception_handler
    def create_user(self, data):
        cursor = self.conn.cursor()
        query = 'insert into users (first_name, last_name, password, email, type) values (%s, %s, ' \
                'crypt(%s, gen_salt(\'bf\')), %s, %s) returning user_id, first_name, last_name, email, type;'
        cursor.execute(query, (data['first_name'].capitalize(), data['last_name'].capitalize(), data['password'],
                               data['email'], data['type']))
        user_info = cursor.fetchone()

        query = 'insert into questions (user_id, type, answer) values (%s, %s, %s)'
        cursor.execute(query, (user_info[0], data['q_type1'], data['ans1']))
        cursor.execute(query, (user_info[0], data['q_type2'], data['ans2']))

        self.conn.commit()
        return user_info, None

    @exception_handler
    def login_user(self, credentials):
        if credentials['admin']:
            user_type = (ADMIN_ACCOUNT, )
        else:
            user_type = (STUDENT_ACCOUNT, CLIENT_ACCOUNT)

        cursor = self.conn.cursor()
        query = 'select user_id, type ' \
                'from users ' \
                'where type in %s and email=%s and password=crypt(%s, password) and deleted=false;'
        cursor.execute(query, (user_type, credentials['email'], credentials['password']))
        result = cursor.fetchone()
        if result is None:
            return None, None

        return result, None

    @exception_handler
    def edit_user(self, data):
        cursor = self.conn.cursor()
        if data['image_key'] is not None:
            query = 'update users ' \
                    'set first_name = %s, last_name = %s, image = %s, about = %s ' \
                    'where user_id=%s and deleted=false returning address_id;'

            cursor.execute(query, (data['first_name'].capitalize(), data['last_name'].capitalize(), data['image_key'],
                                   data['about'], data['user_id']))
        else:
            query = 'update users ' \
                    'set first_name = %s, last_name = %s, about = %s ' \
                    'where user_id=%s and deleted=false returning address_id;'

            cursor.execute(query, (data['first_name'].capitalize(), data['last_name'].capitalize(), data['about'],
                                   data['user_id']))

        user_info = cursor.fetchone()
        if user_info is None:
            return None, None

        else:
            if data['street'] is not None and data['city'] is not None and data['zipcode'] is not None:

                if user_info[0] is None:
                    query1 = 'insert into address (street, city, zipcode) values (%s, %s, %s) returning address_id;'
                    cursor.execute(query1, (data['street'], data['city'], data['zipcode']))

                    address_info = cursor.fetchone()

                    query2 = 'update users set address_id = %s where user_id = %s;'
                    cursor.execute(query2, (address_info[0], data['user_id']))

                else:
                    query = 'update address set street = %s, city = %s, zipcode = %s where address_id = %s;'
                    cursor.execute(query, (data['street'], data['city'], data['zipcode'], user_info[0]))

            else:
                if user_info[0] is not None and (data['street'] is None or data['city'] is None or data['zipcode']
                                                 is None):
                    query = 'delete from address ' \
                            'where address_id = %s;'
                    cursor.execute(query, (user_info[0], ))

            self.conn.commit()
            return user_info, None

    @exception_handler
    def get_all_users(self, data):
        filters = ''
        params = [data['deleted']]
        if 'type' in data:
            filters = 'and type=%s '
            params.append(data['type'])

        cursor = self.conn.cursor()
        query = 'select user_id, first_name, last_name, email, type ' \
                'from users ' \
                'where deleted=%s {filters}' \
                'order by first_name;'.format(filters=filters)
        cursor.execute(query, params)
        results = self.convert_to_list(cursor)
        if len(results) == 0:
            return None, None

        return results, None

    @exception_handler
    def retrieve_questions(self, user_email):
        cursor = self.conn.cursor()
        query = 'select type, answer ' \
                'from questions where user_id in (select user_id from users where email=%s and deleted=false);'
        cursor.execute(query, (user_email['email'],))

        if cursor.rowcount == 0:
            return None, None

        questions = cursor.fetchall()
        question1, answer1 = questions[0]
        question2, answer2 = questions[1]
        security = [question1, question2, answer1, answer2]

        return security, None

    @exception_handler
    def change_password(self, user_email):
        cursor = self.conn.cursor()
        query = 'update users set password = crypt(%s, gen_salt(\'bf\')) where email=%s and deleted=false ' \
                'returning email, password;'
        cursor.execute(query, (user_email['password'], user_email['email']))
        info = cursor.fetchone()
        if info is None:
            return None, None

        self.conn.commit()
        return info, None

    @exception_handler
    def get_user_info(self, user):
        cursor = self.conn.cursor()
        query = 'select first_name, last_name, email, image, about, cancellations, type, address_id ' \
                'from users ' \
                'where user_id=%s and deleted=false;'

        cursor.execute(query, (user['user_id'], ))
        user_info = cursor.fetchone()
        if user_info is None:
            return None, None

        if user_info[-1] is not None:
            query = 'select street, city, zipcode ' \
                    'from address ' \
                    'where address_id=%s;'
            cursor.execute(query, (user_info[-1], ))
            user_info = user_info + cursor.fetchone()
        else:
            user_info = user_info + (None, None, None)

        rate = self.get_user_ratings(user['user_id'], cursor)
        user_info = user_info + (rate, )

        return user_info, None

    @exception_handler
    def delete_user(self, data):
        cursor = self.conn.cursor()
        query = 'update users set deleted=true where user_id=%s and deleted=false;'
        cursor.execute(query, (data['user_id'], ))
        if cursor.rowcount == 0:
            return False, None

        self.conn.commit()
        return True, None
