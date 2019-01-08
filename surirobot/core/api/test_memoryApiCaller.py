from unittest import TestCase

import requests


class TestMemoryApiCaller(TestCase):

    def test_get_users(self):
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        self.response_users = requests.get('http://memory.api.suricats-consulting.com/api/memory/users/',
                                      headers=self.headers)
        # Receive response
        self.assertEqual(self.response_users.status_code, 200)

    def test_get_encodings(self):
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        response_encoding = requests.get('https://memory.api.suricats-consulting.com/api/memory/encodings/',
                                         headers=self.headers)
        self.assertEqual(response_encoding.status_code, 200)

    def test_get_notifications(self):
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        response_notifications = requests.get('https://memory.api.suricats-consulting.com/api/notifications/',
                                         headers=self.headers)
        self.assertEqual(response_notifications.status_code, 200)

    def test_get_last_sensor(self):
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        response_last_sensor = requests.get('https://memory.api.suricats-consulting.com/api/memory/sensors/last',
                                         headers=self.headers)
        self.assertEqual(response_last_sensor.status_code, 200)

    def test_get_sensors(self):
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        response_sensor = requests.get('https://memory.api.suricats-consulting.com/api/memory/sensors/',
                                         headers=self.headers)
        self.assertEqual(response_sensor.status_code, 200)

    def test_add_user(self):
        data = {"firstname": 'firstname', "lastname": 'lastname', "email": 'toto.test@suricats-consulting.com'}
        token = '4d060171dce2fb7add839c93e9b1d10509a52257'
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
        response_add_user = requests.get('https://memory.api.suricats-consulting.com/api/memory/users/',
                                         json=data,
                                         headers=self.headers)
        self.assertEqual(response_add_user.status_code, 200)