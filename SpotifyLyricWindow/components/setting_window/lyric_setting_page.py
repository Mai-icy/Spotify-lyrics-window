#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsPage import Ui_LyricsPage

from common.config import Config
from common.lyric_type.lyric_decode import TransType


class LyricPage(QWidget, Ui_LyricsPage):
    def __init__(self, parent=None, *, lyric_window=None):
        super(LyricPage, self).__init__(parent)
        self.lyric_window = lyric_window
        self.setupUi(self)

        self._init_radioButton()
        self._init_comboBox()
        self._init_signal()

    def _init_comboBox(self):
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

    def _init_radioButton(self):
        self.trans_button_group = QButtonGroup()
        self.trans_button_group.addButton(self.non_trans_radioButton, id=0)
        self.trans_button_group.addButton(self.romaji_radioButton, id=1)
        self.trans_button_group.addButton(self.trans_radioButton, id=2)

    def _init_signal(self):
        self.font_comboBox.currentIndexChanged.connect(self.font_change_event)
        self.color_comboBox.currentIndexChanged.connect(self.color_change_event)

        self.trans_button_group.buttonClicked.connect(self.trans_change_event)
        self.enable_front_checkBox.stateChanged.connect(self.front_change_event)

        self.lyrics_default_button.clicked.connect(self.set_default_event)

    def load_config(self):
        color_style = Config.LyricConfig.rgb_style
        font_family = Config.LyricConfig.font_family
        is_always_front = Config.LyricConfig.is_always_front
        trans_type = Config.LyricConfig.trans_type

        self.enable_front_checkBox.setChecked(is_always_front)
        self.color_comboBox.setCurrentIndex(self.color_list.index(color_style))
        self.font_comboBox.setCurrentIndex(self.font_family_list.index(font_family))
        self.trans_button_group.button(trans_type).setChecked(True)

    def set_default_event(self):
        default_dict = Config.get_default_dict()["LyricConfig"]

        font_family = default_dict["font_family"]
        color_style = default_dict["rgb_style"]
        is_always_front = default_dict["is_always_front"]
        trans_type = default_dict["trans_type"]

        self.enable_front_checkBox.setChecked(is_always_front)
        self.color_comboBox.setCurrentIndex(self.color_list.index(color_style))
        self.font_comboBox.setCurrentIndex(self.font_family_list.index(font_family))

        self.trans_button_group.button(trans_type).setChecked(True)
        self.trans_change_event()

    def trans_change_event(self):
        trans_val = self.trans_button_group.checkedId()
        trans_type = TransType(trans_val)
        self.lyric_window.set_trans_mode(trans_type)

    def front_change_event(self):
        is_always_front = self.enable_front_checkBox.isChecked()
        self.lyric_window.set_always_front(is_always_front)
        setattr(Config.LyricConfig, "is_always_front", is_always_front)

    def font_change_event(self):
        font_family = self.font_comboBox.currentText()
        self.lyric_window.set_font_family(font_family)
        setattr(Config.LyricConfig, "font_family", font_family)

    def color_change_event(self):
        color_style = self.color_comboBox.currentText()
        self.lyric_window.set_rgb_style(color_style)
        setattr(Config.LyricConfig, "rgb_style", color_style)









