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

    def get_user_info(self, user):
        cursor = self.conn.cursor()
        query = 'select address_id from users where user_id = %s;'
        cursor.execute(query, (user['user_id'],))
        address_info = cursor.fetchone()
        self.conn.commit()

        if address_info[0] is None:
            query1 = 'select * from users where user_id = %s;'
            cursor.execute(query1, (user['user_id'],))
            address_user = cursor.fetchone()
            self.conn.commit()
            user_info = [None, address_user[0], address_user[1], address_user[2], address_user[3],
                         address_user[4], address_user[5], address_user[6], address_user[7], address_user[8],
                         None, None, None]

        else:
            query1 = 'select * from users natural inner join address where user_id = %s;'
            cursor.execute(query1, (user['user_id'],))
            user_info = cursor.fetchone()
            self.conn.commit()

        return user_info
