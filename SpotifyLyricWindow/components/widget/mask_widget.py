#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class MaskWidget(QWidget):
    def __init__(self, parent=None):
        super(MaskWidget, self).__init__(parent=parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet('background:rgba(0,0,0,102);')
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.hide()

    def show(self):
        """重写show，设置遮罩大小与parent一致"""
        if self.parent() is None:
            return
        parent_rect = self.parent().geometry()
        self.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        super().show()
