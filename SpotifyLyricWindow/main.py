#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.lyric_window import LyricsWindow
import components.source


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    myWin = LyricsWindow()
    myWin.show()
    sys.exit(app.exec_())
