#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.player.lyric_player import LrcPlayer, LyricThread
from common.lyric.lyric_type import LrcFile, TransType


def test_set_trans_mode_and_show_content(monkeypatch):
    monkeypatch.setattr(LyricThread, "start", lambda self: None)

    outputs = []
    player = LrcPlayer(output_func=lambda row, text, roll_time: outputs.append((row, text, roll_time)))
    player.lrc_file = LrcFile()
    player.lrc_file.load_content("[00:00.00]原文\n", TransType.NON)
    player.lrc_file.load_content("[00:00.00]翻译\n", TransType.CHINESE)

    assert player.set_trans_mode(TransType.CHINESE) is True

    outputs.clear()
    player.show_content(0, 500)

    assert outputs == [(1, "原文", 500), (2, "翻译", 500)]


def test_seek_to_position_resets_timer_and_wakes_thread(monkeypatch):
    monkeypatch.setattr(LyricThread, "start", lambda self: None)

    reset_calls = []
    monkeypatch.setattr(LyricThread, "reset_position", lambda self: reset_calls.append("reset"))

    player = LrcPlayer(output_func=lambda *args: None)
    player.seek_to_position(1200, is_show_last_lyric=False)

    assert reset_calls == []
    assert abs(player.get_time() - 1200) < 200

    player.seek_to_position(800, is_show_last_lyric=True)
    assert reset_calls == ["reset"]


def test_close_terminates_and_joins_thread(monkeypatch):
    monkeypatch.setattr(LyricThread, "start", lambda self: None)

    terminate_calls = []
    join_calls = []
    monkeypatch.setattr(LyricThread, "terminate", lambda self: terminate_calls.append("terminate"))
    monkeypatch.setattr(LyricThread, "join", lambda self, timeout=None: join_calls.append(timeout))

    player = LrcPlayer(output_func=lambda *args: None)
    player.close(timeout=0.5)

    assert terminate_calls == ["terminate"]
    assert join_calls == [0.5]
