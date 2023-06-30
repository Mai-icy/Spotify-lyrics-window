#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QLocale, QTranslator, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QFont

from components.raw_ui.LyricsManagePage import Ui_LyricsManage


class LyricsManageInterface(QWidget, Ui_LyricsManage):
    def __init__(self, parent=None):
        super(LyricsManageInterface, self).__init__(parent)
        self.setupUi(self)


