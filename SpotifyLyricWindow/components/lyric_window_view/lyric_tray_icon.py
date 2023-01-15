#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class LyricsTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, MainWindow=None, parent=None):
        super(LyricsTrayIcon, self).__init__(parent)
        self.main_window = MainWindow
        self._createMenu()
        self.activated.connect(self.clicked)

    def _createMenu(self):
        self.menu = QtWidgets.QMenu()
        if self.main_window:
            self.showAction = QtWidgets.QAction("Show(&S)", self, triggered=self.main_window.show)
            self.settingsAction = QtWidgets.QAction("Settings(&P)", self, triggered=self.show_settings)
            self.menu.addAction(self.showAction)
            self.menu.addAction(self.settingsAction)

        self.quitAction = QtWidgets.QAction("Quit(&X)", self, triggered=self.quit)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

        self.setIcon(QtGui.QIcon(u":/pic/images/LyricsIcon.png"))
        self.icon = self.MessageIcon()

    def set_window(self, window: QWidget):
        self.main_window = window
        self._createMenu()

    def clicked(self, reason):
        """1 right click, 2 double left click，3 left click，4 middle click"""
        if reason == 2 and self.main_window:
            self.main_window.show()

    def show_settings(self):
        if self.main_window:
            self.main_window.settings_button.clicked.emit(True)

    def quit(self):
        if self.main_window:
            self.main_window.close()
        # QtWidgets.qApp.quit()
        QtCore.QCoreApplication.exit(0)
