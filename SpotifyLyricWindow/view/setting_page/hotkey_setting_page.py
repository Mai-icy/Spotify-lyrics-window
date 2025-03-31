#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from components.raw_ui import Ui_HotkeysPage
from components.line_edit.hotkeys_line_edit import HotkeyLineEdit

from common.config import Config


class HotkeysPage(QWidget, Ui_HotkeysPage):
    def __init__(self, parent=None):
        super(HotkeysPage, self).__init__(parent)
        self.setupUi(self)

        self._init_line_edit()
        self._init_signal()

    def _init_line_edit(self):
        """初始化快捷键输入框"""
        self.calibration_hotkey_lineEdit = HotkeyLineEdit("calibrate_button", self.hotkeyslineedit_frame)
        self.lock_hotkey_lineEdit = HotkeyLineEdit("lock_button", self.hotkeyslineedit_frame)
        self.close_hotkey_lineEdit = HotkeyLineEdit("close_button", self.hotkeyslineedit_frame)
        self.trans_hotkey_lineEdit = HotkeyLineEdit("translate_button", self.hotkeyslineedit_frame)
        self.next_hotkey_lineEdit = HotkeyLineEdit("next_button", self.hotkeyslineedit_frame)
        self.last_hotkey_lineEdit = HotkeyLineEdit("last_button", self.hotkeyslineedit_frame)
        self.show_hotkey_lineEdit = HotkeyLineEdit("show_window", self.hotkeyslineedit_frame)
        self.pause_hotkey_lineEdit = HotkeyLineEdit("pause_button", self.hotkeyslineedit_frame)

        self.line_edit_dict = {
            "pause_button": self.pause_hotkey_lineEdit,
            "last_button": self.last_hotkey_lineEdit,
            "next_button": self.next_hotkey_lineEdit,
            "lock_button": self.lock_hotkey_lineEdit,
            "calibrate_button": self.calibration_hotkey_lineEdit,
            "translate_button": self.trans_hotkey_lineEdit,
            "show_window": self.show_hotkey_lineEdit,
            "close_button": self.close_hotkey_lineEdit
        }

        for line_edit in self.line_edit_dict.values():
            line_edit.setMinimumSize(QSize(170, 32))
            line_edit.setMaximumSize(QSize(170, 32))
            line_edit.hotkeys_conflict_signal.connect(self.hotkeys_conflict_event)
            self.HotkeysLineEditFrameVerticalLayout.addWidget(line_edit)

    def _init_signal(self):
        """初始化信号"""
        self.hotkeys_default_button.clicked.connect(self.set_default_event)
        self.enable_hotkeys_checkBox.stateChanged.connect(self.enable_hotkeys_event)

    def load_config(self):
        """载入配置"""
        for line_edit in self.line_edit_dict.values():
            signal_key = line_edit.get_signal_key()
            current_hot_keys = getattr(Config.HotkeyConfig, signal_key)
            if current_hot_keys and current_hot_keys != "null":
                line_edit.set_hotkey(current_hot_keys)
            else:
                line_edit.set_hotkey([])

        self.enable_hotkeys_checkBox.setChecked(Config.HotkeyConfig.is_enable)

    def set_default_event(self):
        """设置初始化按钮事件"""
        default_dict = Config.get_default_dict()["HotkeyConfig"]
        for line_edit in self.line_edit_dict.values():
            line_edit.set_hotkey(default_dict[line_edit.get_signal_key()])

    def hotkeys_conflict_event(self, conflict_signal_key):
        """设置热键出现冲突 将冲突的旧热键 设置为 None"""
        conflict_line_edit = self.line_edit_dict[conflict_signal_key]
        conflict_line_edit.set_hotkey([])

    def enable_hotkeys_event(self):
        """开启关闭 快捷键勾选框 事件"""
        if self.enable_hotkeys_checkBox.isChecked() and not self.pause_hotkey_lineEdit.isEnabled():
            for line_edit in self.line_edit_dict.values():
                line_edit.setEnabled(True)
        elif not self.enable_hotkeys_checkBox.isChecked() and self.pause_hotkey_lineEdit.isEnabled():
            for line_edit in self.line_edit_dict.values():
                line_edit.setEnabled(False)
        else:
            return
