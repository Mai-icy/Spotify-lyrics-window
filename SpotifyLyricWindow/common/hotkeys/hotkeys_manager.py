#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time

from PyQt5.QtCore import QObject, pyqtSignal

from system_hotkey import SystemHotkey
from system_hotkey.system_hotkey import SystemRegisterError
from common.config import cfg
from functools import partial


class HotkeysManager(QObject):

    hotkey_conflict_signal = pyqtSignal(list)

    def __init__(self, hotkey_item_names: list):
        super().__init__()
        self.hotkeys_system = SystemHotkey()
        self.hotkey_item_names = hotkey_item_names
        self.item_name_hotkeys_dict = {}

        for item_name in hotkey_item_names:
            setattr(self, item_name, pyqtSignal())
            item = getattr(cfg, item_name)
            self.item_name_hotkeys_dict[item_name] = cfg.get(item)

            item.valueChanged.connect(partial(self.item_change_event, item))

    def item_change_event(self, item: str, hotkey: list):
        self.item_name_hotkeys_dict[item] = hotkey
        try:  # 测试是否存在热键冲突
            self.hotkeys_system.register(hotkey, callback=lambda _: None)
        except SystemRegisterError:
            conflict_item_names = [item_name for item_name in self.item_name_hotkeys_dict.keys()
                                   if self.item_name_hotkeys_dict[item_name] == hotkey]
            self.hotkey_conflict_signal.emit(conflict_item_names)
        finally:
            self.hotkeys_system.unregister(hotkey)

    def set_hotkey_enable(self, flag: bool):
        if flag:
            for item_name in self.item_name_func_dict.keys():
                hotkey = self.item_name_hotkeys_dict[item_name]
                func = getattr(self, item_name).emit
                try:
                    self.hotkeys_system.register(hotkey, callback=func)
                except SystemRegisterError:  # todo 热键冲突
                    raise SystemRegisterError("热键意外冲突")
        else:
            for hotkey in self.hotkeys_system.keybinds.keys():
                self.hotkeys_system.unregister(hotkey)

    def hotkey_connect(self, item_name, func):
        signal = getattr(self, item_name)
        signal.connect(func)

    def hotkey_disconnect(self, item_name):
        signal = getattr(self, item_name)
        signal.disconnect()


if __name__ == "__main__":
    ...
