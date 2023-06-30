#!/usr/bin/python
# -*- coding:utf-8 -*-
import math

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from components.label import VerticalLabel, HorizontalLabel
from common.config import DisplayMode


class TextScrollArea(QScrollArea):
    def __init__(self, display_mode: DisplayMode, parent=None):
        super(TextScrollArea, self).__init__(parent)

        self.display_mode = display_mode

        self._init_roll()
        self._init_label()
        self._init_scroll_area()

    def _init_label(self):
        """初始化 label"""
        self.horizontal_label = HorizontalLabel()
        self.vertical_label = VerticalLabel()

        self.horizontal_label.setMouseTracking(True)
        self.vertical_label.setMouseTracking(True)

        self.horizontal_label.setMinimumSize(QSize(552, 38))
        self.vertical_label.setMinimumSize(QSize(38, 552))

        self.horizontal_label.setAlignment(Qt.AlignCenter)
        self.vertical_label.setAlignment(Qt.AlignCenter)
        # setAttribute(Qt.WA_TranslucentBackground, True)

    def _init_roll(self):
        """初始化 滚动相关参数"""
        self.timer_tick_lag = 20  # 刷新时间间隔
        self.roll_time_rate = 0.7  # 滚动速率

        # 每次滚动需要的参数
        self.move_step = 1  # 步长
        self.begin_tick = 0  # 开始滚动时间 不会马上开始滚动，稍微暂停的时间长度

        # 代表滚动进度以及滚动状态
        self.current_tick = 0
        self.is_roll = False

        self.horizontal_scrollbar = self.horizontalScrollBar()
        self.vertical_scrollbar = self.verticalScrollBar()

        self.roll_timer = QTimer()
        self.roll_timer.setInterval(self.timer_tick_lag)
        self.roll_timer.timeout.connect(self._tick_event)
        self.roll_timer.start()

    def _init_scroll_area(self):
        """初始化 滚动区域"""
        if self.display_mode == DisplayMode.Horizontal:
            self.setWidget(self.horizontal_label)
            self.setMinimumSize(QSize(552, 38))
        else:
            self.setWidget(self.vertical_label)
            self.setMinimumSize(QSize(38, 552))

        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.setStyleSheet('border:none;background-color:transparent;')
        self.viewport().setStyleSheet("background-color:transparent;")

    def set_text(self, text=''):
        """设置文本，滚动复位"""
        lyrics_label = self.get_current_label()
        lyrics_label.setText(text)
        self.get_current_scrollbar().setValue(0)  # 滚动条复位
        self.refresh_label_size()

        if self.is_roll:
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            self.setAlignment(Qt.AlignCenter)

    def set_roll_time(self, roll_time: int):
        """依据roll_time通过神奇的计算公式得到滚动需要的两个参数"""
        text_size = self.get_current_label().getTextSize()
        self.current_tick = 0
        if not roll_time:
            self.move_step = 0
            self.is_roll = False
            return

        if self.display_mode == DisplayMode.Horizontal:
            roll_distance = text_size - self.width()
        else:
            roll_distance = text_size - self.height()

        self.move_step = math.ceil(2 * (self.timer_tick_lag * roll_distance) / (roll_time * self.roll_time_rate))
        self.begin_tick = 0.5 * (1 - self.roll_time_rate) * roll_time // self.timer_tick_lag

    def refresh_label_size(self):
        """刷新文本框大小，防止卡住不动"""
        text_size = self.get_current_label().getTextSize()

        if self.display_mode == DisplayMode.Horizontal:
            self.is_roll = text_size > self.width()
        else:
            self.is_roll = text_size > self.height()

        lyrics_label = self.get_current_label()
        if not self.is_roll:
            lyrics_label.resize(self.size())
            lyrics_label.setAlignment(Qt.AlignCenter)
            self.setWidgetResizable(True)
        else:
            if self.display_mode == DisplayMode.Horizontal:
                lyrics_label.resize(QSize(text_size, self.height()))
            else:
                lyrics_label.resize(QSize(self.width(), text_size))
            lyrics_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setWidgetResizable(False)

    def get_current_label(self) -> QLabel:
        """获取当前使用的label"""
        return self.widget()

    def get_current_scrollbar(self) -> QScrollBar:
        """获取当前使用的scrollbar"""
        if self.display_mode == DisplayMode.Horizontal:
            return self.horizontal_scrollbar
        else:
            return self.vertical_scrollbar

    def set_label_stylesheet(self, stylesheet):
        self.horizontal_label.setStyleSheet(stylesheet)
        self.vertical_label.setStyleSheet(stylesheet)

    def setFont(self, font: QFont):
        self.horizontal_label.setFont(font)
        self.vertical_label.setFont(font)
        return super(TextScrollArea, self).setFont(font)

    def _tick_event(self):
        """滚动的实现， 作为计时器一次tick的时间值"""
        self.refresh_label_size()
        if self.is_roll:
            self.current_tick += 1
            if self.current_tick > self.begin_tick:
                # 滚动字幕
                scrollbar = self.get_current_scrollbar()
                scrollbar.setValue((self.current_tick - self.begin_tick) * self.move_step)

