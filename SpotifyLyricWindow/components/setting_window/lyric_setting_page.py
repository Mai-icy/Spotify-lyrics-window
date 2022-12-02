#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsPage import Ui_LyricsPage

from common.config import Config

from components.lyric_window_view.lyrics_window_view import LyricsWindowView


class LyricPage(QWidget, Ui_LyricsPage):
    def __init__(self, parent=None, *, lyric_window: LyricsWindowView = None):
        super(LyricPage, self).__init__(parent)
        self.lyric_window = lyric_window
        self.setupUi(self)

        self._init_comboBox()
        self._init_signal()

    def _init_comboBox(self):
        # self.color_dict = {
        #     "红": "red",
        #     "蓝": "blue",
        #     "紫": "violet",
        #     "绿": "green",
        #     "橘": "orange",
        #     "黄": "yellow",
        #     "棕": "brown",
        #     "青": "cyan",
        #     "粉": "pink",
        #     "自定义": "other"
        # }
        self.color_list = ['red', 'blue', 'violet', 'green', 'orange', 'yellow', 'brown', 'cyan', 'pink', 'other']
        self.font_family_list = ["Ebrima", "Gadugi", "Leelawadee", "Leelawadee UI", "Lucida Sans Unicode", "MS Gothic",
                                 "MS Mincho", "MS PGothic", "MS PMincho", "MS UI Gothic", "Malgun Gothic",
                                 "Malgun Gothic Semilight", "Meiryo", "Meiryo UI", "Microsoft JhengHei UI",
                                 "Microsoft JhengHei UI Light", "Microsoft Sans Serif", "Microsoft YaHei UI",
                                 "Microsoft YaHei UI Light", "Nirmala UI", "Nirmala UI Semilight", "Segoe UI",
                                 "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Semilight", "SimSun-ExtB", "Tahoma",
                                 "Yu Gothic UI", "Yu Gothic UI Light", "Yu Gothic UI Semibold",
                                 "Yu Gothic UI Semilight", "仿宋", "华文中宋", "华文仿宋", "华文宋体", "华文彩云", "华文新魏",
                                 "华文楷体", "华文琥珀", "华文细黑", "华文行楷", "华文隶书", "宋体", "幼圆", "微软雅黑",
                                 "微软雅黑 Light", "新宋体", "方正姚体", "方正舒体", "楷体", "等线", "等线 Light", "隶书", "黑体"]
        self.color_comboBox.addItems(self.color_list)
        self.font_comboBox.addItems(self.font_family_list)

    def _init_signal(self):
        self.font_comboBox.currentIndexChanged.connect(self.font_change_event)
        self.color_comboBox.currentIndexChanged.connect(self.color_change_event)

        self.lyrics_default_button.clicked.connect(self.set_default_event)

    def load_config(self):
        color_style = Config.LyricConfig.rgb_style
        font_family = Config.LyricConfig.font_family
        is_always_front = Config.LyricConfig.is_always_front

        self.enable_front_checkBox.setChecked(is_always_front)
        self.color_comboBox.setCurrentIndex(self.color_list.index(color_style))
        self.font_comboBox.setCurrentIndex(self.font_family_list.index(font_family))

    def set_default_event(self):
        default_dict = Config.get_default_dict()["LyricConfig"]

        font_family = default_dict["font_family"]
        color_style = default_dict["rgb_style"]
        is_always_front = default_dict["is_always_front"]

        self.enable_front_checkBox.setChecked(is_always_front)
        self.color_comboBox.setCurrentIndex(self.color_list.index(color_style))
        self.font_comboBox.setCurrentIndex(self.font_family_list.index(font_family))

    def font_change_event(self):
        font_family = self.font_comboBox.currentText()
        self.lyric_window.set_font_family(font_family)
        setattr(Config.LyricConfig, "font_family", font_family)

    def color_change_event(self):
        color_style = self.color_comboBox.currentText()
        self.lyric_window.set_rgb_style(color_style)
        setattr(Config.LyricConfig, "rgb_style", color_style)









