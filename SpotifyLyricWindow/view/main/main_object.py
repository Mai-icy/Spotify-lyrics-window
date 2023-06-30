#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from common.config import cfg, DisplayMode
from components.system_tray_icon.lyric_tray_icon import LyricsTrayIcon
from view.lyric_window.lyric_window_view import LyricsWindowView
from view.setting_window.setting_window_view import SettingWindowView
from view.lyric_manager_window.lyric_manager_view import LyricManagerView


class MainObject(QObject):
    def __init__(self, parent=None):
        super(MainObject, self).__init__(parent)

        hotkey_item_names = ["pause_hotkey", "last_song_hotkey", "next_song_hotkey",
                             "lock_hotkey", "calibrate_hotkey", "translate_hotkey",
                             "show_window_hotkey", "close_window_hotkey", "open_tool_hotkey"]
        # hotkey_signal_dict = {
        #     "pause_hotkey": self
        # }

        # self.hotkeys_system =

        self.tray_icon = LyricsTrayIcon()
        self.lyric_window = LyricsWindowView(cfg.get(cfg.display_mode))
        self.setting_window = None
        self.lyric_manager_window = None

        # self.lyric_window.set_hotkey_enable(True)
        self._init_lyric_window_signal()
        self._init_tray_icon_signal()

    def _init_tray_icon_signal(self):
        self.tray_icon.quit_signal.connect(self.quit_event)
        self.tray_icon.setting_window_show_signal.connect(self.setting_window_show_event)
        self.tray_icon.lyric_window_show_signal.connect(self.lyric_window_show_event)

    def _init_setting_window_signal(self):
        self.setting_window: SettingWindowView

        self.setting_window.lyric_color_changed.connect(self.lyric_window.set_lyrics_rgb)
        self.setting_window.shadow_color_changed.connect(self.lyric_window.set_shadow_rgb)
        self.setting_window.lyric_font_changed.connect(lambda font: self.lyric_window.set_font_family(font.family()))
        self.setting_window.display_mode_changed.connect(self.lyric_window_rebuild_event)
        self.setting_window.show_lyric_manager_signal.connect(self.lyric_manager_window_show_event)

    def _init_lyric_window_signal(self):
        self.lyric_window.lyric_window_show_signal.connect(self.lyric_window_show_event)
        self.lyric_window.setting_window_show_signal.connect(self.setting_window_show_event)
        self.lyric_window.quit_signal.connect(self.quit_event)

    def _init_lyric_manager_signal(self):
        ...

    def lyric_window_rebuild_event(self):
        """重新构建歌词窗口（运用于切换歌词窗口横竖模式）"""
        self.lyric_window.close()
        self.lyric_window.deleteLater()

        mode = cfg.get(cfg.display_mode)
        if mode == DisplayMode.Horizontal:
            default_pos = {
                "pos_x": 500,
                "pos_y": 900,
                "width": 800,
                "height": 150
            }
        else:
            default_pos = {
                "pos_x": 1200,
                "pos_y": 200,
                "width": 150,
                "height": 700
            }

        cfg.set(cfg.pos_x, default_pos["pos_x"])
        cfg.set(cfg.pos_y, default_pos["pos_y"])
        cfg.set(cfg.width, default_pos["width"])
        cfg.set(cfg.height, default_pos["height"])

        self.lyric_window = LyricsWindowView(mode)
        self._init_lyric_window_signal()
        self.lyric_window.show()

    def lyric_window_show_event(self):
        self.lyric_window.show()

    def setting_window_show_event(self):
        """显示设置窗口事件，新建一个窗口对象"""
        if self.setting_window is not None:
            self.setting_window.raise_()
            return
        self.setting_window = SettingWindowView()

        self.setting_window.destroyed.connect(self.setting_window_destroyed_event)
        self._init_setting_window_signal()
        self.setting_window.show()

    def lyric_manager_window_show_event(self):
        if self.lyric_manager_window is not None:
            self.lyric_manager_window.raise_()
            return
        self.lyric_manager_window = LyricManagerView()

        self.lyric_manager_window.destroyed.connect(self.lyric_manager_window_destroyed_event)
        self.lyric_manager_window.show()

    def setting_window_destroyed_event(self):
        """设置窗口关闭连接事件"""
        # 设置窗口已经关闭释放内存，此时self.setting_window为nullptr，将此处定义为None
        self.setting_window = None

    def lyric_manager_window_destroyed_event(self):
        self.lyric_manager_window = None

    def quit_event(self):
        """退出事件"""
        self.lyric_window.close()
        QtCore.QCoreApplication.exit(0)

    def show(self):
        self.lyric_window.show()
        self.tray_icon.show()

