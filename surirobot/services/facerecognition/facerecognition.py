from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer
import os
import logging
import time
import face_recognition
from surirobot.core import ui
from surirobot.services import serv_vc
from surirobot.core.common import State


class FaceRecognition(QThread):
    updateState = pyqtSignal(str, int, dict)
    # deprecated signal -> will be removed
    signalPersonChanged = pyqtSignal(str)

    NB_IMG_PER_SECOND = 2
    MODULE_NAME = 'face'

    # STATE
    NOBODY = -2
    UNKNOWN = -1
    KNOWN = 0

    NOBODY_NAME = 'Nobody'
    UNKNOWN_NAME = 'Unknown'

    def __init__(self):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.signalPersonChanged.connect(ui.setTextUp)

        self.data = {}
        self.faces = []
        self.linker = []
        self.tolerance = float(os.environ.get('FACERECO_TOLERANCE', '0.54'))

        self.faceWorkLoop = QTimer()
        self.faceWorkLoop.timeout.connect(self.detect)

        self.nobodyTimer = QTimer()
        self.nobodyTimer.setSingleShot(True)
        self.nobodyTimerInterval = (1000/self.NB_IMG_PER_SECOND) * 6
        self.nobodyTimer.timeout.connect(self.nobodyTimeout)

        self.counter_unknown = QTimer()
        self.counter_unknown.setSingleShot(True)
        self.unknownTimerInterval = (1000/self.NB_IMG_PER_SECOND) * 12
        self.counter_unknown.timeout.connect(self.timer_unknown_timeout)

        self.counter_known = QTimer()
        self.counter_known.setSingleShot(True)
        self.knownTimerInterval = (1000/self.NB_IMG_PER_SECOND) * 5
        self.counter_known.timeout.connect(self.timer_known_timeout)

        self.state_id = self.NOBODY
        self.pretendent_id = self.NOBODY

        self.buffer = {
            'id': self.UNKNOWN,
            'count': 0,
        }

    def __del__(self):
        self.quit()

    def start(self):
        QThread.start(self)
        time.sleep(3)
        self.emit_person_changed(self.NOBODY)
        self.emit_state_changed(self.NOBODY, self.NOBODY)
        self.faceWorkLoop.start(1000/self.NB_IMG_PER_SECOND)

    @pyqtSlot()
    def detect(self):
        face_locations = []
        face_encodings = []
        small_frame = serv_vc.get_frame()

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(small_frame)
        # num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations, 2)
        if face_encodings:
            if len(face_encodings) > 1:
                self.emit_state_changed(State.STATE_FACE_MULTIPLES, self.UNKNOWN)
            else:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces(self.faces, face_encodings[0], self.tolerance)
                id = self.UNKNOWN
                match_tuples = list(enumerate(match))
                match_tuples = list(filter(lambda t: t[1], match_tuples))
                # print('match : ' + str(match))
                if len(match_tuples) == 0:
                    self.addToBuffer(self.UNKNOWN)
                elif len(match_tuples) == 1:
                    id = self.linker[match_tuples[0][0]]
                    self.addToBuffer(id)
        else:
            self.addToBuffer(self.NOBODY)

    def addToBuffer(self, id):
        # Case nobody is on the camera
        if id == self.NOBODY:
            self.pretendent_id = self.NOBODY
            self.counter_unknown.stop()
            self.counter_known.stop()

            if not self.nobodyTimer.isActive():
                if self.state_id != self.NOBODY:
                    self.nobodyTimer.start(self.nobodyTimerInterval)

        # Case an face is present but we don't know who is it
        elif id == self.UNKNOWN:
            self.pretendent_id = self.NOBODY
            self.nobodyTimer.stop()
            self.counter_known.stop()

            if not self.counter_unknown.isActive():
                if self.state_id != self.UNKNOWN:
                    self.counter_unknown.start(self.unknownTimerInterval)
                    self.emit_state_changed(State.STATE_FACE_WORKING, self.UNKNOWN)

        # Case an know person is present
        else:
            self.nobodyTimer.stop()
            self.counter_unknown.stop()

            if id == self.state_id:
                self.counter_known.stop()
            else:
                if id != self.pretendent_id:
                    self.pretendent_id = id
                    self.counter_known.start(self.knownTimerInterval)
                    self.emit_state_changed(State.STATE_FACE_WORKING, self.UNKNOWN)

    @pyqtSlot()
    def nobodyTimeout(self):
        self.state_id = self.NOBODY
        self.emit_person_changed(self.state_id)
        self.emit_state_changed(State.STATE_FACE_NOBODY, self.NOBODY)

    @pyqtSlot()
    def timer_unknown_timeout(self):
        self.state_id = self.UNKNOWN
        self.emit_person_changed(self.state_id)
        self.emit_state_changed(State.STATE_FACE_UNKNOWN, self.UNKNOWN)

    @pyqtSlot()
    def timer_known_timeout(self):
        if (not self.pretendent_id == self.NOBODY) and (not self.pretendent_id == self.UNKNOWN):
            print('emit known ' + str(self.pretendent_id))
            self.state_id = self.pretendent_id
            self.pretendent_id = self.NOBODY
            self.emit_person_changed(self.state_id)
            self.emit_state_changed(State.STATE_FACE_KNOWN, self.state_id)
        else:
            print('FaceReco : Error - invalid id')

    def emit_state_changed(self, state, id):
        if id == self.NOBODY or id == self.UNKNOWN:
            data = {}
        else:
            data = {
                'id': id,
                'firstname': self.id_to_firstname(id),
                'lastname': self.id_to_lastname(id),
                'name': self.id_to_name(id)
            }
        self.updateState.emit(self.MODULE_NAME, state, data)

    def emit_person_changed(self, id):
        name = self.id_to_name(id)
        print(name)
        self.signalPersonChanged.emit(name)

    def add_picture(self, picture):
        if picture.user.id in self.data:
            pass
        else:
            self.data[picture.user.id] = {
                'name': picture.user.firstname + ' ' + picture.user.lastname,
                'firstname': picture.user.firstname,
                'lastname': picture.user.lastname
            }

        img = face_recognition.load_image_file(picture.path)
        # self.logger.info("Face encoding .....")
        face = face_recognition.face_encodings(img, None, 10)[0]

        self.faces.append(face)
        self.linker.append(picture.user.id)

    def remove_picture(self, picture):
        key = self.linker.index(picture.user.id)
        del self.faces[key]
        del self.linker[key]

    def id_to_name(self, id):
        if id == self.UNKNOWN:
            return self.UNKNOWN_NAME
        if id == self.NOBODY:
            return self.NOBODY_NAME

        return self.data[id]['name']

    def id_to_firstname(self, id):
        if id == self.UNKNOWN:
            return self.UNKNOWN_NAME
        if id == self.NOBODY:
            return self.NOBODY_NAME

        return self.data[id]['firstname']

    def id_to_lastname(self, id):
        if id == self.UNKNOWN:
            return self.UNKNOWN_NAME
        if id == self.NOBODY:
            return self.NOBODY_NAME

        return self.data[id]['lastname']
