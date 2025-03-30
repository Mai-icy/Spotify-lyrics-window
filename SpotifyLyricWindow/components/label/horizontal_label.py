#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt6 import QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class HorizontalLabel(QLabel):
    def __init__(self, parent=None):
        super(HorizontalLabel, self).__init__(parent)

    def getTextSize(self):
        """满足和竖向label同函数格式"""
        return QFontMetrics(self.font()).horizontalAdvance(self.text())
