#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from qfluentwidgets import LineEdit


class HotkeyLineEdit(LineEdit):
    hotkey_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super(HotkeyLineEdit, self).__init__(parent)
        self.unvalidated = False
        self.start_record = False

        self.current_hot_keys = []

        self.setReadOnly(True)

    def get_hotkey(self):
        return self.current_hot_keys

    def set_hotkey(self, hotkey: list):
        if hotkey == self.current_hot_keys:
            if not hotkey:
                self.setText("None")
            return
        self.current_hot_keys = hotkey
        self.hotkey_changed.emit(hotkey)
        if not hotkey:
            self.setText("None")
            return

        forward_dict = {
            "left": "←",
            "right": "→",
            "up": "↑",
            "down": "↓"
        }
        show_keys = []
        for key_ in hotkey:
            if key_ in forward_dict.keys():
                show_keys.append(forward_dict[key_])
            else:
                show_keys.append(key_.capitalize())

        self.setText(" + ".join(show_keys))

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """防止焦点外放后 使输入停止 从而一直显示非法热键"""
        if self.unvalidated:
            self.set_hotkey([])
            self.unvalidated = False
            return
        super(HotkeyLineEdit, self).focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """捕获快捷键"""
        self.start_record = True
        key_value = event.key()
        other_key_dict = {
            Qt.Key_Left: "left",
            Qt.Key_Right: "right",
            Qt.Key_Up: "up",
            Qt.Key_Down: "down"
        }
        modifier_dict = {
            Qt.AltModifier: ["alt"],
            Qt.ShiftModifier: ["shift"],
            Qt.ControlModifier: ["ctrl"],
            (Qt.ControlModifier | Qt.AltModifier): ["ctrl", "alt"],
            (Qt.ShiftModifier | Qt.ControlModifier): ["ctrl", "shift"],
            (Qt.ShiftModifier | Qt.AltModifier): ["shift", "alt"],
            (Qt.ShiftModifier | Qt.AltModifier | Qt.ControlModifier): ["ctrl", "shift", "alt"]
        }

        key = modifiers = None

        if 32 <= key_value <= 127:
            key = chr(key_value).lower()
        elif key_value in other_key_dict:
            key = other_key_dict[key_value]

        if event.modifiers() in modifier_dict:
            modifiers = modifier_dict[event.modifiers()]

        if modifiers and not key:
            self.setText(" + ".join(modify.capitalize() for modify in modifiers))
            self.unvalidated = True
        if modifiers and key and "ctrl" not in modifiers:  # 使用的热键第三方库不支持ctrl
            self.set_hotkey(modifiers + [key])
            self.unvalidated = False

        if event.key() == Qt.Key_Escape:
            self.unvalidated = True

        # 使用的热键第三方库不支持ctrl
        if "ctrl" in modifiers:
            self.unvalidated = True

        super(HotkeyLineEdit, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """松开按键检验是否合法 保存显示合法按键"""
        if not self.start_record:
            return

        if self.unvalidated:
            self.set_hotkey([])
            self.unvalidated = False
            return

        self.start_record = False
        super(HotkeyLineEdit, self).keyReleaseEvent(event)
