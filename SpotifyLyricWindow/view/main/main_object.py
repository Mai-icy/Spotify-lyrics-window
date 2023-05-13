#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from common.config import Config
from common.typing import DisplayMode
from components.system_tray_icon.lyric_tray_icon import LyricsTrayIcon
from view.lyric_window.lyric_window_view import LyricsWindowView
from view.setting_window.setting_window_view import SettingWindowView


class MainObject(QObject):
    def __init__(self, parent=None):
        super(MainObject, self).__init__(parent)

        self.tray_icon = LyricsTrayIcon()
        self.lyric_window = LyricsWindowView()
        self.setting_window = None

        self.lyric_window.set_hotkey_enable(True)

        self._init_signal()

    def _init_signal(self):
        """初始化信号连接"""
        self.tray_icon.quit_signal.connect(self.quit_event)
        self.tray_icon.setting_window_show_signal.connect(self.setting_window_show_event)
        self.tray_icon.lyric_window_show_signal.connect(self.lyric_window_show_event)

        self.lyric_window.lyric_window_show_signal.connect(self.lyric_window_show_event)
        self.lyric_window.setting_window_show_signal.connect(self.setting_window_show_event)
        self.lyric_window.quit_signal.connect(self.quit_event)

    def execute_lyric_window_event(self, func, args):
        """设置窗口对歌词窗口的所有修改将被信号传递到最上级执行"""
        func(*args, lyric_window=self.lyric_window)

    def lyric_window_show_event(self):
        self.lyric_window.show()

    def lyric_window_rebuild_event(self):
        """重新构建歌词窗口（运用于切换歌词窗口横竖模式）"""
        self.lyric_window.close()
        self.lyric_window.deleteLater()

        mode = DisplayMode(Config.LyricConfig.display_mode)
        if mode == DisplayMode.Horizontal:
            default_pos = Config.get_default_dict()["CommonConfig"]["PositionConfig"]
        else:
            default_pos = {
                "pos_x": 1200,
                "pos_y": 200,
                "width": 150,
                "height": 700
            }
        Config.CommonConfig.PositionConfig.pos_x = default_pos["pos_x"]
        Config.CommonConfig.PositionConfig.pos_y = default_pos["pos_y"]
        Config.CommonConfig.PositionConfig.width = default_pos["width"]
        Config.CommonConfig.PositionConfig.height = default_pos["height"]

        self.lyric_window = LyricsWindowView()

        self.lyric_window.lyric_window_show_signal.connect(self.lyric_window_show_event)
        self.lyric_window.setting_window_show_signal.connect(self.setting_window_show_event)
        self.lyric_window.quit_signal.connect(self.quit_event)

        self.lyric_window.show()

    def setting_window_show_event(self):
        """显示设置窗口事件，新建一个窗口对象"""
        if self.setting_window is not None:
            return
        self.setting_window = SettingWindowView()

        self.setting_window.execute_lyric_window_signal.connect(self.execute_lyric_window_event)
        self.setting_window.rebuild_lyric_window_signal.connect(self.lyric_window_rebuild_event)
        self.setting_window.destroyed.connect(self.setting_window_destroyed_event)
        self.setting_window.set_hotkey_signal.connect(self.set_hotkey_event)

        self.setting_window.show()

    def setting_window_destroyed_event(self):
        """设置窗口关闭连接事件"""
        # 设置窗口已经关闭释放内存，此时self.setting_window为nullptr，将此处定义为None
        self.setting_window = None

    def set_hotkey_event(self, flag):
        """设置热键开启或者关闭事件"""
        self.lyric_window.set_hotkey_enable(flag)

    def quit_event(self):
        """退出事件"""
        self.lyric_window.close()
        QtCore.QCoreApplication.exit(0)

    def show(self):
        self.lyric_window.show()
        self.tray_icon.show()

