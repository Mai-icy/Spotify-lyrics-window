#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.path import SETTING_TOML_PATH
import rtoml


class Config:

    class LyricConfig:
        trans_type: int = 0

        font: str = "微软雅黑"
        font_size: int = 25

        is_always_front: bool = True

        lyric_color: str
        shadow_color: str

    class HotkeyConfig:
        ...

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
    ...
