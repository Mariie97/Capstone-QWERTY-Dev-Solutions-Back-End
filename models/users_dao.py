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

    def retrieve_questions(self, user_email):
        cursor = self.conn.cursor()
        query = 'select user_id from users where email = %s;'
        cursor.execute(query, (user_email['email'],))
        result = cursor.fetchone()
        self.conn.commit()

        query2 = 'select type, answer from questions where user_id = %s;'
        cursor.execute(query2, (result[0],))
        questions = cursor.fetchall()
        self.conn.commit()
        question1, answer1 = questions[0]
        question2, answer2 = questions[1]
        security = [question1, question2, answer1, answer2]

        return security

    def change_password(self, user_email):
        cursor = self.conn.cursor()
        query = 'update users set password = crypt(%s, gen_salt(\'bf\')) where email = %s returning email, password;'
        cursor.execute(query, (user_email['password'], user_email['email']))
        info = cursor.fetchone()
        self.conn.commit()

        return info
