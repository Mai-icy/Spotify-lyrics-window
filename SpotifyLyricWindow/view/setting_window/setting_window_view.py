#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStackedWidget, QHBoxLayout

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, MessageBox,
                            isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from common.config import Config
from view.setting_page.lyric_setting_page import LyricPage
from view.setting_page.hotkey_setting_page import HotkeysPage
from view.setting_page.common_setting_page import CommonPage
from view.setting_page.lyrics_manage_page import LyricsManagePage

from common.image.temp_manage import TempFileManage
from common.lyric import LyricFileManage


class SettingWindowView(FramelessWindow):
    execute_lyric_window_signal = pyqtSignal(object, object)  # (function, args)
    rebuild_lyric_window_signal = pyqtSignal()
    set_hotkey_signal = pyqtSignal(bool)

    lin = TempFileManage()
    lin2 = LyricFileManage()

    def __init__(self):
        super(SettingWindowView, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.setTitleBar(StandardTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        self.common_page = CommonPage(setting_window=self)
        self.lyric_page = LyricPage(setting_window=self)
        self.hotkeys_page = HotkeysPage(self)
        self.lyric_manage_page = LyricsManagePage(setting_window=self)

        self.initLayout()
        self.initNavigation()
        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.common_page, FIF.BOOK_SHELF, '常规')
        self.addSubInterface(self.hotkeys_page, FIF.ALBUM, '快捷键')
        self.addSubInterface(self.lyric_page, FIF.FONT, '歌词设置')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.lyric_manage_page, FIF.MUSIC, '歌词管理', NavigationItemPosition.SCROLL)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(1)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle('Setting')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox("test", self)
        w.exec()

    def show(self) -> None:
        # 载入配置
        self.lyric_page.load_config()
        self.hotkeys_page.load_config()
        self.common_page.load_config()

        self.lyric_manage_page.load_lyrics_file()

        self.set_hotkey_signal.emit(False)

        super(SettingWindowView, self).show()

    def closeEvent(self, a0) -> None:
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


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = SettingWindowView()
    w.show()
    app.exec_()
