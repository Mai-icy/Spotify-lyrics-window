#!/usr/bin/env python
# -*- coding:utf-8 -*-
from enum import Enum

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QGuiApplication, QFont, QColor
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__)
# from common.lyric.lyric_type import TransType


class TransType(Enum):
    NON = 0
    ROMAJI = 1
    CHINESE = 2


class DisplayMode(Enum):
    Horizontal = "Horizontal"
    Vertical = "Vertical"


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """
    lyric_folders = ConfigItem(
        "Folders", "LyricFolder", "download/lyric", FolderValidator())
    temp_folder = ConfigItem(
        "Folders", "TempFolder", "download/temp", FolderValidator())

    client_id = ConfigItem(
        "Account", "ClientID", "")
    client_secret = ConfigItem(
        "Account", "ClientSecret", "")

    proxy_ip = ConfigItem(
        "Proxy", "ProxyIP", None)

    pos_x = ConfigItem(
        "Position", "Pos_x", 500)
    pos_y = ConfigItem(
        "Position", "Pos_y", 900)
    width = ConfigItem(
        "Position", "Width", 800)
    height = ConfigItem(
        "Position", "Height", 150)

    enable_always_front = ConfigItem(
        "Lyric", "EnableAlwaysFront", True, BoolValidator())
    trans_mode = OptionsConfigItem(
        "Lyric", "TransMode", TransType.NON, OptionsValidator(TransType), EnumSerializer(TransType))
    display_mode = OptionsConfigItem(
        "Lyric", "DisplayMode", DisplayMode.Horizontal, OptionsValidator(DisplayMode), EnumSerializer(DisplayMode))
    lyric_font_size = RangeConfigItem(
        "Lyric", "FontSize", 25, RangeValidator(15, 50))
    lyric_font_family = ConfigItem(
        "Lyric", "FontFamily", "Microsoft YaHei")
    lyric_color = ColorConfigItem(
        "Lyric", "LyricColor", QColor(86, 152, 195))
    shadow_color = ColorConfigItem(
        "Lyric", "ShadowColor", QColor(190, 190, 190))

    enable_hotkeys = ConfigItem(
        "Hotkeys", "EnableHotkeys", False, BoolValidator())
    pause_hotkey = ConfigItem(
        "Hotkeys", "PauseHotkey", ["alt", "p"])
    last_song_hotkey = ConfigItem(
        "Hotkeys", "LastSongHotkey", ["alt", "left"])
    next_song_hotkey = ConfigItem(
        "Hotkeys", "NextSongHotkey", ["alt", "right"])
    lock_hotkey = ConfigItem(
        "Hotkeys", "LockHotkey", ["alt", "l"])
    calibrate_hotkey = ConfigItem(
        "Hotkeys", "CalibrateHotkey", ["alt", "r"])
    translate_hotkey = ConfigItem(
        "Hotkeys", "TranslateHotkey", ["alt", "a"])
    show_window_hotkey = ConfigItem(
        "Hotkeys", "ShowWindowHotkey", ["alt", "s"])
    close_window_hotkey = ConfigItem(
        "Hotkeys", "CloseWindowHotkey", ["alt", "x"])
    open_tool_hotkey = ConfigItem(
        "Hotkeys", "OpenToolsHotkey", ["alt", "t"])

    dpi_scale = OptionsConfigItem(
        "SettingWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "SettingWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    minimize_to_tray = ConfigItem(
        "SettingWindow", "MinimizeToTray", True, BoolValidator())

    @property
    def lyric_font(self):
        """ get the desktop lyric font """
        font = QFont(self.lyric_font_family.value)
        font.setPixelSize(self.lyric_font_size.value)
        return font

    @lyric_font.setter
    def lyric_font(self, font: QFont):
        dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
        self.lyric_font_family.value = font.family()
        self.lyric_font_size.value = max(15, int(font.pointSize()*dpi/72))
        self.save()


VERSION = __version__
HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io"


cfg = Config()
qconfig.load('config/config.json', cfg)
