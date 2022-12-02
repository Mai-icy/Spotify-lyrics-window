#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.HotkeysPage import Ui_HotkeysPage
from components.hotkeys_line_edit import HotkeyLineEdit

from common.config import Config


class HotkeysPage(QWidget, Ui_HotkeysPage):
    def __init__(self, parent=None):
        super(HotkeysPage, self).__init__(parent)
        self.setupUi(self)

        self._init_line_edit()
        self._init_signal()

    def _init_line_edit(self):
        self.calibration_hotkey_lineEdit = HotkeyLineEdit("calibrate_button", self.hotkeyslineedit_frame)
        self.lock_hotkey_lineEdit = HotkeyLineEdit("lock_button", self.hotkeyslineedit_frame)
        self.close_hotkey_lineEdit = HotkeyLineEdit("close_button", self.hotkeyslineedit_frame)
        self.trans_hotkey_lineEdit = HotkeyLineEdit("translate_button", self.hotkeyslineedit_frame)
        self.next_hotkey_lineEdit = HotkeyLineEdit("next_button", self.hotkeyslineedit_frame)
        self.last_hotkey_lineEdit = HotkeyLineEdit("last_button", self.hotkeyslineedit_frame)
        self.show_hotkey_lineEdit = HotkeyLineEdit("show_window", self.hotkeyslineedit_frame)
        self.pause_hotkey_lineEdit = HotkeyLineEdit("pause_button", self.hotkeyslineedit_frame)

        self.line_edit_list = [self.pause_hotkey_lineEdit, self.last_hotkey_lineEdit, self.next_hotkey_lineEdit,
                               self.lock_hotkey_lineEdit, self.calibration_hotkey_lineEdit, self.trans_hotkey_lineEdit,
                               self.show_hotkey_lineEdit, self.close_hotkey_lineEdit]

        for line_edit in self.line_edit_list:
            line_edit.setMinimumSize(QSize(170, 32))
            line_edit.setMaximumSize(QSize(170, 32))
            self.HotkeysLineEditFrameVerticalLayout.addWidget(line_edit)

    def _init_signal(self):
        self.hotkeys_default_button.clicked.connect(self.set_default_event)
        self.enable_hotkeys_checkBox.stateChanged.connect(self.enable_hotkeys_event)

    def load_config(self):
        for line_edit in self.line_edit_list:
            signal_key = line_edit.get_signal_key()
            current_hot_keys = getattr(Config.HotkeyConfig, signal_key)
            line_edit.set_hotkey(current_hot_keys)

        self.enable_hotkeys_checkBox.setChecked(Config.HotkeyConfig.is_enable)

    def set_default_event(self):
        default_dict = Config.get_default_dict()["HotkeyConfig"]
        for line_edit in self.line_edit_list:
            line_edit.set_hotkey(default_dict[line_edit.get_signal_key()])

    def enable_hotkeys_event(self):
        if self.enable_hotkeys_checkBox.isChecked() and not self.pause_hotkey_lineEdit.isEnabled():
            for line_edit in self.line_edit_list:
                line_edit.setEnabled(True)
        elif not self.enable_hotkeys_checkBox.isChecked() and self.pause_hotkey_lineEdit.isEnabled():
            for line_edit in self.line_edit_list:
                line_edit.setEnabled(False)
        else:
            return
