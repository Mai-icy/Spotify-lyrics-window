#!/usr/bin/python
# -*- coding:utf-8 -*-
from common.api.exceptions import NetworkError
from common.lyric import lyric_download
from common.song_metadata.metadata_type import SongInfo


class FakeLyric:
    def __init__(self, empty=False):
        self._empty = empty
        self.saved_to = []

    def empty(self):
        return self._empty

    def save_to_mrc(self, path):
        self.saved_to.append(path)


class FakeManager:
    def __init__(self):
        self.mapped = []

    def set_track_id_map(self, track_id, track_name):
        self.mapped.append((track_id, track_name))


def make_song(name, singer, duration="03:30", album="Album"):
    return SongInfo(singer=singer, songName=name, album=album, year="", trackNumber="", duration=duration, genre="", picBuffer=None)


def test_download_lrc_prefers_kugou_when_score_is_highest(monkeypatch):
    fake_manager = FakeManager()
    fake_lyric = FakeLyric()

    monkeypatch.setattr(lyric_download, "LyricFileManage", lambda: fake_manager)
    monkeypatch.setattr(lyric_download.spotify_api, "search_song_info", lambda track_id: make_song("Song", "Artist"))
    monkeypatch.setattr(lyric_download.cloud_api, "search_song_id", lambda track_name: [type("Item", (), {"idOrMd5": "cloud-id"})()])
    monkeypatch.setattr(lyric_download.cloud_api, "search_song_info", lambda song_id: make_song("Song", "Artist"))
    monkeypatch.setattr(lyric_download.kugou_api, "search_song_id", lambda track_name: [type("Item", (), {"idOrMd5": "kugou-id"})()])
    monkeypatch.setattr(lyric_download.kugou_api, "search_song_info", lambda song_id: make_song("Song", "Artist"))
    monkeypatch.setattr(lyric_download, "compare_song_info", lambda candidate, spotify: 90 if candidate.album == "Album" else 0)
    monkeypatch.setattr(lyric_download.kugou_api, "fetch_song_lyric", lambda song_md5: fake_lyric)
    monkeypatch.setattr(lyric_download.cloud_api, "fetch_song_lyric", lambda song_id: (_ for _ in ()).throw(AssertionError("cloud should not be used")))
    assert lyric_download.download_lrc("Song - Artist", "track-1", min_score=74) is True
    assert fake_manager.mapped == [("track-1", "Song - Artist")]
    assert fake_lyric.saved_to

def test_download_lrc_returns_false_when_all_sources_fail(monkeypatch):
    monkeypatch.setattr(lyric_download.spotify_api, "search_song_info", lambda track_id: make_song("Song", "Artist"))
    monkeypatch.setattr(lyric_download.cloud_api, "search_song_id", lambda track_name: (_ for _ in ()).throw(NetworkError("cloud error")))
    monkeypatch.setattr(lyric_download.kugou_api, "search_song_id", lambda track_name: (_ for _ in ()).throw(NetworkError("kugou error")))

    assert lyric_download.download_lrc("Song - Artist", "track-3", min_score=74) is False
