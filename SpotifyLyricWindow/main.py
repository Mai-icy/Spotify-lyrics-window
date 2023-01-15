#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.lyric_window import LyricsWindow
from components.lyric_window_view.lyric_tray_icon import LyricsTrayIcon

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    icon = LyricsTrayIcon()
    myWin = LyricsWindow(icon=icon)
    icon.set_window(myWin)
    icon.show()
    myWin.show()
    sys.exit(app.exec_())
