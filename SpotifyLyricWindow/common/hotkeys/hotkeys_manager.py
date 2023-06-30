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

    def __init__(self, item_name_func_dict: dict):
        super().__init__()
        self.hotkeys_system = SystemHotkey()
        self.item_name_func_dict = item_name_func_dict
        self.item_name_hotkeys_dict = {}

        for item_name in self.item_name_func_dict.keys():
            item = getattr(cfg, item_name)
            self.item_name_hotkeys_dict[item_name] = cfg.get(item)
            item.valueChanged.connect(partial(self.item_change_event, item))

    def item_change_event(self, item, hotkey):
        self.item_name_hotkeys_dict[item] = hotkey
        try:
            self.hotkeys_system.register(hotkey, callback=lambda _: None)
        except SystemRegisterError:
            conflict_item_names = [item_name for item_name in self.item_name_hotkeys_dict.keys()
                                   if self.item_name_hotkeys_dict[item_name] == hotkey]
            self.hotkey_conflict_signal.emit(conflict_item_names)
        finally:
            self.set_hotkey_enable(False)

    def set_hotkey_enable(self, flag: bool):
        if flag:
            for item_name in self.item_name_func_dict.keys():
                hotkey = self.item_name_hotkeys_dict[item_name]
                func = self.item_name_func_dict[item_name]
                try:
                    self.hotkeys_system.register(hotkey, callback=func)
                except SystemRegisterError:  # 热键冲突
                    raise SystemRegisterError("热键意外冲突")
        else:
            for hotkey in self.hotkeys_system.keybinds.keys():
                self.hotkeys_system.unregister(hotkey)


if __name__ == "__main__":
    ...
