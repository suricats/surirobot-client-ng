import os

import struct
import traceback
from PyQt5.QtCore import pyqtSlot
import types
from functools import wraps


def rawbytes(s):
    """Convert a string to raw bytes without encoding"""
    outlist = []
    for cp in s:
        num = ord(cp)
        if num < 255:
            outlist.append(struct.pack('b', num))
        elif num < 65535:
            outlist.append(struct.pack('>H', num))
        else:
            b = (num & 0xFF0000) >> 16
            H = num & 0xFFFF
            outlist.append(struct.pack('>bH', b, H))
    return b''.join(outlist)


def ehpyqtSlot(*args):
    if len(args) == 0 or isinstance(args[0], types.FunctionType):
        args = []

    @pyqtSlot(*args)
    def slotdecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args)
            except Exception as e:
                print('{} occured in slot'.format(type(e).__name__))
                traceback.print_exc()
        return wrapper
    return slotdecorator


class Dir():
    BASE = os.getcwd()
    TMP = BASE + '/tmp/'
    DATA = BASE + '/data/'
    PICTURES = DATA + 'pictures/'


class State():
    NO_STATE = -9999
    FACE_NOBODY = -2
    FACE_NOBODY_AVAILABLE = -3
    FACE_UNKNOWN = -1
    FACE_KNOWN = 0
    FACE_KNOWN_AVAILABLE = 1
    FACE_UNKNOWN_AVAILABLE = 2
    FACE_MULTIPLES = 3
    FACE_MULTIPLES_AVAILABLE = 4
    FACE_DATAVALUE_WORKING = 5
    FACE_DATAVALUE_NOT_WORKING = 6
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
