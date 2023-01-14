#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class VerticalLabel(QLabel):
    def __init__(self, parent=None):
        super(VerticalLabel, self).__init__(parent)
        self.text_height = 0

    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)

        self.text_height = 0
        ascii_text = ""
        font_metrics = QFontMetrics(self.font())

        other_size = self.width() - font_metrics.height()
        paint_x = other_size

        for ch in self.text():
            if ch.isascii():
                ascii_text += ch
            else:
                painter.rotate(90)
                if ascii_text:
                    painter.drawText(QPoint(self.text_height, -paint_x - 10), ascii_text)
                    self.text_height += font_metrics.width(ascii_text)
                    ascii_text = ""
                painter.rotate(-90)
                self.text_height += font_metrics.height()
                painter.drawText(QPoint(paint_x, self.text_height), ch)
        painter.rotate(90)
        if ascii_text:
            painter.drawText(QPoint(self.text_height, -paint_x - 10), ascii_text)
            self.text_height += font_metrics.width(ascii_text)

        self.text_height += 0.5 * font_metrics.height()  # 经验值 补偿

    def getTextSize(self):
        return self.text_height
