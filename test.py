import unittest

import xmlrunner

from app import app


class MyTestCase(unittest.TestCase):

    def test_something(self):
        client = app.test_client(self)
        response = client.get('/api/retrieve_messages/2')
        print(response)
        self.assertEqual(response.status_code, 400)  # add assertion here

        response = client.get('/api/retrieve_messages/2', query_string={'user_id': 2})
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
