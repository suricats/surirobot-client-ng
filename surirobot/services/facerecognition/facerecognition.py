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
    signalIndicator = pyqtSignal(str, str)
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
        self.faceWorkLoop.setInterval(1000/self.NB_IMG_PER_SECOND)

        self.nobodyTimer = QTimer()
        self.nobodyTimer.setSingleShot(True)
        self.nobodyTimer.setInterval((1000/self.NB_IMG_PER_SECOND) * 6)
        self.nobodyTimer.timeout.connect(self.nobodyTimeout)

        self.unknownTimer = QTimer()
        self.unknownTimer.setSingleShot(True)
        self.unknownTimer.setInterval((1000/self.NB_IMG_PER_SECOND) * 12)
        self.unknownTimer.timeout.connect(self.unknownTimeout)

        self.knownTimer = QTimer()
        self.knownTimer.setSingleShot(True)
        self.knownTimer.setInterval((1000/self.NB_IMG_PER_SECOND) * 5)
        self.knownTimer.timeout.connect(self.knownTimeout)

        self.stateId = self.NOBODY
        self.pretendentId = self.NOBODY

        self.buffer = {
            'id': self.UNKNOWN,
            'count': 0,
        }

    def __del__(self):
        self.quit()

    def start(self):
        QThread.start(self)
        time.sleep(3)
        self.personChanged(self.NOBODY)
        self.stateChanged(self.NOBODY, self.NOBODY)
        self.faceWorkLoop.start()

    @pyqtSlot()
    def detect(self):
        faceLocations = []
        faceEncodings = []
        smallFrame = serv_vc.get_frame()
        if smallFrame is None:
            self.signalIndicator.emit("face", "red")
        else:
            # Find all the faces and face encodings in the current frame of video
            faceLocations = face_recognition.face_locations(smallFrame)
            # num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
            faceEncodings = face_recognition.face_encodings(smallFrame, faceLocations, 2)
            if faceEncodings:
                if len(faceEncodings) > 1:
                    self.stateChanged(State.FACE_MULTIPLES)
                else:
                    # See if the face is a match for the known face(s)
                    match = face_recognition.compare_faces(self.faces, faceEncodings[0], self.tolerance)
                    id = self.UNKNOWN
                    # Transform in tuples of (index, value)
                    match = list(enumerate(match))
                    match = list(filter(lambda t: t[1], match))
                    # print('match : ' + str(match))
                    if len(match) == 0:
                        self.addToBuffer(self.UNKNOWN)
                    elif len(match) == 1:
                        id = self.linker[match[0][0]]
                        self.addToBuffer(id)
            else:
                self.addToBuffer(self.NOBODY)
        self.faceWorkLoop.setInterval(-time.time() % (1 / self.NB_IMG_PER_SECOND)*1000)

    def addToBuffer(self, id):
        # Case nobody is on the camera
        if id == self.NOBODY:
            self.pretendentId = self.NOBODY
            self.unknownTimer.stop()
            self.knownTimer.stop()

            if not self.nobodyTimer.isActive():
                if self.stateId != self.NOBODY:
                    self.nobodyTimer.start()

        # Case a face is present but we don't know who is it
        elif id == self.UNKNOWN:
            self.pretendentId = self.NOBODY
            self.nobodyTimer.stop()
            self.knownTimer.stop()

            if not self.unknownTimer.isActive():
                if self.stateId != self.UNKNOWN:
                    self.unknownTimer.start()
                    self.stateChanged(State.FACE_WORKING)

        # Case a know person is present
        else:
            self.nobodyTimer.stop()
            self.unknownTimer.stop()

            if id == self.stateId:
                self.knownTimer.stop()
            else:
                if id != self.pretendentId:
                    self.pretendentId = id
                    self.knownTimer.start()
                    self.stateChanged(State.FACE_WORKING)

    @pyqtSlot()
    def nobodyTimeout(self):
        self.stateId = self.NOBODY
        self.personChanged(self.stateId)
        self.stateChanged(State.FACE_NOBODY, self.NOBODY)

    @pyqtSlot()
    def unknownTimeout(self):
        self.signalIndicator.emit("face", "green")
        self.stateId = self.UNKNOWN
        self.personChanged(self.stateId)
        self.stateChanged(State.FACE_UNKNOWN, self.UNKNOWN)

    @pyqtSlot()
    def knownTimeout(self):
        self.signalIndicator.emit("face", "green")
        if (not self.pretendentId == self.NOBODY) and (not self.pretendentId == self.UNKNOWN):
            self.logger.info('Detection of ' + str(self.pretendentId))
            self.stateId = self.pretendentId
            self.pretendentId = self.NOBODY
            self.personChanged(self.stateId)
            self.stateChanged(State.FACE_KNOWN, self.stateId)
        else:
            self.logger.info('Error - invalid id')

    def stateChanged(self, state, id=None):
        if id == self.NOBODY or id == self.UNKNOWN or id is None:
            data = {}
        else:
            data = {
                'id': id,
                'firstname': self.idToFirstname(id),
                'lastname': self.idToLastname(id),
                'name': self.idToName(id)
            }
        self.updateState.emit(self.MODULE_NAME, state, data)

    def personChanged(self, id):
        name = self.idToName(id)
        print(name)
        self.signalPersonChanged.emit(name)

    def addPicture(self, picture):
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

    def removePicture(self, picture):
        key = self.linker.index(picture.user.id)
        del self.faces[key]
        del self.linker[key]

    def idToName(self, id):
        if id == self.UNKNOWN:
            return self.UNKNOWN_NAME
        if id == self.NOBODY:
            return self.NOBODY_NAME

        return self.data[id]['name']

    def idToFirstname(self, id):
        if id == self.UNKNOWN:
            return self.UNKNOWN_NAME
        if id == self.NOBODY:
            return self.NOBODY_NAME

        return self.data[id]['firstname']

    def idToLastname(self, id):
        if id == self.UNKNOWN:
            return self.UNKNOWN_NAME
        if id == self.NOBODY:
            return self.NOBODY_NAME

        return self.data[id]['lastname']
