import os


class Dir():
    BASE = os.getcwd()
    TMP = BASE + '/tmp/'
    DATA = BASE + '/data/'
    PICTURES = DATA + 'pictures/'


class State():
    FACE_NOBODY = -2
    FACE_NOBODY_AVAILABLE = -3
    FACE_UNKNOWN = -1
    FACE_KNOWN = 0
    FACE_KNOWN_AVAILABLE = 1
    FACE_UNKNOWN_AVAILABLE = 2
    FACE_MULTIPLES = 3
    FACE_MULTIPLES_AVAILABLE = 4
    FACE_WORKING = 5
    FACE_NOT_WORKING = 6
    SOUND_NEW = 6
    SOUND_AVAILABLE = 7
    CONVERSE_NEW = 8
    CONVERSE_AVAILABLE = 9
    SOUND_NEW = 10
    CONVERSE_NEW = 11
    SOUND_AVAILABLE = 12
    CONVERSE_AVAILABLE = 13
    EMOTION_NEW = 15
    EMOTION_NO = 16
    KEYBOARD_NEW = 17
    KEYBOARD_AVAILABLE = 18
