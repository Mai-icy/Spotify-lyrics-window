#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsManagePage import Ui_LyricsManage

from common.config import Config


class LyricsManagePage(QWidget, Ui_LyricsManage):
    def __init__(self, parent=None):
        super(LyricsManagePage, self).__init__(parent)
        self.setupUi(self)


