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

    def edit_user(self, data):
        cursor = self.conn.cursor()
        query = 'update users set first_name = %s, last_name = %s, image = %s, about = %s, ' \
                'password = crypt(%s, gen_salt(\'bf\')) where user_id = %s returning user_id, first_name, last_name, ' \
                ' image, about, password, address_id;'
        cursor.execute(query, (data['first_name'].capitalize(), data['last_name'].capitalize(), data['image'],
                               data['about'], data['password'], data['user_id']))
        user_info = cursor.fetchone()
        self.conn.commit()

        if user_info[6] == 'null':
            query1 = 'insert into address (street, city, zipcode) values (%s, %s, %s);'
            cursor.execute(query1, (data['street'], data['city'], data['zipcode']))
            query2 = 'update users set address_id = %s where user_id = %s;'
            cursor.execute(query2, (user_info[6], data['user_id']))

        else:
            query = 'update address set street = %s, city = %s, zipcode = %s where address_id = %s;'
            cursor.execute(query, (data['street'], data['city'], data['zipcode'], user_info[6]))

        self.conn.commit()
        return user_info
