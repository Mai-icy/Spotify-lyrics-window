#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WarningDialog(object):
    def setupUi(self, WarningDialog):
        WarningDialog.setObjectName("WarningDialog")
        WarningDialog.resize(199, 133)
        self.verticalLayout = QtWidgets.QVBoxLayout(WarningDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.warning_label = QtWidgets.QLabel(WarningDialog)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(20)
        self.warning_label.setFont(font)
        self.warning_label.setTextFormat(QtCore.Qt.AutoText)
        self.warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.warning_label.setObjectName("warning_label")
        self.verticalLayout.addWidget(self.warning_label)
        self.buttonBox = QtWidgets.QDialogButtonBox(WarningDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(WarningDialog)
        self.buttonBox.accepted.connect(WarningDialog.accept)
        self.buttonBox.rejected.connect(WarningDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(WarningDialog)

    def retranslateUi(self, WarningDialog):
        _translate = QtCore.QCoreApplication.translate
        WarningDialog.setWindowTitle(_translate("WarningDialog", "警告"))
        self.warning_label.setText(_translate("WarningDialog", "TextLabel"))
