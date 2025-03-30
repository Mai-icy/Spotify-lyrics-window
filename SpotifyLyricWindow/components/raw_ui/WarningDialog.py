#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialogButtonBox
from PyQt6.QtCore import Qt


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
        # 设置文本格式和对齐方式
        self.warning_label.setTextFormat(Qt.TextFormat.AutoText)
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 设置对象名称
        self.warning_label.setObjectName("warning_label")

        # 将标签添加到布局中
        self.verticalLayout.addWidget(self.warning_label)

        # 创建按钮框
        self.buttonBox = QDialogButtonBox(WarningDialog)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
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
