import sys
from PyQt5.QtWidgets import QApplication
from .gui.ui import MainWindow

# Load QT
app = QApplication(sys.argv)
ui = MainWindow()
ui.smartShow()

# Start VideoCapture
from surirobot.services import VideoCapture
serv_vc = VideoCapture()
serv_vc.start()

# Start FaceRecognition
from surirobot.services.facerecognition import FaceRecognition
serv_fr = FaceRecognition()
serv_fr.start()
serv_fr.person_changed.connect(ui.setTextMiddle)

# Load faces from DB
from surirobot.services.facerecognition.loader import FaceLoader
face_loader = FaceLoader()
face_loader.start()

# Start AudioPlayer
from surirobot.services import AudioPlayer
serv_ap = AudioPlayer()
serv_ap.start()
