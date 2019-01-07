from unittest import TestCase


class TestEmotionalAPICaller(TestCase):
    def test_analyse(self):
        self.file_path = "str"
        self.integer_file_path = 123
        self.assertEqual(self.file_path, "str", "Correct file path")
        self.assertNotEqual(self.integer_file_path, "str", "Wrong file path")
        self.assertTrue(self.file_path)

    def test_getAnalysis(self):
        self.file_path= "string"
        self.assertEqual(self.file_path, "string", "Correct")

    def test_start(self):
        self.setUp()
