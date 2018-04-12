import os


class Dir():
    BASE = os.getcwd()
    TMP = BASE + '/tmp/'
    DATA = BASE + '/data/'
    PICTURES = DATA + 'pictures/'


class State():
    STATE_IDLE = 0
    STATE_DETECTED = 1
    STATE_NOT_DETECTED = 2
    STATE_WAITING_FOR_CONFIRMATION = 3
    STATE_CONFIRMATION_NO = 4
    STATE_CONFIRMATION_YES = 5
