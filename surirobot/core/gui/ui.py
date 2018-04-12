from PyQt5.QtGui import QFont, QPixmap, QImage, QPalette, QColor, QIcon

from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSlot


class MainWindow(QDialog):
    NORMAL_IMAGE = 'res/SuriRobot1.png'
    MICRO_IMAGE = 'res/mic.png'
    BASIC_IMAGE = 'res/illustrations/activities/basic.jpg'
    LISTENING_IMAGE = 'res/illustrations/activities/listening2.jpg'

    SURI_BASIC = 0
    SURI_LISTENING = 1

    def __init__(self):
        QDialog.__init__(self)

        # Image
        self.image_map = [
            self.load_image(self.BASIC_IMAGE),
            self.load_image(self.LISTENING_IMAGE)
        ]

        self.imgWidget = QWidget(self)
        self.labelImage = QLabel(self.imgWidget)
        self.labelImage.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        image = self.image_map[self.SURI_BASIC]
        self.labelImage.setPixmap(QPixmap.fromImage(image))
        self.imgWidget.resize(image.height(), image.width())

        # Font
        f = QFont('Roboto', 16, QFont.Bold)

        # Text Up
        self.labelTextUp = QLabel(self)
        self.labelTextUp.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelTextUp.setFont(f)
        self.labelTextUp.setText("N/A")

        # Text Middle
        self.labelTextMiddle = QLabel(self)
        self.labelTextMiddle.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelTextMiddle.setFont(f)
        self.labelTextMiddle.setText("N/A")

        # Text Down
        self.labelTextDown = QLabel(self)
        self.labelTextDown.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelTextDown.setFont(f)
        self.labelTextDown.setText("N/A")

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

    def smartShow(self):
        self.showFullScreen()
        self.updateWidgets()
        # Timer display fixer
        displayFixer = QTimer(self)
        displayFixer.setInterval(1000)
        displayFixer.setSingleShot(True)
        displayFixer.timeout.connect(self.updateWidgets)
        displayFixer.start()

    def setTextUpFont(self, f):
        self.labelTextUp.setFont(f)
        self.updateWidgets()

    @pyqtSlot(str)
    def setTextUp(self, text):
        self.labelTextUp.setText(text)
        self.updateWidgets()

    @pyqtSlot(str)
    def setTextMiddle(self, text):
        self.labelTextMiddle.setText(text)
        self.updateWidgets()

    @pyqtSlot(str)
    def setTextDown(self, text):
        self.labelTextDown.setText(text)
        self.updateWidgets()

    @pyqtSlot(int)
    def setImage(self, image_id):
        image = self.image_map[image_id]
        self.labelImage.setPixmap(QPixmap.fromImage(image))
        self.imgWidget.resize(image.height(), image.width())
        self.updateWidgets()

    def setEditText(self):
        self.editText = QTextEdit()
        self.editText.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.editText.show()
        self.updateWidgets()

    def getEditText(self):
        return self.editText.toPlainText()

    def sendEditText(self):
        ###emit sendEditTextSignal(self.editText.toPlainText())
        pass

    @pyqtSlot()
    def updateWidgets(self):
        self.labelTextUp.adjustSize()
        self.labelTextMiddle.adjustSize()
        self.labelTextDown.adjustSize()

        self.labelTextUp.move(
            self.width() / 2 - self.labelTextUp.width() / 2,
            self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2
        )
        self.labelTextMiddle.move(
            self.width() / 2 - self.labelTextUp.width() / 2,
            self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2 + self.labelTextUp.height()
        )
        self.labelTextDown.move(
            self.width() / 2 - self.labelTextUp.width() / 2,
            self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2 + self.labelTextUp.height() + self.labelTextMiddle.height()
        )

        self.imgWidget.adjustSize()
        self.imgWidget.move(
            self.width() / 2 - self.imgWidget.width() / 2,
            self.height() / 3 - self.imgWidget.height() / 2
        )

    # SIGNALS

    def setTextUpSignal(self, text):
        self.setTextUp(text)
        self.updateWidgets()

    def setTextMiddleSignal(self, text):
        self.setTextMiddle(text)
        self.updateWidgets()

    def setTextDownSignal(self, text):
        self.setTextDown(text)
        self.updateWidgets()

    # Slots

    #def createManualWindow(self):
    #    manualW = manualWindow()
    #    manualW.show()
