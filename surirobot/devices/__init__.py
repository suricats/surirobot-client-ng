from PyQt5.QtCore import QThread

# Start AudioPlayer
from surirobot.devices.audioplayer import AudioPlayer
serv_ap = AudioPlayer()
serv_ap.start(QThread.HighestPriority)

# Start AudioRecorder
from surirobot.devices.audiorecorder import AudioRecorder
serv_ar = AudioRecorder()
serv_ar.start()

# Start VideoCapture
from surirobot.devices.videocapture import VideoCapture
serv_vc = VideoCapture()
serv_vc.start()