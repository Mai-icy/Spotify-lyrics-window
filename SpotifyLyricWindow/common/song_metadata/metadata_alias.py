#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import re
import threading
import time
import unicodedata

from common.api.exceptions import NetworkError, NoneResultError
from common.logger import get_logger
from common.song_metadata.metadata_type import SongInfo, SongAliasInfo


logger = get_logger(__name__)
_lookup_lock = threading.Lock()
_failed_until = 0


def normalize_name(name: str) -> str:
    """仅统一大小写、全半角和空白，不通过模糊相似度推断实体相同。"""
    return ''.join(unicodedata.normalize('NFKC', name or '').casefold().split())


def duration_seconds(duration: str) -> int:
    try:
        minute, second = duration.split(':')
        return int(minute) * 60 + int(second)
    except (AttributeError, TypeError, ValueError):
        return 0


def _match_singers(song_info: SongInfo, song_alias: SongAliasInfo) -> bool:
    if not song_alias.artistNames:
        # 兼容旧数据；没有逐歌手信息时不猜测署名如何拆分。
        return normalize_name(song_info.singer) in map(normalize_name, song_alias.singerNames)
    groups = tuple(frozenset(normalize_name(name) for name in names if normalize_name(name))
                   for names in song_alias.artistNames)
    if not groups or len(groups) > 8:
        return False
    structured = bool(song_info.artistNames)
    remaining = (tuple(map(normalize_name, song_info.artistNames)) if structured else
                 normalize_name(song_info.singer))
    if structured and len(remaining) != len(groups):
        return False

    def match(names, pending):
        if not pending:
            return not names
        if not names:
            return False
        for index, aliases in enumerate(pending):
            rest = pending[:index] + pending[index + 1:]
            if structured:
                if names[0] in aliases and match(names[1:], rest):
                    return True
            else:
                # 仅按已知的完整歌手名消费文本，不把名字里的逗号直接拆开。
                for alias in aliases:
                    prefix = alias + ',' if rest else alias
                    if names.startswith(prefix) and match(names[len(prefix):], rest):
                        return True
        return False

    return match(remaining, groups)


def song_alias_mismatch(song_info: SongInfo, song_alias: SongAliasInfo) -> str:
    """返回别名确认失败的原因，空字符串表示确认成功。"""
    if not song_info or not song_alias:
        return '元数据缺失'
    duration = duration_seconds(song_info.duration)
    alias_duration = duration_seconds(song_alias.duration)
    if not duration or not alias_duration or abs(duration - alias_duration) > 3:
        return '时长缺失或相差超过3秒'
    if normalize_name(song_info.songName) not in map(normalize_name, song_alias.songNames):
        return '歌名不在录音别名中'
    if not _match_singers(song_info, song_alias):
        return '完整歌手署名不匹配'
    # 别名不能抹掉现场、伴奏等版本区别，即使录音时长接近也不能直接认定。
    version_pattern = r'\b(?:live|remix|instrumental|karaoke|rearrange)\b|现场|現場|伴奏|演唱会|カラオケ'
    source_versions = set(re.findall(version_pattern, song_info.songName.lower()))
    target_versions = set(re.findall(version_pattern, (song_alias.songNames[0] + ' ' + song_alias.comment).lower()))
    return '' if source_versions == target_versions else '现场、伴奏等录音版本不一致'


def is_song_alias(song_info: SongInfo, song_alias: SongAliasInfo) -> bool:
    return not song_alias_mismatch(song_info, song_alias)


def get_song_aliases(track_id: str, song_info: SongInfo) -> SongAliasInfo:
    """按歌曲查询并缓存别名，只在自动歌词匹配失败后使用。"""
    global _failed_until
    if not song_info or not song_info.songName or not song_info.singer or not duration_seconds(song_info.duration):
        return None
    # 延迟导入：正常匹配不初始化 MusicBrainz 客户端或缓存管理器。
    from common.api.musicbrainz_api import MusicBrainzApi
    from common.temp_manage import TempFileManage

    song_key = json.dumps(['song-v1', track_id, song_info.songName, song_info.singer, song_info.duration],
                          ensure_ascii=False)
    artist_key = json.dumps(['artist-v1', normalize_name(song_info.singer)], ensure_ascii=False)
    with _lookup_lock:
        try:
            cache = TempFileManage()
            cached = cache.get_musicbrainz_cache(song_key)
            if cached is False:
                return None
            if cached is not None:
                alias = SongAliasInfo(**cached)
                if is_song_alias(song_info, alias):
                    return alias
            if time.monotonic() < _failed_until:
                return None
            api = MusicBrainzApi()
            artist_id = cache.get_musicbrainz_cache(artist_key)
            if artist_id is None:
                try:
                    artists = api.search_artist_id(song_info.singer)
                except NoneResultError:
                    artists = []
                artist_ids = {artist.id for artist in artists
                              if normalize_name(song_info.singer) in map(normalize_name, artist.names)}
                # 同名歌手不依赖搜索分数直接选择；合作署名无法确认时保留原匹配。
                artist_id = artist_ids.pop() if len(artist_ids) == 1 else False
                cache.save_musicbrainz_cache(artist_key, artist_id, 2592000 if artist_id else 86400)
            if not artist_id:
                return None
            songs = api.search_song_id(song_info.songName, artist_id)
            duration = duration_seconds(song_info.duration)
            song_ids = list(dict.fromkeys(song.idOrMd5 for song in songs
                                         if duration and duration_seconds(song.duration) and
                                         abs(duration_seconds(song.duration) - duration) <= 3))
            aliases = []
            # 限制详情请求数；候选过多时不只挑第一条，以免把不同版本合并。
            if len(song_ids) <= 3:
                for song_id in song_ids:
                    alias = api.search_song_info(song_id)
                    if is_song_alias(song_info, alias):
                        aliases.append(alias)
            if len(aliases) == 1:
                cache.save_musicbrainz_cache(song_key, aliases[0]._asdict())
                return aliases[0]
            cache.save_musicbrainz_cache(song_key, False, 86400)
        except NoneResultError:
            try:
                cache.save_musicbrainz_cache(song_key, False, 86400)
            except OSError as e:
                logger.warning('MusicBrainz 缓存保存失败: %s', e)
        except (NetworkError, OSError, ValueError, TypeError, KeyError, AttributeError, IndexError) as e:
            # 服务异常只短暂冷却，不记成“没有别名”，更不改写歌词ID映射。
            _failed_until = time.monotonic() + 30
            logger.warning('MusicBrainz 别名查询暂不可用，保留原匹配: %s', e)
    return None


def get_alias_keywords(song_info: SongInfo, song_alias: SongAliasInfo) -> list:
    """优先尝试中日文歌名与中文歌手名，最多补充两个搜索词。"""
    names = sorted(song_alias.songNames, key=lambda name: not re.search(r'[\u3040-\u9fff]', name))
    singers = sorted(song_alias.singerNames,
                     key=lambda name: not (re.search(r'[\u4e00-\u9fff]', name) and
                                           not re.search(r'[\u3040-\u30ff]', name)))
    original = normalize_name(f'{song_info.songName} - {song_info.singer}')
    keywords = []
    # 先覆盖不同歌名，再尝试其他歌手名，避免两个名额都被繁简体歌手名占用。
    for singer in singers:
        for name in names:
            keyword = f'{name} - {singer}'
            if normalize_name(keyword) != original and keyword not in keywords:
                keywords.append(keyword)
            if len(keywords) == 2:
                return keywords
    return keywords
