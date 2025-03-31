#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class LyricsTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, MainWindow, parent=None):
        super(LyricsTrayIcon, self).__init__(parent)
        self.main_window = MainWindow
        self._createMenu()
        self.activated.connect(self.clicked)

    def _createMenu(self):
        self.menu = QtWidgets.QMenu()

        self.showAction = QtGui.QAction("Show(&S)", self, triggered=self.main_window.show)
        self.settingsAction = QtGui.QAction("Settings(&P)", self, triggered=self.show_settings)
        self.quitAction = QtGui.QAction("Quit(&X)", self, triggered=self.quit)
        self.menu.addAction(self.showAction)
        self.menu.addAction(self.settingsAction)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

        self.setIcon(QtGui.QIcon(u":/pic/images/LyricsIcon.png"))

    def clicked(self, reason):
        """1 right click, 2 double left click，3 left click，4 middle click"""
        if reason == 2:
            self.main_window.show()

    def show_settings(self):
        self.main_window.settings_button.clicked.emit(True)

    def quit(self):
        self.main_window.close()
        # QtWidgets.qApp.quit()
        QtCore.QCoreApplication.exit(0)
