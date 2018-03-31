from surirobot.services import VideoCapture, AudioPlayer, AudioRecorder
from surirobot.services.facerecognition import FaceRecognition


def init():
    global serv_vc
    serv_vc = VideoCapture()
    serv_vc.start()

    global serv_ap
    serv_ap = AudioPlayer()
    serv_ap.start()

    global serv_ar
    serv_ar = AudioRecorder()
    serv_ar.start()

    global serv_fr
    serv_fr = FaceRecognition()
    serv_fr.start()


def stop():
    serv_fr.stop()
    serv_vc.stop()
    serv_ap.stop()
    serv_ar.stop()
