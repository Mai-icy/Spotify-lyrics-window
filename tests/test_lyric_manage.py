#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

import pytest

from common.lyric.lyric_manage import LyricFileManage
from common.lyric.lyric_type import LrcFile, TransType


@pytest.fixture
def isolated_lyric_manage(tmp_path, monkeypatch):
    lyric_dir = tmp_path / "lyrics"
    lyric_dir.mkdir()
    lyric_data_path = lyric_dir / "lyric.json"
    lyric_data_path.write_text(json.dumps({}, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr("common.lyric.lyric_manage.LRC_PATH", lyric_dir)
    monkeypatch.setattr("common.lyric.lyric_manage.LYRIC_DATA_FILE_PATH", lyric_data_path)

    LyricFileManage._instance = None
    LyricFileManage._is_init = False
    manager = LyricFileManage()
    yield manager, lyric_dir, lyric_data_path
    LyricFileManage._instance = None
    LyricFileManage._is_init = False


def test_track_id_mapping_and_offsets_round_trip(isolated_lyric_manage):
    manager, _, lyric_data_path = isolated_lyric_manage

    manager.set_track_id_map("track-1", "Song A - Artist A")
    manager.set_offset_file("track-1", 500)

    assert manager.get_id("Song A - Artist A") == "track-1"
    assert manager.get_title("track-1") == "Song A - Artist A"
    assert manager.get_offset_file("track-1") == 500

    saved_data = json.loads(lyric_data_path.read_text(encoding="utf-8"))
    assert saved_data["id2title"]["track-1"] == "Song A - Artist A"
    assert saved_data["offset"]["track-1"] == 500


def test_set_not_found_can_write_and_clear(isolated_lyric_manage):
    manager, _, lyric_data_path = isolated_lyric_manage

    manager.set_not_found("track-2", "Song B - Artist B")
    assert manager.get_not_found("track-2")["track_title"] == "Song B - Artist B"

    manager.set_not_found("track-2", "")
    assert manager.get_not_found("track-2") is None

    saved_data = json.loads(lyric_data_path.read_text(encoding="utf-8"))
    assert "track-2" not in saved_data["no_lyric"]


def test_save_lyric_file_creates_mrc_and_clears_not_found(isolated_lyric_manage):
    manager, lyric_dir, _ = isolated_lyric_manage
    manager.set_not_found("track-3", "Song C - Artist C")

    lrc_file = LrcFile()
    lrc_file.load_content("[00:00.00]第一句\n[00:01.00]第二句", TransType.NON)

    manager.save_lyric_file("track-3", lrc_file)

    assert (lyric_dir / "track-3.mrc").exists()
    assert manager.get_not_found("track-3") is None
    assert manager.get_title("track-3") == "Song C - Artist C"
