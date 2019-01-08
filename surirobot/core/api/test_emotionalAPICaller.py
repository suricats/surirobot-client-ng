from unittest import TestCase
import requests


class TestEmotionalAPICaller(TestCase):
    def test_analyse(self):

        self.headers = {'Authorization': 'Token ', 'Content-Type': 'application/json'}
        response_analysis = requests.get('https://portal.azure.com/microsoft/analyse/',
                                         headers=self.headers)
        self.assertEqual(response_analysis.status_code, 200)

    def test_getAnalysis(self):
        self.file_path= "string"
        self.assertEqual(self.file_path, "string", "Correct")

    def test_start(self):
        self.setUp()
