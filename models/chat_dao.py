from decorators import exception_handler
from models.main_dao import MainDao


class ChatDao(MainDao):

    @exception_handler
    def create_message(self, data):
        cursor = self.conn.cursor()
        query = 'insert into messages (sender_id, receiver_id, job_id, content) values (%s, %s, %s, %s) ' \
                'returning msg_id, sender_id, receiver_id, job_id, content, date'
        cursor.execute(query, (data['sender_id'], data['receiver_id'], data['job_id'], data['content']))
        message = cursor.fetchone()
        self.conn.commit()
        return message, None

    @exception_handler
    def get_job_messages(self, data):
        cursor = self.conn.cursor()
        query = 'select msg_id, sender_id, receiver_id, job_id, content, date, S.first_name, S.last_name, ' \
                'R.first_name, R.last_name ' \
                'from messages as M' \
                '   inner join users as S on M.sender_id=S.user_id ' \
                '   inner join users as R on M.receiver_id=R.user_id ' \
                'where job_id=%s ' \
                'order by date asc;'

        cursor.execute(query, (data['job_id'], ))
        messages = self.convert_to_list(cursor)
        if messages.__len__() == 0:
            return None, None

        return messages, None

