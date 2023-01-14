#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class HorizontalLabel(QLabel):
    def __init__(self, parent=None):
        super(HorizontalLabel, self).__init__(parent)

    def getTextSize(self):
        """满足和竖向label同函数格式"""
        return QFontMetrics(self.font()).width(self.text())
