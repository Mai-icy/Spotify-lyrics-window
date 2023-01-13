#!/usr/bin/python
# -*- coding:utf-8 -*-
import math

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from components.lyric_window_view.vertical_label import VerticalLabel


class TextScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super(TextScrollArea, self).__init__(parent)
        self._init_roll()
        self._init_label()
        self._init_scroll_area()

        self.mode = 0

    def _init_roll(self):
        self.timer_tick_lag = 20  # 刷新时间间隔
        self.roll_time_rate = 0.7  # 滚动速率

        # 每次滚动需要的参数
        self.move_step = 1  # 步长
        self.begin_tick = 0  # 开始滚动时间 不会马上开始滚动，稍微暂停的时间长度

        # 代表滚动进度以及滚动状态
        self.current_tick = 0
        self.is_roll = False

        self.scrollbar = self.horizontalScrollBar()
        self.roll_timer = QTimer()
        self.roll_timer.setInterval(self.timer_tick_lag)
        self.roll_timer.timeout.connect(self._tick_event)
        self.roll_timer.start()

    def _init_label(self):
        self.horizontal_label = QLabel()
        self.vertical_label = VerticalLabel()

        self.horizontal_label.setMouseTracking(True)
        self.vertical_label.setMouseTracking(True)

        self.horizontal_label.setMinimumSize(QSize(552, 38))
        self.vertical_label.setMinimumSize(QSize(38, 552))

        self.horizontal_label.setAlignment(Qt.AlignCenter)
        self.vertical_label.setAlignment(Qt.AlignCenter)
        # setAttribute(Qt.WA_TranslucentBackground, True)

    def _init_scroll_area(self):
        self.setWidget(self.horizontal_label)

        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumSize(QSize(552, 38))
        self.setWidgetResizable(True)

        self.setStyleSheet('border:none;background-color:transparent;')
        self.viewport().setStyleSheet("background-color:transparent;")

    def set_text(self, text=''):
        lyrics_label = self.current_label()
        lyrics_label.setText(text)
        self.scrollbar.setValue(0)  # 滚动条复位
        self.refresh_label_size()

        if self.is_roll:
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            self.setAlignment(Qt.AlignCenter)

    def set_roll_time(self, roll_time: int):
        """依据roll_time通过神奇的计算公式得到滚动需要的两个参数"""
        text_width = self.get_text_width()
        roll_width = text_width - self.width()
        self.current_tick = 0
        if not roll_time:
            self.move_step = 0
            self.is_roll = False
            return
        self.move_step = math.ceil(2 * (self.timer_tick_lag * roll_width) / (roll_time * self.roll_time_rate))
        self.begin_tick = 0.5 * (1 - self.roll_time_rate) * roll_time // self.timer_tick_lag

    def get_text_width(self):
        text = self.current_label().text()
        return QFontMetrics(self.font()).width(text)

    def refresh_label_size(self):

        width = self.get_text_width()
        self.is_roll = width > self.width()
        lyrics_label = self.current_label()
        if not self.is_roll:
            lyrics_label.resize(self.size())
            lyrics_label.setAlignment(Qt.AlignCenter)
            self.setWidgetResizable(True)
        else:
            lyrics_label.resize(QSize(width, self.height()))
            lyrics_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setWidgetResizable(False)

    def _tick_event(self):
        self.refresh_label_size()
        if self.is_roll:
            self.current_tick += 1
            if self.current_tick > self.begin_tick:
                self.scrollbar.setValue((self.current_tick - self.begin_tick) * self.move_step)

    def current_label(self) -> QLabel:
        if self.mode == 0:
            return self.horizontal_label
        else:
            return self.vertical_label

    def set_label_stylesheet(self, stylesheet):
        self.horizontal_label.setStyleSheet(stylesheet)
        self.vertical_label.setStyleSheet(stylesheet)

    def setFont(self, font: QFont):
        self.horizontal_label.setFont(font)
        self.vertical_label.setFont(font)
        return super(TextScrollArea, self).setFont(font)
