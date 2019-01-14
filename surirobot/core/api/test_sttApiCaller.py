from unittest import TestCase
import os

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testdata.txt')

class TestSttApiCaller(TestCase):
    def test_recognize(self,):
        self.testopen = open(TESTDATA_FILENAME).read()
