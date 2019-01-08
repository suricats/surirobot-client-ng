from unittest import TestCase
import requests


class TestConverseApiCaller(TestCase):
    def test_converse_audio(self):
        """
        self.file_path = "string"
        self.integer_file_path = 123
        self.assertEqual(self.file_path, "string", "Correct")
        self.assertNotEqual(self.integer_file_path, "string", "Uncorrect")
        """
        response_encoding = requests.get('https://converse.api.suricats-consulting.com/api/converse/text')
        self.assertEqual(response_encoding.status_code, 200)
