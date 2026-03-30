#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.song_metadata import compare_metadata
from common.song_metadata.metadata_type import SongInfo


def make_song(name="Song", singer="Artist", album="Album", duration="03:30"):
    return SongInfo(
        singer=singer,
        songName=name,
        album=album,
        year="",
        trackNumber="",
        duration=duration,
        genre="",
        picBuffer=None,
    )


def test_parse_duration():
    assert compare_metadata.__parse_duration("03:45") == 225


def test_compare_song_info_returns_zero_for_missing_input():
    assert compare_metadata.compare_song_info(None, make_song()) == 0
    assert compare_metadata.compare_song_info(make_song(), None) == 0


def test_compare_song_info_uses_duration_name_singer_and_album(monkeypatch):
    monkeypatch.setattr(compare_metadata.fuzz, "partial_ratio", lambda left, right: 90 if left == right else 60)

    score = compare_metadata.compare_song_info(
        make_song(name="Song", singer="Artist", album="Album", duration="03:30"),
        make_song(name="Song", singer="Artist", album="Album", duration="03:30"),
    )

    assert score == 92.5


def test_compare_song_info_uses_reduced_duration_score_with_small_gap(monkeypatch):
    monkeypatch.setattr(compare_metadata.fuzz, "partial_ratio", lambda left, right: 80)

    score = compare_metadata.compare_song_info(
        make_song(duration="03:30", album=""),
        make_song(duration="03:33", album=""),
    )

    assert score == 80


def test_compare_song_info_ignores_album_when_missing(monkeypatch):
    monkeypatch.setattr(compare_metadata.fuzz, "partial_ratio", lambda left, right: 70)

    score = compare_metadata.compare_song_info(
        make_song(album="", duration="03:30"),
        make_song(album="", duration="03:30"),
    )

    assert score == 80
