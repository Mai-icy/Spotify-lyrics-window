#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from common.config import Config
from components.widget.mask_widget import MaskWidget
from components.raw_ui import Ui_SettingsWindow
from view.setting_page.lyric_setting_page import LyricPage
from view.setting_page.hotkey_setting_page import HotkeysPage
from view.setting_page.common_setting_page import CommonPage
from view.setting_page.lyrics_manage_page import LyricsManagePage

import view.setting_window.lightstyle_rc


class SettingWindowView(QWidget, Ui_SettingsWindow):

    execute_lyric_window_signal = pyqtSignal(object, object)  # (function, args)
    rebuild_lyric_window_signal = pyqtSignal()
    set_hotkey_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(SettingWindowView, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)  # 在关闭的时候删除对象
        self.setupUi(self)

        self._init_page()
        self._init_signal()
        self._init_style_sheet()

    def _init_page(self):
        """初始化设置页面"""
        self.mask_ = MaskWidget(self)

        self.common_page = CommonPage(setting_window=self)
        self.lyric_page = LyricPage(setting_window=self)
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
        with open("resource/ui/lightstyle.qss", "r") as f:
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
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()
        else:
            if flag:
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

    def show(self) -> None:
        # 载入配置
        self.lyric_page.load_config()
        self.hotkeys_page.load_config()
        self.common_page.load_config()

        self.lyric_manage_page.load_lyrics_file()

        self.set_hotkey_signal.emit(False)

        super(SettingWindowView, self).show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """关闭设置窗口"""
        # 歌词窗口 配置 始终和配置同步 快捷键需要先被关闭再打开
        self.set_hotkey_signal.emit(True)
        # 保存配置
        Config.save_config()

        super(SettingWindowView, self).closeEvent(a0)

    def create_sender(self, func, args=()):
        """将所有要操作歌词窗口的函数上传到最上级"""
        signal = self.execute_lyric_window_signal

        def sender():
            signal.emit(func, args)

        return sender


if __name__ == "__main__":
    import sys

    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = SettingWindowView()
    myWin.show()
    sys.exit(app.exec_())
