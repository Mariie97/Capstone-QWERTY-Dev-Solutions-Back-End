import decimal

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
                'where email=%s and password=crypt(%s, password);'
        cursor.execute(query, (credentials['email'], credentials['password']))
        result = cursor.fetchone()
        return result

    def edit_user(self, data):
        cursor = self.conn.cursor()
        query = 'update users set first_name = %s, last_name = %s, image = %s, about = %s, password = ' \
                'crypt(%s, gen_salt(\'bf\')) where user_id = %s returning address_id;'

        cursor.execute(query, (data['first_name'].capitalize(), data['last_name'].capitalize(), data['image_key'],
                               data['about'], data['password'], data['user_id']))

        user_info = cursor.fetchone()
        if user_info is None:
            return None
        else:
            self.conn.commit()

            if data['street'] is not None and data['city'] is not None and data['zipcode'] is not None:

                if user_info[0] is None:
                    query1 = 'insert into address (street, city, zipcode) values (%s, %s, %s) returning address_id;'
                    cursor.execute(query1, (data['street'], data['city'], data['zipcode']))

                    address_info = cursor.fetchone()
                    self.conn.commit()

                    query2 = 'update users set address_id = %s where user_id = %s;'
                    cursor.execute(query2, (address_info[0], data['user_id']))

                else:
                    query = 'update address set street = %s, city = %s, zipcode = %s where address_id = %s;'
                    cursor.execute(query, (data['street'], data['city'], data['zipcode'], user_info[0]))

                self.conn.commit()
            return user_info

    def get_all_users(self, data):
        cursor = self.conn.cursor()
        query = 'select first_name, last_name, email ' \
                'from users ' \
                'where type=%s;'
        cursor.execute(query, (data['type'], ))
        results = []
        for row in cursor:
            results.append(row)
        return results

    def get_user_info(self, user):
        cursor = self.conn.cursor()
        query = 'select address_id from users where user_id = %s;'
        query2 = 'select AVG(value) from rates where user_id = %s;'
        cursor.execute(query, (user['user_id'],))
        address_info = cursor.fetchone()
        if address_info is None:
            return None
        cursor.execute(query2, (user['user_id'],))
        rate_average = cursor.fetchone()

        if rate_average[0] is None:
            new_number = str(decimal.Decimal(0.0))
        else:
            new_number = str(decimal.Decimal(rate_average[0]))

        if address_info[0] is None:
            query1 = 'select * from users where user_id = %s;'
            cursor.execute(query1, (user['user_id'],))
            address_user = cursor.fetchone()
            user_info = [None, address_user[0], address_user[1], address_user[2], address_user[3],
                         address_user[4], address_user[5], address_user[6], address_user[7], address_user[8],
                         None, None, None, new_number]

        else:
            query1 = 'select * from users natural inner join address where user_id = %s;'
            cursor.execute(query1, (user['user_id'],))
            query_info = cursor.fetchone()
            user_info = [query_info[0], query_info[1], query_info[2], query_info[3], query_info[4], query_info[5],
                         query_info[6], query_info[7], query_info[8], query_info[9], query_info[10], query_info[11],
                         query_info[12], new_number]

        return user_info
