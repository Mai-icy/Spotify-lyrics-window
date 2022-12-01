#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsPage import Ui_LyricsPage

from common.config import Config


class LyricPage(QWidget, Ui_LyricsPage):
    def __init__(self, parent=None):
        super(LyricPage, self).__init__(parent)
        self.setupUi(self)

    def _init_signal(self):

        self.trans_checkBox.stateChanged.connect()
        self.romoji_checkBox.stateChanged.connect()

        self.color_comboBox.currentIndexChanged.connect(self.color_change_event)

    def checkbox_change(self):
        pass

    def color_change_event(self):
        font_family = self.color_comboBox.currentText()
        setattr(Config.LyricConfig, "font_family", font_family)









