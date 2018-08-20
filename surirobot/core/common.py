import logging
import os
import struct
import time
import traceback
import types
from functools import wraps

from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal

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
                if (int(os.environ.get('DEBUG', '0')) in [0, 1] and not (func.__name__ == 'set_camera' or (
                        type(wargs[0]).__name__ == 'VideoCapture' and func.__name__ == 'detect'))) or int(
                    os.environ.get('DEBUG', '0')) >= 2:
                    logger.debug('Slot called : {}.{} ({}) : {}'.format(type(wargs[0]).__name__, func.__name__,
                                                                        [item.__name__ for item in args], [
                                                                            type(item).__name__ if type(
                                                                                item) not in primitives else '{}:{}'.format(
                                                                                type(item).__name__, item) for item in
                                                                            wargs[1:]]))
                func(*wargs)
            except Exception as e:
                logger.error('{} occurred in slot'.format(type(e).__name__))
                traceback.print_exc()

        return wrapper

    return slotdecorator


class QSuperTimer(QTimer):
    started = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self):
        QTimer.__init__(self)
        self.start_time = 0
        self.elapsed_time = 0

    def start(self, p_int=None):
        self.start_time = time.time()
        self.elapsed_time = 0
        if p_int:
            super().start(p_int)
        else:
            super().start()
        self.started.emit()

    def stop(self):
        self.elapsed_time = 0
        super().stop()
        self.stopped.emit()

    def pause(self):
        self.elapsed_time += self.elapsed()
        self.stop()

    def resume(self):
        self.setSingleShot(True)
        self.timeout.connect(self._resume)
        self.start(self.interval() - (self.elapsed_time if self.elapsed_time > 0 else 0))

    @ehpyqtSlot
    def _resume(self):
        self.setSingleShot(False)
        self.timeout.disconnect(self._resume)
        self.start()

    def elapsed(self):
        """
        Return the elapsed time in msec
        :return: float
        """
        diff = time.time() - self.start_time
        return diff * 1000


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
    REDIS_NEW = 19
    REDIS_AVAILABLE = 20
