import os
import requests
import json
from unittest import TestCase


class TestTtsApiCaller(TestCase):
    def test_speak(self):

        # Test Local Voice SetUp
        self.local_voice = bool(int(os.environ.get('LOCAL_VOICE', True)))
        self.assertEqual(self.local_voice, True)

        # Test Playing Sound
        self.DEFAULT_LANGUAGE_EXT = 'fr-FR'
        self.data = {
                'text': 'Hello World',
                'language': self.DEFAULT_LANGUAGE_EXT
                }
        self.data = json.dumps(self.data)
        r = requests.get('https://memory.api.suricats-consulting.com/api/tts/speak/',
                         json=self.data)
        self.assertEqual(r.status_code, 200)
