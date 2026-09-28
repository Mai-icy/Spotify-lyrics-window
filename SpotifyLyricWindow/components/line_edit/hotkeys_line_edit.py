#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from common.config import Config


class HotkeyLineEdit(QLineEdit):
    hotkeys_conflict_signal = pyqtSignal(str)

    def __init__(self, signal_key, parent=None):
        super(HotkeyLineEdit, self).__init__(parent)
        self.unvalidated = False
        self.start_record = False

        self.signal_key = signal_key
        self.current_hot_keys = []

        self.setReadOnly(True)
        self.setPlaceholderText(self.tr('未设置'))

    def get_signal_key(self) -> str:
        return self.signal_key

    def set_hotkey(self, hotkey: list):
        """
        设置该输入框对应的快捷键，会保存至配置文件

        :param hotkey: 快捷键组合 例如： ["ctrl", "a"]
        """
        self.unvalidated = False
        self.start_record = False
        hotkey = ['space' if key == ' ' else key for key in hotkey]
        # 判断是否冲突
        hotkeys_dict = Config.to_dict().get("HotkeyConfig", {})
        for signal_key in hotkeys_dict.keys():
            if hotkey and signal_key != self.signal_key and hotkeys_dict[signal_key] == hotkey:
                # signal_key 为冲突的热键信号名
                self.hotkeys_conflict_signal.emit(signal_key)
                # HotkeysPage 负责接收信号并进行处理
                break

        self.current_hot_keys = hotkey
        if not hotkey:
            self.clear()
            setattr(Config.HotkeyConfig, self.signal_key, [])
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
        setattr(Config.HotkeyConfig, self.signal_key, self.current_hot_keys)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """防止焦点外放后 使输入停止 从而一直显示非法热键"""
        self.start_record = False
        if self.unvalidated:
            self.set_hotkey([])
        super(HotkeyLineEdit, self).focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """捕获快捷键"""
        self.start_record = True
        key_value = event.key()

        other_key_dict = {
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_Right: "right",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_Down: "down"
        }

        modifier_dict = {
            Qt.KeyboardModifier.AltModifier: ["alt"],
            Qt.KeyboardModifier.ShiftModifier: ["shift"],
            Qt.KeyboardModifier.ControlModifier: ["ctrl"],
            (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier): ["ctrl", "alt"],
            (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier): ["ctrl", "shift"],
            (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.AltModifier): ["shift", "alt"],
            (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.ControlModifier)
            : ["ctrl", "shift", "alt"]
        }

        key = modifiers = None

        if 33 <= key_value <= 127:
            key = chr(key_value).lower()
        elif key_value in other_key_dict:
            key = other_key_dict[key_value]

        if event.modifiers() in modifier_dict:
            modifiers = modifier_dict[event.modifiers()]
        if sys.platform == 'darwin':
            # Qt 默认将 macOS 的 Command/Control 对调；pynput 使用物理键名。
            # https://doc.qt.io/qt-6/macos-issues.html#special-keys
            control, command = Qt.KeyboardModifier.MetaModifier, Qt.KeyboardModifier.ControlModifier
            if QApplication.testAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta):
                control, command = command, control
            modifiers = [name for flag, name in (
                (control, 'ctrl'), (command, 'cmd'),
                (Qt.KeyboardModifier.ShiftModifier, 'shift'), (Qt.KeyboardModifier.AltModifier, 'alt'))
                if event.modifiers() & flag]

        if modifiers and not key:
            self.setText(" + ".join(modify.capitalize() for modify in modifiers))
            self.unvalidated = True
        if modifiers and key:
            self.set_hotkey(modifiers + [key])
            self.unvalidated = False

        if event.key() == Qt.Key.Key_Escape:
            self.unvalidated = True

        super(HotkeyLineEdit, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """松开按键检验是否合法 保存显示合法按键"""
        if not self.start_record:
            return

        self.start_record = False
        if self.unvalidated:
            self.set_hotkey([])

        super(HotkeyLineEdit, self).keyReleaseEvent(event)
