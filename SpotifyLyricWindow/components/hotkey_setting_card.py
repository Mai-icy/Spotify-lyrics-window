#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QToolButton,
                             QVBoxLayout, QPushButton)

from qfluentwidgets import SettingCard, FluentIconBase, ConfigItem, qconfig

from components.line_edit.hotkeys_line_edit import HotkeyLineEdit


class HotkeySettingCard(SettingCard):
    """ Setting card with hotkey lineEdit """
    hotkeyChanged = pyqtSignal(object)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None,
                 configItem: ConfigItem = None, parent=None):
        super().__init__(icon, title, content, parent)
        self.iconLabel.hide()

        self.configItem = configItem
        self.hotkeyLineEdit = HotkeyLineEdit(self)
        self.hotkeyLineEdit.hotkey_changed.connect(self.setValue)

        self.hBoxLayout.addWidget(self.hotkeyLineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        if configItem:
            self.setValue(qconfig.get(configItem))
            configItem.valueChanged.connect(self.hotkeyChanged)

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.hotkeyLineEdit.set_hotkey(value)
