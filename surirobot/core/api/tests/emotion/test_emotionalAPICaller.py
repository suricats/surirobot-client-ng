import unittest
from unittest import TestCase
import doctest


class TestEmotionalAPICaller(TestCase):
    def setUp(self):
        from surirobot.core.api import EmotionalAPICaller
        self.emotion = EmotionalAPICaller()

    def test_analyse(self):
        self.fail()

    def test_save_results(self):
        self.fail()

    def test_getAnalysis(self):
        self.fail()

    def test_start(self):
        self.fail()


if __name__ == '__main__':
    unittest.main()
    doctest.testmod()