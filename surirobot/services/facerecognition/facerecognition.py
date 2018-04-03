from PyQt5.QtCore import QThread, pyqtSignal
import os
import logging
import time
import face_recognition
from surirobot.core import serv_vc


class FaceRecognition(QThread):
    NB_IMG_PER_SECOND = 4

    UNKNOWN_FACE_ID = -1
    UNKNOWN_FACE_NAME = 'Unknown'

    person_changed = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.data = {}
        self.faces = []
        self.linker = []

        self.buffer = {
            'id': self.UNKNOWN_FACE_ID,
            'count': 0,
        }

    def __del__(self):
        self.wait()

    def run(self):
        face_locations = []
        face_encodings = []
        face_names = []
        tolerance = float(os.environ.get('FACERECO_TOLERANCE', '0.54'))

        time.sleep(3)

        while(True):
            time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
            small_frame = serv_vc.get_frame()

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(small_frame)
            # num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations, 10)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                match = face_recognition.compare_faces(self.faces, face_encoding, tolerance)
                id = self.UNKNOWN_FACE_ID

                for key, value in enumerate(match):
                    if value:
                        id = self.linker[key]
                        break
                face_names.append(id)

            self.addToBuffer(face_names)

    def addToBuffer(self, faces):
        if faces:
            id = faces[0]
        else:
            id = self.UNKNOWN_FACE_ID

        if id == self.buffer['id']:
            self.buffer['count'] = self.buffer['count'] + 1

            if self.buffer['id'] == self.UNKNOWN_FACE_ID:
                if self.buffer['count'] == 30:
                    self.emit_person_changed(id)
            else:
                if self.buffer['count'] == 5:
                    self.emit_person_changed(id)
        else:
            self.buffer['id'] = id
            self.buffer['count'] = 0

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
        self.logger.info("        Face encoding .....")
        face = face_recognition.face_encodings(img, None, 10)[0]

        self.faces.append(face)
        self.linker.append(picture.user.id)

    def remove_picture(self, picture):
        key = self.linker.index(picture.user.id)
        del self.faces[key]
        del self.linker[key]

    def id_to_name(self, id):
        if id == self.UNKNOWN_FACE_ID:
            return self.UNKNOWN_FACE_NAME

        return self.data[id]['name']
