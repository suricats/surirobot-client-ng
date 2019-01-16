from unittest import TestCase
import requests
from ffmpy import FFmpeg

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

        # Test the recording sample
        token = res.json()['access_token']
        headers = {"Authorization": "Bearer " + token}
        pp = requests.post("https://apiv4.beyondverbal.com/v4/recording/start",
                           json={"dataFormat": {"type": "WAV"}},
                           verify=False,
                           headers=headers)

        self.assertEqual(pp.status_code, 200)

        #Test the sending sample
        file_path = '/home/alain/workspace/surirobot-client-ng/surirobot/core/api/charlene.wav'
        recordingId = pp.json()['recordingId']
        new_file = file_path.split('.')[0] + '-format.wav'
        with open(new_file, 'rb') as wavdata:
            r = requests.post("https://apiv4.beyondverbal.com/v4/recording/"+recordingId,
                        data=wavdata,
                        verify=False,
                        headers=headers)
        self.assertEqual(r.status_code, 200)