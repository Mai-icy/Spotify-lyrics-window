#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsSettingsPage import Ui_LyricsSettingsPage

from common.config import Config
from common.lyric.lyric_type import TransType


class LyricPage(QWidget, Ui_LyricsSettingsPage):
    def __init__(self, parent=None, *, lyric_window=None, setting_window=None):
        super(LyricPage, self).__init__(parent)
        self.setting_window = setting_window
        self.lyric_window = lyric_window
        self.setupUi(self)

        self._init_radioButton()
        self._init_comboBox()
        self._init_colorDialog()
        self._init_signal()

    def _init_comboBox(self):
        """初始化下拉选框"""
        self.style_dict = {
            # color   lyrics_color    shadow_color
            "blue": ((86, 152, 195), (190, 190, 190)),
            "red": ((255, 77, 109), (150, 150, 150)),
            "violet": ((153, 111, 214), (150, 150, 150)),
            "green": ((152, 201, 163), (190, 190, 190)),
            "orange": ((255, 119, 61), (120, 120, 120)),
            "yellow": ((255, 225, 80), (150, 150, 150)),
            "brown": ((176, 137, 104), (150, 150, 150)),
            "cyan": ((61, 204, 199), (120, 120, 120)),
            "pink": ((237, 178, 209), (120, 120, 120))
        }
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
        """初始化翻译按钮"""
        self.trans_button_group = QButtonGroup()
        self.trans_button_group.addButton(self.non_trans_radioButton, id=0)
        self.trans_button_group.addButton(self.romaji_radioButton, id=1)
        self.trans_button_group.addButton(self.trans_radioButton, id=2)

    def _init_colorDialog(self):
        self.color_dialog = QColorDialog(self)

    def _init_signal(self):
        """初始化信号"""
        self.font_comboBox.currentIndexChanged.connect(self.font_change_event)
        self.color_comboBox.currentIndexChanged.connect(self.color_style_change_event)

        self.trans_button_group.buttonClicked.connect(self.trans_change_event)
        self.enable_front_checkBox.stateChanged.connect(self.front_change_event)

        self.lyrics_color_button.clicked.connect(self.custom_lyrics_color_event)
        self.shadow_color_button.clicked.connect(self.custom_shadow_color_event)

        self.lyrics_default_button.clicked.connect(self.set_default_event)

    def load_config(self):
        """导入配置"""
        color_style = Config.LyricConfig.rgb_style
        font_family = Config.LyricConfig.font_family
        is_always_front = Config.LyricConfig.is_always_front
        trans_type = Config.LyricConfig.trans_type

        self.enable_front_checkBox.setChecked(is_always_front)
        self.color_comboBox.setCurrentIndex(self.color_list.index(color_style))
        self.font_comboBox.setCurrentIndex(self.font_family_list.index(font_family))
        self.trans_button_group.button(trans_type).setChecked(True)

    def set_default_event(self):
        """恢复默认值事件"""
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
        """切换翻译"""
        trans_val = self.trans_button_group.checkedId()
        trans_type = TransType(trans_val)
        # 同步到歌词窗口
        self.lyric_window.set_trans_mode(trans_type)

    def front_change_event(self):
        """修改置顶事件"""
        is_always_front = self.enable_front_checkBox.isChecked()
        # 同步到歌词窗口
        self.lyric_window.set_always_front(is_always_front)
        setattr(Config.LyricConfig, "is_always_front", is_always_front)

    def font_change_event(self):
        """修改字体事件"""
        font_family = self.font_comboBox.currentText()
        # 同步到歌词窗口
        self.lyric_window.set_font_family(font_family)
        setattr(Config.LyricConfig, "font_family", font_family)

    def color_style_change_event(self):
        """修改歌词颜色方案事件"""
        color_style = self.color_comboBox.currentText()
        if color_style == "other":
            lyrics_color = Config.LyricConfig.lyric_color
            shadow_color = Config.LyricConfig.shadow_color
            self._set_label_rgb(self.lyrics_color_label, lyrics_color)
            self._set_label_rgb(self.shadow_color_label, shadow_color)

            setattr(Config.LyricConfig, "rgb_style", "other")
            return

        # 同步到歌词窗口
        self.lyric_window.set_rgb_style(color_style)
        self._set_label_rgb(self.lyrics_color_label, self.style_dict[color_style][0])
        self._set_label_rgb(self.shadow_color_label, self.style_dict[color_style][1])

        setattr(Config.LyricConfig, "rgb_style", color_style)
        setattr(Config.LyricConfig, "lyric_color", self.style_dict[color_style][0])
        setattr(Config.LyricConfig, "shadow_color", self.style_dict[color_style][1])

    def custom_lyrics_color_event(self):
        """自定义歌词颜色事件"""
        if self.color_comboBox.currentText() != "other":
            self.color_comboBox.setCurrentIndex(self.color_list.index("other"))

        lyric_rgb = Config.LyricConfig.lyric_color
        now_color = QColor(*lyric_rgb)

        self.setting_window.mask_.show()
        new_color = self.color_dialog.getColor(now_color)
        self.setting_window.mask_.hide()

        color = (new_color.red(), new_color.green(), new_color.blue())
        self.lyric_window.set_lyrics_rgb(color)

        self._set_label_rgb(self.lyrics_color_label, color)
        setattr(Config.LyricConfig, "lyric_color", color)

    def custom_shadow_color_event(self):
        """自定义阴影颜色事件"""
        if self.color_comboBox.currentText() != "other":
            self.color_comboBox.setCurrentIndex(self.color_list.index("other"))

        shadow_color = Config.LyricConfig.shadow_color
        now_color = QColor(*shadow_color)

        self.setting_window.mask_.show()
        new_color = self.color_dialog.getColor(now_color)
        self.setting_window.mask_.hide()

        color = (new_color.red(), new_color.green(), new_color.blue())
        self.lyric_window.set_shadow_rgb(color)

        self._set_label_rgb(self.shadow_color_label, color)
        setattr(Config.LyricConfig, "shadow_color", color)

    @staticmethod
    def _set_label_rgb(label: QLabel, rgb: tuple):
        """
        为label设置颜色

        :param rgb: 对应的rgb颜色值 例如 (237, 178, 209)
        """
        stylesheet = f"background:rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
        label.setStyleSheet(stylesheet)





