#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.path import SETTING_TOML_PATH
import rtoml


class Config:

    class CommonConfig:
        pos_x: int = 500
        pos_y: int = 900
        width: int = 800
        height: int = 150

    class LyricConfig:
        trans_type: int = 0

        font_family: str = "微软雅黑"
        font_size: int = 25

        is_always_front: bool = True

        rgb_style: str = "blue"
        lyric_color: tuple = (86, 152, 195)
        shadow_color: tuple = (190, 190, 190)

    class HotkeyConfig:
        is_enable: bool = True

        calibrate_button: tuple = ("alt", "r")
        lock_button: tuple = ("alt", "l")
        close_button: tuple = ("alt", "x")
        translate_button: tuple = ("alt", "a")
        next_button: tuple = ("alt", "right")
        last_button: tuple = ("alt", "left")
        pause_button: tuple = ("alt", "p")
        show_window: tuple = ("alt", "s")

    @classmethod
    def read_config(cls):
        data = rtoml.load(SETTING_TOML_PATH)
        cls._load_config(cls, data)
        return cls

    @classmethod
    def _load_config(cls, last_cls, dic):
        for key in dic.keys():
            if isinstance(dic[key], dict):
                now_cls = getattr(last_cls, key)
                cls._load_config(now_cls, dic[key])
            else:
                setattr(last_cls, key, dic[key])

    @classmethod
    def save_config(cls):
        config_dic = {}
        cls._save_config(cls, config_dic)

        for key in list(config_dic.keys()):
            if not config_dic[key]:
                config_dic.pop(key)

        rtoml.dump(config_dic, SETTING_TOML_PATH)

    @classmethod
    def _save_config(cls, last_cls, dic):
        attr_dict = last_cls.__dict__
        for attr in attr_dict.keys():
            if not attr.startswith("__"):
                value = getattr(last_cls, attr)
                if hasattr(value, '__dict__'):
                    dic[attr] = {}
                    now_cls = getattr(last_cls, attr)
                    cls._save_config(now_cls, dic[attr])
                else:
                    dic[attr] = value


Config.read_config()


if __name__ == '__main__':
    Config.save_config()
