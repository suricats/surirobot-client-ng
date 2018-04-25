from PyQt5.QtGui import QFont, QPixmap, QImage, QPalette, QColor, QIcon

from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QMainWindow, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSlot
from .new import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    NORMAL_IMAGE = 'res/SuriRobot1.png'
    MICRO_IMAGE = 'res/mic.png'
    BASIC_IMAGE = 'res/illustrations/activities/basic.jpg'
    LISTENING_IMAGE = 'res/illustrations/activities/listening2.jpg'

    SURI_BASIC = 0
    SURI_LISTENING = 1

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.setupUi(self)

        # Image
        self.image_map = [
            self.load_image(self.BASIC_IMAGE),
            self.load_image(self.LISTENING_IMAGE)
        ]

        self.image.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        image = self.image_map[self.SURI_BASIC]
        self.image.setPixmap(QPixmap.fromImage(image))
        self.imageWidget.resize(image.height(), image.width())

        # Font
        f = QFont('Roboto', 16, QFont.Bold)

        # Text Up
        self.labelUp.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelUp.setFont(f)
        self.labelUp.setText("N/A")

        # Text Middle
        self.labelMiddle = QLabel(self)
        self.labelMiddle.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelMiddle.setFont(f)
        self.labelMiddle.setText("N/A")

        # Text Down
        self.labelDown = QLabel(self)
        self.labelDown.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelDown.setFont(f)
        self.labelDown.setText("N/A")

        # Background color
        pal = QPalette()

        # set black background
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def load_image(self, image_path):
        image = QImage()
        image.load(image_path)
        return image

    # def smartShow(self):
    #     self.showFullScreen()
    #     self.updateWidgets()
    #     # Timer display fixer
    #     displayFixer = QTimer(self)
    #     displayFixer.setInterval(1000)
    #     displayFixer.setSingleShot(True)
    #     displayFixer.timeout.connect(self.updateWidgets)
    #     displayFixer.start()

    @pyqtSlot(str)
    def setTextUp(self, text):
        self.labelUp.setText(text)

    @pyqtSlot(str)
    def setTextMiddle(self, text):
        self.labelMiddle.setText(text)

    @pyqtSlot(str)
    def setTextDown(self, text):
        self.labelDown.setText(text)

    @pyqtSlot(int)
    def setImage(self, image_id):
        image = self.image_map[image_id]
        self.image.setPixmap(QPixmap.fromImage(image))
        self.imageWidget.resize(image.height(), image.width())

    # @pyqtSlot()
    # def updateWidgets(self):
    #     self.labelTextUp.adjustSize()
    #     self.labelTextMiddle.adjustSize()
    #     self.labelTextDown.adjustSize()
    #
    #     self.labelTextUp.move(
    #         self.width() / 2 - self.labelTextUp.width() / 2,
    #         self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2
    #     )
    #     self.labelTextMiddle.move(
    #         self.width() / 2 - self.labelTextUp.width() / 2,
    #         self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2 + self.labelTextUp.height()
    #     )
    #     self.labelTextDown.move(
    #         self.width() / 2 - self.labelTextUp.width() / 2,
    #         self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2 + self.labelTextUp.height() + self.labelTextMiddle.height()
    #     )
    #
    #     self.imgWidget.adjustSize()
    #     self.imgWidget.move(
    #         self.width() / 2 - self.imgWidget.width() / 2,
    #         self.height() / 3 - self.imgWidget.height() / 2
    #     )

    # SIGNALS

    def setTextUpSignal(self, text):
        self.setTextUp(text)

    def setTextMiddleSignal(self, text):
        self.setTextMiddle(text)

    def setTextDownSignal(self, text):
        self.setTextDown(text)

    # Slots

    #def createManualWindow(self):
    #    manualW = manualWindow()
    #    manualW.show()
