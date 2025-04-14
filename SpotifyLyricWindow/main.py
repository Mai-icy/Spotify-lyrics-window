#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import platform

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from view.lyric_window.lyric_window import LyricsWindow
import components.source


if __name__ == "__main__":
    if platform.system() == "Linux" and os.getenv("XDG_SESSION_TYPE") == "wayland":
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    myWin = LyricsWindow()
    myWin.show()
    sys.exit(app.exec())
