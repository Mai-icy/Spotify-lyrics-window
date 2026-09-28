#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import *

from components.settings_ui import Ui_HotkeysPage
from components.line_edit.hotkeys_line_edit import HotkeyLineEdit

from common.config import Config
from common.hotkeys import has_hotkey_permission, request_hotkey_permission


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
        if sys.platform == 'darwin':
            self.accessibility_button.clicked.connect(self._accessibility_event)
            self.input_monitoring_button.clicked.connect(self._input_monitoring_event)

    def load_config(self):
        """载入配置"""
        for line_edit in self.line_edit_dict.values():
            signal_key = line_edit.get_signal_key()
            current_hot_keys = getattr(Config.HotkeyConfig, signal_key)
            if current_hot_keys and current_hot_keys != "null":
                line_edit.set_hotkey(current_hot_keys)
            else:
                line_edit.set_hotkey([])

        with QSignalBlocker(self.enable_hotkeys_checkBox):
            self.enable_hotkeys_checkBox.setChecked(Config.HotkeyConfig.is_enable)
        self.enable_hotkeys_event()

    def set_default_event(self):
        """设置初始化按钮事件"""
        default_dict = Config.get_default_dict()["HotkeyConfig"]
        for line_edit in self.line_edit_dict.values():
            line_edit.set_hotkey(default_dict[line_edit.get_signal_key()])
        with QSignalBlocker(self.enable_hotkeys_checkBox):
            self.enable_hotkeys_checkBox.setChecked(default_dict['is_enable'])
        self.enable_hotkeys_event()

    def hotkeys_conflict_event(self, conflict_signal_key):
        """设置热键出现冲突时，清空冲突的旧热键。"""
        conflict_line_edit = self.line_edit_dict[conflict_signal_key]
        conflict_line_edit.set_hotkey([])

    def enable_hotkeys_event(self):
        """开启关闭 快捷键勾选框 事件"""
        enabled = self.enable_hotkeys_checkBox.isChecked()
        if enabled and not has_hotkey_permission():
            enabled = False
            with QSignalBlocker(self.enable_hotkeys_checkBox):
                self.enable_hotkeys_checkBox.setChecked(False)
            self.hotkeys_tip_label.setText(self.tr('尚未获得快捷键权限，已保持关闭。请先通过上方按钮完成授权。'))
        else:
            self.hotkeys_tip_label.clear()
        Config.HotkeyConfig.is_enable = enabled
        for line_edit in self.line_edit_dict.values():
            line_edit.setEnabled(enabled)

    def _accessibility_event(self):
        request_hotkey_permission('accessibility')
        self._open_permission_settings('Privacy_Accessibility')

    def _input_monitoring_event(self):
        request_hotkey_permission('input_monitoring')
        self._open_permission_settings('Privacy_ListenEvent')

    def _open_permission_settings(self, pane):
        if not QDesktopServices.openUrl(QUrl(f'x-apple.systempreferences:com.apple.preference.security?{pane}')):
            self.hotkeys_tip_label.setText(self.tr('无法打开系统设置，请手动前往「隐私与安全性」完成授权。'))
        else:
            self.hotkeys_tip_label.setText(self.tr('授权后请返回并重新勾选启用；若仍未识别，请重启程序。'))
