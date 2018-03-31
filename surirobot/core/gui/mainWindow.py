# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(990, 680)
        self.frame = QtWidgets.QFrame(mainWindow)
        self.frame.setGeometry(QtCore.QRect(-40, 0, 1061, 691))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.labelImage = QtWidgets.QLabel(self.frame)
        self.labelImage.setGeometry(QtCore.QRect(270, 110, 401, 251))
        self.labelImage.setObjectName("labelImage")

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "mainWindow"))
        self.labelImage.setText(_translate("mainWindow", "<html><head/><body><p><br/></p></body></html>"))

