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

    pause_hotkey = pyqtSignal(object)
    last_song_hotkey = pyqtSignal(object)
    next_song_hotkey = pyqtSignal(object)
    lock_hotkey = pyqtSignal(object)
    calibrate_hotkey = pyqtSignal(object)
    translate_hotkey = pyqtSignal(object)
    show_window_hotkey = pyqtSignal(object)
    close_window_hotkey = pyqtSignal(object)
    open_tool_hotkey = pyqtSignal(object)

    connected_slots = {}

    def __init__(self, hotkey_item_names: list):
        super().__init__()
        self.hotkeys_system = SystemHotkey()
        self.hotkey_item_names = hotkey_item_names
        self.item_name_hotkeys_dict = {}
        self.hotkeys_is_open = False

        for item_name in hotkey_item_names:
            # setattr(HotkeysManager, item_name, pyqtSignal())
            item = getattr(cfg, item_name)
            self.item_name_hotkeys_dict[item_name] = cfg.get(item)

            item.valueChanged.connect(partial(self._item_change_event, item_name))

    def _item_change_event(self, item_name: str, hotkey: list):
        self.item_name_hotkeys_dict[item_name] = hotkey
        if not hotkey:
            return

        try:  # 测试是否存在热键冲突
            self.hotkeys_system.register(hotkey, callback=lambda _: None)
            for o_item_name, o_item_hotkey in self.item_name_hotkeys_dict.items():
                if o_item_name != item_name and o_item_hotkey == hotkey:
                    raise SystemRegisterError

        except SystemRegisterError:
            conflict_item_names = [item_name for item_name in self.item_name_hotkeys_dict.keys()
                                   if self.item_name_hotkeys_dict[item_name] == hotkey]
            self.hotkey_conflict_signal.emit(conflict_item_names)

            item = getattr(cfg, item_name)
            cfg.set(item, [])
        finally:
            self.hotkeys_system.unregister(hotkey)

    def set_hotkey_enable(self, flag: bool):
        if self.hotkeys_is_open == flag:
            return

        self.hotkeys_is_open = flag
        if flag:
            for item_name in self.hotkey_item_names:
                hotkey = self.item_name_hotkeys_dict[item_name]
                if not hotkey:
                    continue
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
        self.connected_slots[item_name] = func
        signal.connect(func)

    def hotkey_disconnect(self, item_name):
        signal = getattr(self, item_name)
        signal.disconnect(self.connected_slots[item_name])


if __name__ == "__main__":
    ...
