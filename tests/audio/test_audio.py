import unittest
import doctest

#from surirobot.core.api import ConverseApiCaller


def is_even(nbr):
    """
    Cette fonction teste si un nombre est pair.
    """
    return nbr % 2 == 0


class MyTest(unittest.TestCase):
    def test_is_even(self):
        self.assertTrue(is_even(2))
        self.assertEqual(is_even(0), True)
        #self.assertTrue(ConverseApiCaller.converse_audio())


if __name__ == '__main__':
    unittest.main()
    doctest.testmod()