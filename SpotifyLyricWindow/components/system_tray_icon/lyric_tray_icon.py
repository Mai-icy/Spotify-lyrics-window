#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class LyricsTrayIcon(QtWidgets.QSystemTrayIcon):
    setting_window_show_signal = pyqtSignal()
    lyric_window_show_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(LyricsTrayIcon, self).__init__(parent)
        self._init_menu()
        self._init_signal()

        self.setIcon(QtGui.QIcon(u":/pic/images/LyricsIcon.png"))

    def _init_menu(self):
        self.menu = QtWidgets.QMenu()

        self.quit_action = QtWidgets.QAction("Quit(&X)", self)
        self.show_action = QtWidgets.QAction("Show(&S)", self)
        self.setting_action = QtWidgets.QAction("Settings(&P)", self)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.setting_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        self.setContextMenu(self.menu)

    def _init_signal(self):
        self.quit_action.triggered.connect(self.quit_event)
        self.show_action.triggered.connect(self.show_lyric_window_event)
        self.setting_action.triggered.connect(self.show_setting_window_event)

        self.activated.connect(self.clicked_event)

    def clicked_event(self, reason):
        """1 右键, 2 左键双击，3 左键，4 中键点击"""
        if reason == 2:
            self.show_lyric_window_event()

    def show_lyric_window_event(self):
        self.lyric_window_show_signal.emit()

    def show_setting_window_event(self):
        self.setting_window_show_signal.emit()

    def quit_event(self):
        self.quit_signal.emit()
        # QtWidgets.qApp.quit()
        QtCore.QCoreApplication.exit(0)
