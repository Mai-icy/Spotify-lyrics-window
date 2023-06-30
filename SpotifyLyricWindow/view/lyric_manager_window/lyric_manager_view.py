#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QLocale, QTranslator, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QFont

from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import isDarkTheme, FluentTranslator
from common.config import cfg
from view.lyric_manager_window.lyric_manager_interface import LyricsManageInterface


class LyricManagerView(FramelessWindow):
    def __init__(self, parent=None):
        super(LyricManagerView, self).__init__(parent)
        self.setTitleBar(StandardTitleBar(self))
        self.setWindowTitle(self.tr("Lyric Manager"))
        self.hBoxLayout = QHBoxLayout(self)

        self.lyric_manager_interface = LyricsManageInterface(self)

        self.hBoxLayout.setContentsMargins(0, 25, 0, 0)
        self.hBoxLayout.addWidget(self.lyric_manager_interface)

        self.setAttribute(Qt.WA_DeleteOnClose)
        cfg.themeChanged.connect(self.setQss)
        self.setQss()

    def setQss(self):
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

