#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class VerticalLabel(QLabel):
    def __init__(self, parent=None):
        super(VerticalLabel, self).__init__(parent)
        self.painter = QPainter(self)
        self.font_metrics = QFontMetrics(self.font())
        self.text_width = 0

    def paintEvent(self, a0: QPaintEvent) -> None:
        self.initPainter(self.painter)
        self.text_width = 0

        ascii_text = ""

        for ch in self.text():
            if not ch.isascii():
                ascii_text += ch
            else:
                self.painter.rotate(90)
                if ascii_text:
                    self.painter.drawText(QPoint(0, self.text_width), ascii_text)
                    self.text_width += self.font_metrics.width(ascii_text)
                    ascii_text = ""
                self.painter.rotate(-90)
                self.text_width += self.font_metrics.height()
                self.painter.drawText(QPoint(0, self.text_width), ch)
        self.painter.rotate(90)
        if ascii_text:
            self.painter.drawText(QPoint(0, self.text_width), ascii_text)
            self.text_width += self.font_metrics.width(ascii_text)
        self.painter.rotate(-90)
