from unittest import TestCase


class TestConverseApiCaller(TestCase):
    def test_converse_audio(self):
        self.file_path = "string"
        self.integer_file_path = 123
        self.assertEqual(self.file_path, "string", "Correct")
        self.assertNotEqual(self.integer_file_path, "string", "Uncorrect")

    def test_start(self):
        self.setUp()

    def test_stop(self):
        self.setUp()
