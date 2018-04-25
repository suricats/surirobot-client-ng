from surirobot.services import serv_ap, serv_fr, serv_ar, face_loader, serv_emo
from PyQt5.QtCore import QObject, pyqtSlot


class Leaver(QObject):
    __instance__ = None

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):
        QObject.__init__(self)

    @pyqtSlot()
    def leaveAllThreads(self):
        print("Leaving app..")
        serv_ap.stop()
        serv_ap.quit()
        serv_fr.quit()
        serv_ar.quit()
        face_loader.quit()
        serv_emo.quit()
