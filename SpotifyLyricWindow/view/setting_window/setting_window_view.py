#!/usr/bin/python
# -*- coding:utf-8 -*-

from PyQt6 import QtGui
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from common.config import Config
from components.widget.mask_widget import MaskWidget
from components.settings_ui import Ui_SettingsWindow, ASSET_PATH, scroll_page
from view.setting_page.lyric_setting_page import LyricPage
from view.setting_page.hotkey_setting_page import HotkeysPage
from view.setting_page.common_setting_page import CommonPage
from view.setting_page.lyrics_manage_page import LyricsManagePage


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
        self.page_listWidget.setCurrentRow(0)

    def _init_page(self):
        """初始化设置页面"""
        self.mask_ = MaskWidget(self)

        self.common_page = CommonPage(lyric_window=self.lyric_window, setting_window=self)
        self.lyric_page = LyricPage(lyric_window=self.lyric_window, setting_window=self)
        self.hotkeys_page = HotkeysPage(self)
        self.lyric_manage_page = LyricsManagePage(setting_window=self)

        self.page_stackedWidget.addWidget(scroll_page(self.common_page))
        self.page_stackedWidget.addWidget(scroll_page(self.hotkeys_page))
        self.page_stackedWidget.addWidget(scroll_page(self.lyric_page))
        self.page_stackedWidget.addWidget(self.lyric_manage_page)

    def _init_signal(self):
        """初始化信号"""
        self.page_listWidget.currentRowChanged.connect(self.page_change_event)
        # 等 Qt 更新系统调色板后再应用主题；窗口销毁时自动断开连接。
        QApplication.styleHints().colorSchemeChanged.connect(
            self._system_theme_event, Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def _system_theme_event(self):
        if Config.CommonConfig.settings_theme == 'system':
            self._init_style_sheet()

    def _init_style_sheet(self):
        dark = Config.CommonConfig.settings_theme == 'dark'
        if Config.CommonConfig.settings_theme == 'system':
            dark = QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        # 只设置当前窗口的调色板，子对话框继承；不影响桌面歌词或 QApplication。
        palette = QPalette(QApplication.palette())
        colors = {
            QPalette.ColorRole.Window: ('#f7f8fa', '#1e1e1e'),
            QPalette.ColorRole.Base: ('#ffffff', '#252526'),
            QPalette.ColorRole.AlternateBase: ('#f4f8f5', '#2a2a2a'),
            QPalette.ColorRole.Text: ('#283b39', '#cccccc'),
            QPalette.ColorRole.WindowText: ('#283b39', '#cccccc'),
            QPalette.ColorRole.Button: ('#ffffff', '#333333'),
            QPalette.ColorRole.ButtonText: ('#41584e', '#dddddd'),
            QPalette.ColorRole.Highlight: ('#d5e8de', '#264f78'),
            QPalette.ColorRole.HighlightedText: ('#183c32', '#e4effa'),
            QPalette.ColorRole.Link: ('#16775f', '#75beff'),
            QPalette.ColorRole.PlaceholderText: ('#74817d', '#909090'),
        }
        for role, values in colors.items():
            palette.setColor(role, QColor(values[int(dark)]))
        for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
            palette.setColor(QPalette.ColorGroup.Disabled, role, QColor('#777777' if dark else '#9aa69f'))
        with (ASSET_PATH / 'settings.qss').open(encoding='utf-8') as f:
            style_sheet = f.read().replace('@assets', ASSET_PATH.as_posix())
        if dark:
            with (ASSET_PATH / 'settings-dark.qss').open(encoding='utf-8') as f:
                style_sheet += '\n' + f.read().replace('@assets', ASSET_PATH.as_posix())
        self.setStyleSheet(style_sheet)
        self.ensurePolished()
        self.setPalette(palette)

    def page_change_event(self, index):
        if not 0 <= index < self.page_stackedWidget.count():
            return
        descriptions = (
            self.tr('管理窗口行为、歌词同步和 Spotify 连接。'),
            self.tr('不用离开当前应用，也能轻松控制歌词。'),
            self.tr('调整方向、字体与配色，找到舒服的阅读方式。'),
            self.tr('浏览、编辑与整理已经下载的歌词。'),
        )
        self.page_stackedWidget.setCurrentIndex(index)
        self.page_title.setText(self.page_listWidget.item(index).text())
        self.page_description.setText(descriptions[index])

    def page_click_event(self, item: QListWidgetItem):
        """切换配置页面"""
        index = self.page_listWidget.row(item)
        self.page_listWidget.setCurrentRow(index)

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
