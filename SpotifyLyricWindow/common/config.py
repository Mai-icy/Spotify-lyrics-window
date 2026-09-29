#!/usr/bin/python
# -*- coding:utf-8 -*-
import rtoml
import sys
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH
if sys.platform == "darwin" and getattr(sys, "frozen", False):
    # 签名后的 .app 只读；用户数据独立保存，更新应用时不会丢失。
    DATA_PATH = Path.home() / "Library/Application Support/Spotify Lyrics Window"
SETTING_TOML_PATH = DATA_PATH / Path(r"resource/setting.toml")


class Config:
    _default_dict = {}

    class CommonConfig:
        is_quit_on_close: bool = False
        is_save_position: bool = True
        is_auto_track_sync: bool = True
        language: str = 'zh_CN'
        settings_theme: str = 'system'

        api_offset: int = 0

        class ClientConfig:
            client_id: str = ""
            client_secret: str = ""
            sp_dc: str = ""
            spotify_proxy_ip: str = ""
            cloudmusic_proxy_ip: str = ""
            kugou_proxy_ip: str = ""
            mainland_ip: str = ""

        class PathConfig:
            temp_file_path: str = ""
            lyrics_file_path: str = ""

        class PositionConfig:
            pos_x: int = 0
            pos_y: int = 0
            width: int = 800
            height: int = 150

    class LyricConfig:
        trans_type: int = 0
        display_mode: int = 0  # 0代表水平显示歌词，1代表竖直显示歌词

        font_family: str = "微软雅黑"
        translation_font_family: str = "微软雅黑"
        font_size: int = 25

        is_always_front: bool = True

        rgb_style: str = "blue"
        lyric_color: tuple = (86, 152, 195)
        shadow_color: tuple = (190, 190, 190)

    class HotkeyConfig:
        is_enable: bool = False

        pause_button: list = []
        last_button: list = []
        next_button: list = []
        lock_button: list = []
        calibrate_button: list = []
        translate_button: list = []
        show_window: list = []
        close_button: list = []

    @classmethod
    def read_config(cls):
        """读取toml配置文件配置，存储在Config类属性"""
        cls._default_dict = cls.to_dict()
        if not SETTING_TOML_PATH.exists():
            SETTING_TOML_PATH.parent.mkdir(parents=True, exist_ok=True)
            cls.save_config()
            return

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
                if not attr.startswith("_"):
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

    @classmethod
    def get_default_dict(cls) -> dict:
        return cls._default_dict


Config.read_config()


if __name__ == '__main__':
    Config.read_config()
    Config.save_config()
    ...
