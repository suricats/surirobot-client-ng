from unittest import TestCase
import requests
import os

class TestEmotionalAPICaller(TestCase):
    def test_analyse(self):

        self.headers = {'Authorization': 'Token ', 'Content-Type': 'application/json'}
        response_analysis = requests.get('https://portal.azure.com/microsoft/analyse/',
                                         headers=self.headers)
        self.assertEqual(response_analysis.status_code, 200)

    def test_getAnalysis(self):

        # Test token verification
        res = requests.post("https://token.beyondverbal.com/token", data={"grant_type": "client_credentials",
                                         "apiKey": '76918380-3268-40be-8dc6-fba59804dd76'})
        self.assertEqual(res.status_code, 200)

        # Test the sample analysis
        token = res.json()['access_token']
        headers = {"Authorization": "Bearer " + token}
        pp = requests.post("https://apiv4.beyondverbal.com/v4/recording/start",
                           json={"dataFormat": {"type": "WAV"}},
                           verify=False,
                           headers=headers)

        self.assertEqual(pp.status_code, 200)
