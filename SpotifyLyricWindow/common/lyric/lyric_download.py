#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests

from common.api.lyric_api import CloudMusicWebApi, KugouApi, SpotifyApi
from common.api.exceptions import NoneResultError, NetworkError, UserError
from common.song_metadata import compare_song_info
from common.lyric import LyricFileManage
from common.path import LRC_PATH
from common.logger import get_logger

cloud_api = CloudMusicWebApi()
kugou_api = KugouApi()
spotify_api = SpotifyApi()
logger = get_logger(__name__)


def _search_candidates(api, keyword, spotify_info, seen, song_alias=None):
    """粗筛搜索结果，只请求少量候选详情；不同歌词源使用各自的ID集合。"""
    try:
        songs = api.search_song_id(keyword)
    except NoneResultError:
        return [], True
    except NetworkError:
        return [], False

    from common.song_metadata.metadata_alias import duration_seconds

    duration = duration_seconds(spotify_info.duration)

    def rank_song(song):
        info = spotify_info._replace(songName=getattr(song, 'songName', ''), singer=getattr(song, 'singer', ''),
                                     duration=getattr(song, 'duration', '0:00'), album=None, artistNames=())
        score = (compare_song_info(info, spotify_info, song_alias=song_alias) if song_alias else
                 compare_song_info(info, spotify_info))
        return score, -abs(duration_seconds(info.duration) - duration)

    songs = sorted(songs[:5], key=rank_song, reverse=True)
    songs = [song for song in songs if song.idOrMd5 not in seen]
    candidates = []
    for song in songs[:3]:
        song_id = song.idOrMd5
        seen.add(song_id)
        try:
            song_info = api.search_song_info(song_id)
        except (NetworkError, NoneResultError):
            continue
        if song_alias:
            from common.song_metadata.metadata_alias import is_song_alias

            if not is_song_alias(song_info, song_alias):
                continue
        score = (compare_song_info(song_info, spotify_info, song_alias=song_alias) if song_alias else
                 compare_song_info(song_info, spotify_info))
        candidates.append((score, api, song_id, song_info))
    return candidates, True


def _download_candidates(candidates, track_name, track_id, min_score, attempted):
    """按评分下载候选，分数相同时保留原有酷狗优先的行为。"""
    candidates = sorted(candidates, key=lambda item: (item[0], item[1] is kugou_api), reverse=True)
    for score, api, song_id, _ in candidates:
        if score <= min_score or (api, song_id) in attempted:
            continue
        attempted.add((api, song_id))
        try:
            lrc = api.fetch_song_lyric(song_id)
            if not lrc.empty():
                lrc.save_to_mrc(str(LRC_PATH / f'{track_id}.mrc'))
                LyricFileManage().set_track_id_map(track_id, track_name)
                return True
        except (NetworkError, NoneResultError):
            continue
    return False


def download_lrc(track_name: str, track_id: str, *, min_score=74) -> bool:
    """download lyric by the track_id. Kugou and Cloud Api were used."""
    file_name = LRC_PATH / f"{track_id}.mrc"

    # min_score = 74  # 最低相似度评分
    try:
        spotify_info = spotify_api.search_song_info(track_id)
    except NetworkError as e:
        raise e

    candidates, attempted = [], set()
    sources = []
    for api in (cloud_api, kugou_api):
        seen = set()
        results, available = _search_candidates(api, track_name, spotify_info, seen)
        candidates.extend(results)
        if available:
            sources.append((api, seen))
    if _download_candidates(candidates, track_name, track_id, min_score, attempted):
        return True

    # 原匹配未找到歌词时才请求别名；歌词源本身不可用时不增加额外网络请求。
    if sources:
        from common.song_metadata.metadata_alias import get_song_aliases, get_alias_keywords

        song_alias = get_song_aliases(track_id, spotify_info)
        if song_alias:
            candidates = [(compare_song_info(info, spotify_info, song_alias=song_alias), api, song_id, info)
                          for _, api, song_id, info in candidates]
            if _download_candidates(candidates, track_name, track_id, min_score, attempted):
                logger.debug('使用 MusicBrainz 别名匹配歌词: %s -> %s', track_id, song_alias.id)
                return True
            for keyword in get_alias_keywords(spotify_info, song_alias):
                for api, seen in sources:
                    results, _ = _search_candidates(api, keyword, spotify_info, seen, song_alias)
                    candidates.extend(results)
                if _download_candidates(candidates, track_name, track_id, min_score, attempted):
                    logger.debug('使用 MusicBrainz 别名搜索歌词: %s -> %s', track_id, song_alias.id)
                    return True

    # spotify 歌词 API 暂不支持
    # try:
    #     lrc = spotify_api.fetch_song_lyric(track_id)
    #     if not lrc.empty():
    #         lrc.save_to_mrc(str(file_name))
    #         LyricFileManage().set_track_id_map(track_id, track_name)
    #         return True
    # except (NetworkError, UserError):
    #     pass

    return False


if __name__ == "__main__":
    # download_lrc("蜜蜂 - DUSTCELL", "6oDv2ylQf1fiqOMp7UWcV8")
    # download_lrc("インナアチャイルド - 理芽", "2VviHaihEuSsYo6OOqxJ7m")
    # download_lrc("ice melt - Cö Shu Nie", "07JUoZ3jQ0kr9DwFJeOGlr")
    # download_lrc("ブルーノート - 水槽", "3Ug6cD9VZE2J9eHc5jCASh")
    # download_lrc("Void - DUSTCELL", "5QnnLbeNiTPQn68agY3i6D")
    # download_lrc("蜜蜂 - DUSTCELL", "6oDv2ylQf1fiqOMp7UWcV8")
    pass

