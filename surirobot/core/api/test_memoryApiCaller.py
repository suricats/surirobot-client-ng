from unittest import TestCase

import requests


class TestMemoryApiCaller(TestCase):

    def test_get_users(self):
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        response_users = requests.get('http://memory.api.suricats-consulting.com/api/memory/users/ ',
                                      headers=self.headers)
        # Receive response
        self.assertEqual(response_users.status_code, 200)

    def test_get_encodings(self):
        response_encoding = requests.get('https://converse.api.suricats-consulting.com/api/memory/users/')
        self.assertEqual(response_encoding.status_code, 200)

    def test_get_notifications(self):
        response = requests.get('https://converse.api.suricats-consulting.com/api/notifications')
        self.assertEqual(response.status_code, 200)

    def test_get_last_sensor(self):
        self.setUp()

    def test_get_sensors(self):
        self.setUp()

    def test_add_user(self):
        self.setUp()

    def test_add_encoding(self):
        self.setUp()
