#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import re
from typing import List
from time import localtime

import requests

from common.api.api_error import NoneResultError
from common.api.lyric_api.base_lyric_api import BaseMusicApi
from common.lyric.lyric_type import LrcFile, TransType
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo


class CloudMusicWebApi(BaseMusicApi):
    _SEARCH_SONG_ID_URL = 'https://music.163.com/api/search/get/web?&s={}&type=1&offset={}&total=true&limit=10'
    _SEARCH_SONG_INFO_URL = 'http://music.163.com/api/song/detail/?id={}&ids=[{}]'
    _FETCH_LYRIC_URL = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1&rv=-1'

    def search_song_id(self, keyword: str, page: int = 1) -> List[SongSearchInfo]:
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)
        url = self._SEARCH_SONG_ID_URL.format(keyword, (page - 1) * 20)

        res_json = requests.post(url, timeout=4).json()

        if res_json["result"] == {} or res_json['code'] == 400 or res_json["result"]['songCount'] == 0:  # 该关键词没有结果
            raise NoneResultError

        song_info_list = []

        for data in res_json["result"]["songs"]:
            duration = data["duration"] // 1000
            song_data = {
                "songName": data['name'],
                "singer": ','.join(artist_info["name"] for artist_info in data["artists"]),
                "duration": '%d:%d%d' % (duration // 60, duration % 60 // 10, duration % 10),
                "idOrMd5": str(data['id'])
            }
            song_info_list.append(SongSearchInfo(**song_data))
        if song_info_list:
            return song_info_list
        else:
            raise NoneResultError

    def search_song_info(self, song_id: str, *, download_pic: bool = False) -> SongInfo:
        url = self._SEARCH_SONG_INFO_URL.format(song_id, song_id)
        res_json = requests.post(url, timeout=10).json()

        if res_json['code'] == 400 or res_json['code'] == 406:
            raise requests.RequestException("访问过于频繁或接口失效")

        song_json = res_json['songs'][0]
        artists_list = [info["name"] for info in song_json["artists"]]
        duration = song_json["duration"] // 1000

        if download_pic:
            pic_url = song_json["album"]["picUrl"]
            pic_data = requests.get(pic_url, timeout=10).content
            pic_buffer = io.BytesIO(pic_data)
        else:
            pic_buffer = None

        song_info = {
            "singer": ','.join(artists_list),
            "songName": song_json["name"],
            "album": song_json["album"]["name"],
            "year": str(localtime(song_json["album"]["publishTime"] // 1000).tm_year),
            "trackNumber": (song_json["no"], song_json["album"]["size"]),
            "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
            "genre": None,
            "picBuffer": pic_buffer}
        song_info = SongInfo(**song_info)
        return song_info

    def fetch_song_lyric(self, song_id: str) -> LrcFile:
        res_json = requests.get(self._FETCH_LYRIC_URL.format(song_id), timeout=10).json()
        lrc_file = LrcFile()
        lrc_file.load_content(res_json['lrc']['lyric'], TransType.NON)
        if res_json.get('tlyric', None):
            lrc_file.load_content(res_json['tlyric']['lyric'], TransType.CHINESE)
        if res_json.get('romalrc', None):
            lrc_file.load_content(res_json['romalrc']['lyric'], TransType.ROMAJI)
        return lrc_file


if __name__ == '__main__':
    from pprint import pprint

    test_api = CloudMusicWebApi()
    print("\n----test----(search_song_id)")
    pprint(test_api.search_song_id("miku"))
    print("\n----test----(search_song_info)")
    print(test_api.search_song_info("1900488879"))
    print("\n----test----(fetch_song_lyric)")
    pprint(test_api.fetch_song_lyric("1900488879").trans_non_dict)
