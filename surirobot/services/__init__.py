from PyQt5.QtCore import QThread


# Start VideoCapture
from surirobot.services.videocapture import VideoCapture
serv_vc = VideoCapture()
serv_vc.start()

# Start FaceRecognition
from surirobot.services.facerecognition import FaceRecognition
serv_fr = FaceRecognition()
serv_fr.start()

# Load faces from DB
from surirobot.services.facerecognition.loader import FaceLoader
face_loader = FaceLoader()
face_loader.start(QThread.LowestPriority)

# Start AudioPlayer
from surirobot.services.audioplayer import AudioPlayer
serv_ap = AudioPlayer()
serv_ap.start(QThread.HighestPriority)

# Start AudioRecorder
from surirobot.services.audiorecorder import AudioRecorder
serv_ar = AudioRecorder()
serv_ar.start()
