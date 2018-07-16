from PyQt5.QtCore import QObject, QThread
from surirobot.core.common import Dir


# Base class for API callers
class ApiCaller(QObject):
    TMP_DIR = Dir.TMP
    DEFAULT_LANGUAGE = 'fr'
    DEFAULT_LANGUAGE_EXT = 'fr-FR'

    def __init__(self, url='https://www.google.fr'):
        QObject.__init__(self)
        self.url = url
        self.currentThread = QThread()
        self.moveToThread(self.currentThread)

    def __del__(self):
        self.stop()

    def start(self):
        """
        Start the thread of the API caller
        """
        self.currentThread.start()

    def stop(self):
        """
        Stop the thread of the API caller
        """
        self.currentThread.quit()
