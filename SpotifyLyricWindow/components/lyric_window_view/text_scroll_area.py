#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class TextScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super(QScrollArea, self).__init__(parent)
        self._init_roll()
        self._init_window()

    def _init_window(self):
        self._lyrics_label = QtWidgets.QLabel()
        self._lyrics_label.setObjectName("lyrics_label")
        self._lyrics_label.setMinimumSize(QSize(552, 38))
        # self._lyrics_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self._lyrics_label.setAlignment(Qt.AlignCenter)

        self.setWidget(self._lyrics_label)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet('border:none;background-color:transparent;')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumSize(QSize(552, 38))
        self.setWidgetResizable(True)
        self.viewport().setStyleSheet("background-color:transparent;")

    def _init_roll(self):
        self.text = ''
        self.text_index = 0
        self.text_width = 0
        self._is_roll = False
        self._scrollbar = self.horizontalScrollBar()

    def set_text(self, text='', width=0):
        self._resize_label(width)
        self._lyrics_label.setText(text)
        self.text = text
        self.text_index = 0
        self.text_width = width
        if width > self.width():
            self._is_roll = True
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            self._is_roll = False
            self.setAlignment(Qt.AlignCenter)
        self._scrollbar.setValue(0)  # 滚动条复位

    def set_font(self, font):
        self._lyrics_label.setFont(font)

    def set_mouse_track(self):
        self.setMouseTracking(True)
        self._lyrics_label.setMouseTracking(True)

    def _set_label_size(self):
        if not self._is_roll:
            self._lyrics_label.resize(self.size())
            self._lyrics_label.setAlignment(Qt.AlignCenter)
            self.setWidgetResizable(True)
        else:
            self._lyrics_label.resize(QSize(self.text_width, self.height()))
            self._lyrics_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setWidgetResizable(False)

    def update_index(self, begin_index, move_step):
        self._set_label_size()
        if self._is_roll:
            self.text_index += 1
            if self.text_index > begin_index:
                self._scrollbar.setValue((self.text_index - begin_index) * move_step)

    def _resize_label(self, new_text_width):
        self.text_width = new_text_width
        if new_text_width < self.width():
            self._is_roll = False
        else:
            self._is_roll = True
        self._set_label_size()

    def setCursor(self, union, cursor=None, Qt_CursorShape=None):
        self._lyrics_label.setCursor(union)
        return super().setCursor(union)

    def set_label_stylesheet(self, stylesheet):
        self._lyrics_label.setStyleSheet(stylesheet)
