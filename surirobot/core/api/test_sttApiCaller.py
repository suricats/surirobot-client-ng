from unittest import TestCase
import requests
import os


class TestSttApiCaller(TestCase):
    def test_recognize(self, file_path='/home/alain/workspace/surirobot-client-ng/surirobot/core/api/charlene.wav'):
        with open(file_path, 'rb') as file:
            self.url = 'https://converse.api.suricats-consulting.com/api/stt/recognize'
            data = {'language': 'fr-FR'}

            r = requests.post(self.url, files={'audio': file}, data=data)
            self.assertEqual(r.status_code, 200)