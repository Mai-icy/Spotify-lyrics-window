#!/usr/bin/python
# -*- coding:utf-8 -*-
import copy

import rtoml

from common import config as config_module
from common.config import Config


def _apply_config_snapshot(snapshot, target_cls):
    for key, value in snapshot.items():
        current = getattr(target_cls, key)
        if isinstance(value, dict) and hasattr(current, "__dict__"):
            _apply_config_snapshot(value, current)
        else:
            setattr(target_cls, key, value)


def _reset_config_state(snapshot):
    # Reset top-level nested classes one by one to keep the original object graph.
    for section in ("CommonConfig", "LyricConfig", "HotkeyConfig"):
        _apply_config_snapshot(snapshot[section], getattr(Config, section))
    Config._default_dict = copy.deepcopy(snapshot.get("_default_dict", {}))


def test_save_config_writes_toml(tmp_path, monkeypatch):
    setting_path = tmp_path / "setting.toml"
    snapshot = Config.to_dict()

    monkeypatch.setattr(config_module, "SETTING_TOML_PATH", setting_path)
    try:
        Config.CommonConfig.ClientConfig.client_id = "client-id"
        Config.CommonConfig.ClientConfig.mainland_ip = "123.58.172.91"
        Config.CommonConfig.PathConfig.lyrics_file_path = "C:/lyrics"
        Config.LyricConfig.font_family = "测试字体"
        Config.HotkeyConfig.pause_button = ["ctrl", "p"]

        Config.save_config()

        saved = rtoml.load(setting_path)
        assert saved["CommonConfig"]["ClientConfig"]["client_id"] == "client-id"
        assert saved["CommonConfig"]["ClientConfig"]["mainland_ip"] == "123.58.172.91"
        assert saved["CommonConfig"]["PathConfig"]["lyrics_file_path"] == "C:/lyrics"
        assert saved["LyricConfig"]["font_family"] == "测试字体"
        assert saved["HotkeyConfig"]["pause_button"] == ["ctrl", "p"]
    finally:
        _reset_config_state(snapshot)


def test_read_config_updates_values_and_stores_previous_defaults(tmp_path, monkeypatch):
    setting_path = tmp_path / "setting.toml"
    snapshot = Config.to_dict()

    monkeypatch.setattr(config_module, "SETTING_TOML_PATH", setting_path)
    setting_path.write_text(
        """
[CommonConfig.ClientConfig]
client_id = "loaded-id"

[CommonConfig.PositionConfig]
width = 640

[LyricConfig]
font_family = "新字体"
is_always_front = false
""".strip(),
        encoding="utf-8",
    )

    try:
        Config.CommonConfig.ClientConfig.client_id = ""
        Config.CommonConfig.PositionConfig.width = 800
        Config.LyricConfig.font_family = "微软雅黑"
        Config.LyricConfig.is_always_front = True

        Config.read_config()

        assert Config.CommonConfig.ClientConfig.client_id == "loaded-id"
        assert Config.CommonConfig.PositionConfig.width == 640
        assert Config.LyricConfig.font_family == "新字体"
        assert Config.LyricConfig.is_always_front is False
        assert Config.get_default_dict()["LyricConfig"]["font_family"] == "微软雅黑"
    finally:
        _reset_config_state(snapshot)


def test_to_dict_keeps_nested_sections_shape():
    snapshot = Config.to_dict()
    try:
        Config.CommonConfig.ClientConfig.client_id = ""
        Config.CommonConfig.ClientConfig.client_secret = ""
        Config.CommonConfig.ClientConfig.sp_dc = ""
        Config.CommonConfig.ClientConfig.proxy_ip = ""
        Config.CommonConfig.ClientConfig.mainland_ip = ""

        data = Config.to_dict()

        assert "ClientConfig" in data["CommonConfig"]
        assert data["CommonConfig"]["ClientConfig"]["client_id"] == ""
    finally:
        _reset_config_state(snapshot)
