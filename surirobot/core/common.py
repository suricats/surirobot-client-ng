import os

import struct
import traceback
from PyQt5.QtCore import pyqtSlot
import types
from functools import wraps
import logging

primitives = [int, str, bool, dict, list, float, tuple, set]
logger = logging.getLogger('COMMON')


def rawbytes(s):
    """
    Convert a string to raw bytes without encoding
    Parameters
    ----------
    s : str

    Returns
    -------
    bytearray
    """
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
    """
    Decorator that coats the :class:`PyQt5.QtCore.pyqtSlot` decorator and handles exceptions.
    """
    if len(args) == 0 or isinstance(args[0], types.FunctionType):
        args = []

    @pyqtSlot(*args)
    def slotdecorator(func):
        @wraps(func)
        def wrapper(*wargs):
            try:
                if (int(os.environ.get('DEBUG', '0')) in [0, 1] and not (func.__name__ == 'set_camera' or (type(wargs[0]).__name__ == 'VideoCapture' and func.__name__ == 'detect'))) or int(os.environ.get('DEBUG', '0')) >= 2:
                    logger.debug('Slot called : {}.{} ({}) : {}'.format(type(wargs[0]).__name__, func.__name__, [item.__name__ for item in args], [type(item).__name__ if type(item) not in primitives else '{}:{}'.format(type(item).__name__, item) for item in wargs[1:]]))
                func(*wargs)
            except Exception as e:
                logger.error('{} occurred in slot'.format(type(e).__name__))
                traceback.print_exc()
        return wrapper
    return slotdecorator


class Dir:
    """
    Store file and directory paths
    """
    BASE = os.getcwd()
    TMP = BASE + '/tmp/'
    DATA = BASE + '/data/'
    PICTURES = DATA + 'pictures/'
    LOG = BASE + '/log/'


class State:
    """
    List all the states that services can have
    """
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
    EMOTION_NEW = 15
    EMOTION_NO = 16
    KEYBOARD_NEW = 17
    KEYBOARD_AVAILABLE = 18
