#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.SettingsWindow import Ui_SettingsWindow
from components.setting_window.lyric_setting_page import LyricPage
from components.setting_window.hotkey_setting_page import HotkeysPage


class SettingWindow(QWidget, Ui_SettingsWindow):
    close_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(SettingWindow, self).__init__(parent)
        self.setupUi(self)

        self._init_page()
        self._init_signal()

    def _init_page(self):
        self.lyric_page = LyricPage(self)
        self.hotkeys_page = HotkeysPage()

        self.page_stackedWidget.addWidget(self.lyric_page)
        self.page_stackedWidget.addWidget(self.hotkeys_page)

    def _init_signal(self):
        self.page_listWidget.itemClicked.connect(self.page_click_event)

    def page_click_event(self, item: QListWidgetItem):
        index = self.page_listWidget.row(item)
        self.page_stackedWidget.setCurrentIndex(index)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_signal.emit(None)
        super(SettingWindow, self).closeEvent(a0)


if __name__ == "__main__":
    import sys

    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = SettingWindow()
    myWin.show()
    sys.exit(app.exec_())