#!/usr/bin/python
# -*- coding:utf-8 -*-
import itertools
import re
import threading
import time
from typing import List

import requests

from common.api.exceptions import NoneResultError, NetworkError
from common.song_metadata.metadata_type import ArtistAliasInfo, SongAliasInfo, SongSearchInfo


class MusicBrainzApi:
    _SEARCH_ARTIST_ID_URL = 'https://musicbrainz.org/ws/2/artist/'
    _SEARCH_SONG_ID_URL = 'https://musicbrainz.org/ws/2/recording/'
    _SEARCH_SONG_INFO_URL = 'https://musicbrainz.org/ws/2/recording/{}'
    _SEARCH_SONG_ISRC_URL = 'https://musicbrainz.org/ws/2/isrc/{}'

    header = {'User-Agent': 'SpotifyLyricsWindow/1.0 (https://github.com/Mai-icy/Spotify-lyrics-window)'}
    _request_lock = threading.Lock()
    _last_request_time = 0
    _request_interval = 1.5

    def _request_json(self, url: str, params: dict, *, allow_missing: bool = False):
        # 官方限速要求：https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting
        # 多个实例共用限速；从上一次响应结束计时，重试同样经过此处。
        with self._request_lock:
            for attempt in range(2):
                wait_time = self._request_interval - (time.monotonic() - MusicBrainzApi._last_request_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                try:
                    res = requests.get(url, params={**params, 'fmt': 'json'}, headers=self.header, timeout=4)
                except requests.RequestException as e:
                    raise NetworkError("MusicBrainz 查询失败") from e
                finally:
                    MusicBrainzApi._last_request_time = time.monotonic()

                if allow_missing and res.status_code == 404:
                    raise NoneResultError("该ISRC无对应录音")
                if res.status_code in (429, 500, 502, 503, 504) and attempt == 0:
                    retry_after = res.headers.get('Retry-After', '2')
                    try:
                        wait_time = max(2, float(retry_after))
                    except ValueError:
                        raise NetworkError("MusicBrainz 服务繁忙，请稍后重试")
                    if wait_time > 4:
                        raise NetworkError("MusicBrainz 服务繁忙，请稍后重试")
                    time.sleep(wait_time)
                    continue
                try:
                    res.raise_for_status()
                    res_json = res.json()
                except (requests.RequestException, ValueError) as e:
                    raise NetworkError("MusicBrainz 查询失败") from e
                if not isinstance(res_json, dict) or res_json.get('error'):
                    raise NetworkError("MusicBrainz 返回数据异常")
                return res_json

    @staticmethod
    def _quote_keyword(keyword: str) -> str:
        return '"' + keyword.replace('\\', '\\\\').replace('"', '\\"') + '"'

    @staticmethod
    def _get_alias_names(data: dict, name_key: str) -> tuple:
        names = [data[name_key]]
        names.extend(alias['name'] for alias in data.get('aliases', [])
                     if alias.get('type') != 'Search hint')
        return tuple(dict.fromkeys(name for name in names if isinstance(name, str) and name.strip()))

    @staticmethod
    def _get_duration(duration) -> str:
        seconds = int(duration or 0) // 1000
        return f'{seconds // 60}:{seconds % 60:02d}'

    def search_artist_id(self, keyword: str) -> List[ArtistAliasInfo]:
        # 不限定 artist 字段，使歌手别名也参与搜索。
        res_json = self._request_json(self._SEARCH_ARTIST_ID_URL,
                                      {'query': self._quote_keyword(keyword), 'limit': 5})
        try:
            artists = [ArtistAliasInfo(data['id'], self._get_alias_names(data, 'name'))
                       for data in res_json['artists']]
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            raise NetworkError("MusicBrainz 歌手数据异常") from e
        if not artists:
            raise NoneResultError("该搜索词无对应歌手")
        return artists

    def search_song_id(self, keyword: str, artist_id: str = None) -> List[SongSearchInfo]:
        name = self._quote_keyword(keyword)
        query = f'(recording:{name} OR alias:{name})'
        if artist_id:
            query += f' AND arid:{self._quote_keyword(artist_id)}'
        # 无歌手条件时扩大候选范围；截断结果不能用来判定录音唯一。
        limit = 5 if artist_id else 20
        res_json = self._request_json(self._SEARCH_SONG_ID_URL, {'query': query, 'limit': limit})
        try:
            count = int(res_json.get('count', 0))
            songs = [SongSearchInfo(data['title'], ','.join(artist['name'] for artist in data['artist-credit']),
                                   self._get_duration(data.get('length')), data['id'])
                     for data in res_json['recordings']]
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            raise NetworkError("MusicBrainz 歌曲数据异常") from e
        if count > limit:
            raise NoneResultError("歌曲候选过多，无法确认唯一录音")
        if not songs:
            raise NoneResultError("该搜索词无对应歌曲")
        return songs

    def search_song_info(self, song_id: str) -> SongAliasInfo:
        # 同一次查询获取录音及其歌手别名，而不是仅选取一种首选语言。
        # https://musicbrainz.org/doc/MusicBrainz_API#Lookups
        res_json = self._request_json(self._SEARCH_SONG_INFO_URL.format(song_id),
                                      {'inc': 'aliases+artist-credits+isrcs'})
        if res_json.get('id') != song_id:
            raise NetworkError("MusicBrainz 录音ID与请求不一致")
        return self._get_song_info(res_json)

    def search_song_isrc(self, isrc: str) -> List[SongAliasInfo]:
        # ISRC 查询可能对应多个录音，不直接取第一项。
        # https://musicbrainz.org/doc/MusicBrainz_API#isrc
        isrc = isrc.replace('-', '').strip().upper() if isinstance(isrc, str) else ''
        if not re.fullmatch(r'[A-Z]{2}[A-Z0-9]{3}[0-9]{7}', isrc):
            raise NoneResultError("ISRC格式无效")
        res_json = self._request_json(self._SEARCH_SONG_ISRC_URL.format(isrc),
                                      {'inc': 'aliases+artist-credits+isrcs'}, allow_missing=True)
        try:
            if res_json['isrc'] != isrc:
                raise ValueError('ISRC与请求不一致')
            songs = [self._get_song_info(data) for data in res_json['recordings']]
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            raise NetworkError("MusicBrainz ISRC数据异常") from e
        if not songs:
            raise NoneResultError("该ISRC无对应录音")
        return songs

    def _get_song_info(self, res_json: dict) -> SongAliasInfo:
        """复用普通录音查询和ISRC查询的元数据解析。"""
        try:
            artist_names = []
            for credit in res_json['artist-credit']:
                names = (credit['name'], *self._get_alias_names(credit['artist'], 'name'))
                artist_names.append(tuple(dict.fromkeys(names)))
            # 合作歌曲保留完整歌手组合，不把其中一个歌手当成整首歌的署名。
            singers = tuple(','.join(names) for names in itertools.islice(itertools.product(*artist_names), 32))
            return SongAliasInfo(res_json['id'], self._get_alias_names(res_json, 'title'), singers,
                                 self._get_duration(res_json.get('length')), res_json.get('disambiguation', ''),
                                 tuple(artist_names), tuple(res_json.get('isrcs', ())))
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            raise NetworkError("MusicBrainz 歌曲别名数据异常") from e


if __name__ == '__main__':
    from pprint import pprint

    test_api = MusicBrainzApi()
    print("\n----test----(search_artist_id)")
    pprint(test_api.search_artist_id("sakanaction"))
    print("\n----test----(search_song_id)")
    pprint(test_api.search_song_id("Tsuki no Wan", "01830cc1-8a04-4dfb-9e4a-d557dfda6a93"))
    print("\n----test----(search_song_info)")
    pprint(test_api.search_song_info("d353e814-f027-41fe-9b8f-83bac8aada5f"))
    print("\n----test----(search_song_isrc)")
    pprint(test_api.search_song_isrc("JPPO01805180"))
