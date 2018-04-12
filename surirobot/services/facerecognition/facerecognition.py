from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import os
import logging
import time
import face_recognition
from surirobot.core import ui
from surirobot.services import serv_vc
from .counter import Counter
from surirobot.core.common import State


class FaceRecognition(QThread):
    updateState = pyqtSignal(str, int, dict)
    # deprecated signal -> will be removed
    person_changed = pyqtSignal(str)

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

        self.person_changed.connect(ui.setTextUp)

        self.data = {}
        self.faces = []
        self.linker = []

        self.counter_nobody = Counter(self.NB_IMG_PER_SECOND * 5)
        self.counter_nobody.timeout.connect(self.timer_nobody_timeout)
        self.counter_unknown = Counter(self.NB_IMG_PER_SECOND * 5)
        self.counter_unknown.timeout.connect(self.timer_unknown_timeout)
        self.counter_known = Counter(self.NB_IMG_PER_SECOND * 2)
        self.counter_known.timeout.connect(self.timer_known_timeout)

        self.state_id = self.NOBODY
        self.pretendent_id = self.NOBODY

        self.buffer = {
            'id': self.UNKNOWN,
            'count': 0,
        }

    def __del__(self):
        self.wait()

    def run(self):
        face_locations = []
        face_encodings = []
        tolerance = float(os.environ.get('FACERECO_TOLERANCE', '0.54'))

        time.sleep(3)

        self.emit_person_changed(self.NOBODY)
        self.emit_state_changed(self.NOBODY, self.NOBODY)

        while(True):
            time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
            small_frame = serv_vc.get_frame()

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(small_frame)
            # num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations, 2)

            if face_encodings:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces(self.faces, face_encodings[0], tolerance)
                id = self.UNKNOWN
                for key, value in enumerate(match):
                    if value:
                        id = self.linker[key]
                        break
                self.addToBuffer(id)
            else:
                self.addToBuffer(self.NOBODY)

    def addToBuffer(self, id):
        self.counter_nobody.increment()
        self.counter_unknown.increment()
        self.counter_known.increment()

        if id == self.NOBODY:
            self.pretendent_id = self.NOBODY
            self.counter_unknown.stop()
            self.counter_known.stop()

            if not self.counter_nobody.is_active():
                if self.state_id != self.NOBODY:
                    self.counter_nobody.start()

        elif id == self.UNKNOWN:
            self.pretendent_id = self.NOBODY
            self.counter_nobody.stop()
            self.counter_known.stop()

            if not self.counter_unknown.is_active():
                if self.state_id != self.UNKNOWN:
                    self.counter_unknown.start()

        else:
            self.counter_nobody.stop()
            self.counter_unknown.stop()

            if id == self.state_id:
                self.counter_known.stop()
            else:
                if id != self.pretendent_id:
                    self.pretendent_id = id
                    self.counter_known.start()

    @pyqtSlot()
    def timer_nobody_timeout(self):
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
        print('emit known ' + str(self.pretendent_id))
        self.state_id = self.pretendent_id
        self.pretendent_id = self.NOBODY
        self.emit_person_changed(self.state_id)
        self.emit_state_changed(State.STATE_FACE_KNOWN, self.state_id)

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
        self.person_changed.emit(name)

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
        #self.logger.info("Face encoding .....")
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
