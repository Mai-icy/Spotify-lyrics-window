#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import random
import re
from time import localtime
from typing import List

import requests

from common.api.exceptions import NoneResultError, NetworkError
from common.api.lyric_api.base_lyric_api import BaseMusicApi
from common.config import Config
from common.lyric.lyric_type import LrcFile, TransType
from common.path import RESOURCE_PATH
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo


class CloudMusicWebApi(BaseMusicApi):
    _SEARCH_SONG_ID_URL = 'https://music.163.com/api/search/get/web?&s={}&type=1&offset={}&total=true&limit=10'
    _SEARCH_SONG_INFO_URL = 'http://music.163.com/api/song/detail/?id={}&ids=[{}]'
    _FETCH_LYRIC_URL = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1&rv=-1'
    _USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    _MAINLAND_IP_PATH = RESOURCE_PATH / 'data' / 'mainland_ip.txt'

    @staticmethod
    def _get_proxy():
        proxy_ip = Config.CommonConfig.ClientConfig.cloudmusic_proxy_ip
        return {"https": proxy_ip, "http": proxy_ip} if proxy_ip else {}

    @classmethod
    def _generate_mainland_ip(cls):
        ip_lines = cls._MAINLAND_IP_PATH.read_text(encoding='utf-8').splitlines()
        mainland_ip_pool = [ip.strip() for ip in ip_lines if ip.strip()]
        if not mainland_ip_pool:
            raise ValueError("mainland_ip.txt is empty")
        return random.choice(mainland_ip_pool)

    @classmethod
    def _get_or_create_mainland_ip(cls):
        mainland_ip = Config.CommonConfig.ClientConfig.mainland_ip
        if mainland_ip:
            return mainland_ip

        mainland_ip = cls._generate_mainland_ip()
        Config.CommonConfig.ClientConfig.mainland_ip = mainland_ip
        Config.save_config()
        return mainland_ip

    @classmethod
    def _build_headers(cls):
        headers = {"User-Agent": cls._USER_AGENT}
        mainland_ip = Config.CommonConfig.ClientConfig.mainland_ip
        if mainland_ip:
            headers.update({
                "X-Real-IP": mainland_ip,
                "X-Forwarded-For": mainland_ip
            })
        return headers

    def _request_json(self, method: str, url: str, **kwargs):
        return getattr(requests, method)(url, headers=self._build_headers(), **kwargs).json()

    def search_song_id(self, keyword: str, page: int = 1, _retry: bool = True) -> List[SongSearchInfo]:
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)
        url = self._SEARCH_SONG_ID_URL.format(keyword, (page - 1) * 20)
        try:
            res_json = requests.post(
                url,
                timeout=4,
                headers=self._build_headers(),
                proxies=self._get_proxy(),
            ).json()
        except requests.exceptions.RequestException as e:
            raise NetworkError("网易云搜索歌词出错") from e

        if res_json.get("abroad"):
            if _retry:
                self._get_or_create_mainland_ip()
                return self.search_song_id(keyword, page, _retry=False)
            raise NoneResultError
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

    def search_song_info(self, song_id: str, *, download_pic: bool = False, pic_size: int = 0) -> SongInfo:
        url = self._SEARCH_SONG_INFO_URL.format(song_id, song_id)
        try:
            res_json = requests.post(
                url,
                timeout=10,
                headers=self._build_headers(),
                proxies=self._get_proxy(),
            ).json()
        except requests.exceptions.RequestException as e:
            raise NetworkError("网易云查找歌词信息出错") from e

        if res_json['code'] == 400 or res_json['code'] == 406:
            raise NetworkError("访问过于频繁或接口失效")

        song_json = res_json['songs'][0]
        artists_list = [info["name"] for info in song_json["artists"]]
        duration = song_json["duration"] // 1000
        if download_pic:
            param = {} if not pic_size else {"param": f"{pic_size}y{pic_size}"}
            pic_url = song_json["album"]["picUrl"]
            try:
                pic_data = requests.get(
                    pic_url,
                    timeout=10,
                    params=param,
                    headers=self._build_headers(),
                    proxies=self._get_proxy(),
                ).content
            except requests.exceptions.RequestException as e:
                raise NetworkError("网易云歌曲图片获取失败") from e
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
            "picBuffer": pic_buffer,
        }
        return SongInfo(**song_info)

    def fetch_song_lyric(self, song_id: str) -> LrcFile:
        try:
            res_json = requests.get(
                self._FETCH_LYRIC_URL.format(song_id),
                timeout=10,
                headers=self._build_headers(),
                proxies=self._get_proxy(),
            ).json()
        except requests.exceptions.RequestException as e:
            raise NetworkError("网易云下载歌词失败") from e
        lrc_file = LrcFile()
        lrc_file.load_content(res_json['lrc']['lyric'], TransType.NON)
        if res_json.get('tlyric'):
            lrc_file.load_content(res_json['tlyric']['lyric'], TransType.CHINESE)
        if res_json.get('romalrc'):
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
