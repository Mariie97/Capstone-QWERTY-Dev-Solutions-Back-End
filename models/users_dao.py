from decorators import exception_handler
from models.main_dao import MainDao


class UserDao(MainDao):

    def create_user(self, data):
        cursor = self.conn.cursor()
        query = 'insert into users (first_name, last_name, password, email, type) values (%s, %s, ' \
                'crypt(%s, gen_salt(\'bf\')), %s, %s) returning user_id, first_name, last_name, email, type;'
        cursor.execute(query, (data['first_name'].capitalize(), data['last_name'].capitalize(), data['password'],
                               data['email'], data['type']))
        user_info = cursor.fetchone()
        self.conn.commit()

        query = 'insert into questions (user_id, type, answer) values (%s, %s, %s)'
        cursor.execute(query, (user_info[0], data['q_type1'], data['ans1']))
        cursor.execute(query, (user_info[0], data['q_type2'], data['ans2']))
        self.conn.commit()

        return user_info

    def login_user(self, credentials):
        cursor = self.conn.cursor()
        query = 'select user_id, type ' \
                'from users ' \
                'where email=%s and password=crypt(%s, password) and deleted=false;'
        cursor.execute(query, (credentials['email'], credentials['password']))
        result = cursor.fetchone()
        return result

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
            return None
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

    def get_all_users(self, data):
        cursor = self.conn.cursor()
        query = 'select user_id, first_name, last_name, email ' \
                'from users ' \
                'where type=%s and deleted=false ' \
                'order by first_name;'
        cursor.execute(query, (data['type'], ))
        results = self.convert_to_list(cursor)
        return results

    def retrieve_questions(self, user_email):
        cursor = self.conn.cursor()
        query = 'select type, answer ' \
                'from questions where user_id in (select user_id from users where email=%s and deleted=false);'
        cursor.execute(query, (user_email['email'],))

        if cursor.rowcount == 0:
            return None

        questions = cursor.fetchall()
        question1, answer1 = questions[0]
        question2, answer2 = questions[1]
        security = [question1, question2, answer1, answer2]

        return security

    def change_password(self, user_email):
        cursor = self.conn.cursor()
        query = 'update users set password = crypt(%s, gen_salt(\'bf\')) where email=%s and deleted=false ' \
                'returning email, password;'
        cursor.execute(query, (user_email['password'], user_email['email']))
        info = cursor.fetchone()
        if info is None:
            return None
        self.conn.commit()

        return info

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

        query = 'select AVG(value) from rates where user_id=%s;'
        cursor.execute(query, (user['user_id'], ))
        rate = cursor.fetchone()[0]
        if rate is None:
            user_info = user_info + (None, )
        else:
            rate_value = float(rate[0])
            format_number = int(rate_value) if rate_value.is_integer() else format(rate_value, ".2f")
            user_info = user_info + (format_number, )

        return user_info, None

    @exception_handler
    def delete_user(self, data):
        cursor = self.conn.cursor()
        query = 'update users set deleted=true where user_id=%s;'
        cursor.execute(query, (data['user_id'], ))
        if cursor.rowcount == 0:
            return False, None

        self.conn.commit()
        return True, None
