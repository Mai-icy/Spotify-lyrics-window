#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.path import SETTING_TOML_PATH
import rtoml


class Config:
    default_dict = {}

    class PositionConfig:
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

        pause_button: tuple = ("alt", "p")
        last_button: tuple = ("alt", "left")
        next_button: tuple = ("alt", "right")
        lock_button: tuple = ("alt", "l")
        calibrate_button: tuple = ("alt", "r")
        translate_button: tuple = ("alt", "a")
        show_window: tuple = ("alt", "s")
        close_button: tuple = ("alt", "x")

    @classmethod
    def read_config(cls):
        """读取toml配置文件配置，存储在Config类属性"""
        def _load_config(last_cls, dic):
            for key in dic.keys():
                if isinstance(dic[key], dict):
                    now_cls = getattr(last_cls, key)
                    _load_config(now_cls, dic[key])
                else:
                    setattr(last_cls, key, dic[key])

        data = rtoml.load(SETTING_TOML_PATH)
        _load_config(cls, data)

    @classmethod
    def save_config(cls):
        """写入toml配置文件配置，存储Config类属性至文件"""
        config_dic = cls.to_dict()

        rtoml.dump(config_dic, SETTING_TOML_PATH)

    @classmethod
    def to_dict(cls) -> dict:
        """将当前配置装换为字典并返回"""
        def _save_config(last_cls, dic):
            attr_dict = last_cls.__dict__
            for attr in attr_dict.keys():
                if not attr.startswith("__"):
                    value = getattr(last_cls, attr)
                    if hasattr(value, '__dict__'):
                        dic[attr] = {}
                        now_cls = getattr(last_cls, attr)
                        _save_config(now_cls, dic[attr])
                    else:
                        dic[attr] = value

        config_dic = {}
        _save_config(cls, config_dic)

        for key in list(config_dic.keys()):
            if not config_dic[key]:
                config_dic.pop(key)

        return config_dic


Config.default_dict = Config.to_dict()
Config.read_config()


if __name__ == '__main__':
    # Config.save_config()

    print(Config.default_dict)
