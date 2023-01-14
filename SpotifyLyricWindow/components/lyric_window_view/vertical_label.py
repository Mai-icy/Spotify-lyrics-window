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

        self.text_height = 0  # 记录文本高度 已用于绘画文本
        ascii_text = ""
        font_metrics = QFontMetrics(self.font())

        other_size = self.width() - font_metrics.height()
        paint_x = other_size  # 文本布局需要手动计算 将文本写于水平方向靠右

        # 以下目的为 ASCII字符横过来写，非ASCII字符竖着写
        for ch in self.text():
            if ch.isascii():
                ascii_text += ch
            else:
                painter.rotate(90)
                if ascii_text:
                    # painter 被旋转，坐标轴也会跟着变化 参考(x,y) 等价于 (y,-x) 10为补偿经验值
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

        self.text_height += 1 * font_metrics.height()  # 经验值 补偿

    def getTextSize(self):
        """获取当前播放歌词的高度, 可用于计算滚动参数"""
        return self.text_height
