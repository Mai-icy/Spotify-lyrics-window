#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from common.config import Config


class HotkeyLineEdit(QLineEdit):
    def __init__(self, signal_key, parent=None):
        super(HotkeyLineEdit, self).__init__(parent)
        self.unvalidated = False
        self.signal_key = signal_key
        self.start_record = False
        self.current_hot_keys = getattr(Config.HotkeyConfig, signal_key)
        self.set_hotkey_text(self.current_hot_keys)

        self.setReadOnly(True)

    def get_signal_key(self) -> str:
        return self.signal_key

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        if self.unvalidated:
            self.set_hotkey_text([])
            self.unvalidated = False
            return
        super(HotkeyLineEdit, self).focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
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
        if modifiers and key:
            self.set_hotkey_text(modifiers + [key])
            self.unvalidated = False

        if event.key() == Qt.Key_Escape:
            self.unvalidated = True

        super(HotkeyLineEdit, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if not self.start_record:
            return

        if self.unvalidated:
            self.set_hotkey_text([])
            self.unvalidated = False
            return

        self.start_record = False
        super(HotkeyLineEdit, self).keyReleaseEvent(event)

    def set_hotkey_text(self, hotkey):
        self.current_hot_keys = hotkey
        if not hotkey:
            self.setText("None")
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

        if hotkey:
            setattr(Config.HotkeyConfig, self.signal_key, self.current_hot_keys)
        else:
            setattr(Config.HotkeyConfig, self.signal_key, None)
