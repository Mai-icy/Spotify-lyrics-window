#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.lyric_window import LyricsWindow
from components.lyric_window_view.lyrics_window_view import LyricsTrayIcon

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = LyricsWindow()
    tray = LyricsTrayIcon(myWin)
    tray.show()
    sys.exit(app.exec_())
