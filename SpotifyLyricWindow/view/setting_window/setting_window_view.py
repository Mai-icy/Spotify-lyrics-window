#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt6 import QtGui
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from common.path import QSS_PATH
from common.config import Config
from components.widget.mask_widget import MaskWidget
from components.raw_ui import Ui_SettingsWindow
from view.setting_page.lyric_setting_page import LyricPage
from view.setting_page.hotkey_setting_page import HotkeysPage
from view.setting_page.common_setting_page import CommonPage
from view.setting_page.lyrics_manage_page import LyricsManagePage

import view.setting_window.lightstyle_rc

class SettingWindow(QWidget, Ui_SettingsWindow):
    close_signal = pyqtSignal(object)

    def __init__(self, parent=None, *, lyric_window=None):
        super(SettingWindow, self).__init__(parent)
        self.lyric_window = lyric_window
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # 在关闭的时候删除对象
        self.setupUi(self)

        self._init_page()
        self._init_signal()
        self._init_style_sheet()

    def _init_page(self):
        """初始化设置页面"""
        self.mask_ = MaskWidget(self)

        self.common_page = CommonPage(lyric_window=self.lyric_window, setting_window=self)
        self.lyric_page = LyricPage(lyric_window=self.lyric_window, setting_window=self)
        self.hotkeys_page = HotkeysPage(self)
        self.lyric_manage_page = LyricsManagePage(setting_window=self)

        self.page_stackedWidget.addWidget(self.common_page)
        self.page_stackedWidget.addWidget(self.hotkeys_page)
        self.page_stackedWidget.addWidget(self.lyric_page)
        self.page_stackedWidget.addWidget(self.lyric_manage_page)

    def _init_signal(self):
        """初始化信号"""
        self.page_listWidget.itemClicked.connect(self.page_click_event)

    def _init_style_sheet(self):
        with QSS_PATH.open("r") as f:
            style_sheet = f.read()
        self.setStyleSheet(style_sheet)

    def page_click_event(self, item: QListWidgetItem):
        """切换配置页面"""
        index = self.page_listWidget.row(item)
        self.page_stackedWidget.setCurrentIndex(index)

    def set_always_front(self, flag: bool):
        """
        设置窗口是否在最上层

        :param flag: True 为 在最上层
        """
        if not self.isHidden():
            self.hide()
            if flag:
                self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)

            self.show()
        else:
            if flag:
                self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)

    def show(self) -> None:
        # 载入配置
        self.lyric_page.load_config()
        self.hotkeys_page.load_config()
        self.common_page.load_config()

        self.lyric_manage_page.load_lyrics_file()

        self.lyric_window.set_hotkey_enable(False)

        super(SettingWindow, self).show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """关闭设置窗口"""
        # 歌词窗口 配置 始终和配置同步 快捷键需要先被关闭再打开
        self.lyric_window.set_hotkey_enable(True)
        # 保存配置
        Config.save_config()

        super(SettingWindow, self).closeEvent(a0)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    myWin = SettingWindow()
    myWin.show()
    sys.exit(app.exec())
