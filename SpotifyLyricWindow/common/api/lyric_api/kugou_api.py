#!/usr/bin/python
# -*- coding:utf-8 -*-
import base64
import io
import re
from typing import List, Dict

import requests

from common.api.api_error import NoneResultError
from common.lyric_type.lyric_decode import KrcFile
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0a1) Gecko/20110623 Firefox/7.0a1 Fennec/7.0a1'}


class KugouApi:
    _get_hash_search_url = 'http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={}&page={' \
                           '}&pagesize=20&showtype=1 '
    _get_key_search_url = 'http://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={}'
    _get_lrc_url = 'http://lyrics.kugou.com/download?ver=1&client=pc&id={}&accesskey={}&fmt={}&charset=utf8'
    _album_info_url = 'http://mobilecdn.kugou.com/api/v3/album/info?albumid={}&plat=0&pagesize=100&area_code=1'
    _song_info_url = 'http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={}'
    # 获取hash值需要搜索关键词。获取access_key和id需要hash值。下载文件需要access_key和id

    def __init__(self):
        self.total_num = 0

    def search_hash(self, keyword: str, page: object = 1) -> List[SongSearchInfo]:
        """
        Query the basic information and MD5 value of a song.

        :rtype: object
        :param keyword: The words you want to search for
        :param page: the number of page
        :return: Contains a list of basic song information
        """
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)
        url = self._get_hash_search_url.format(keyword, page)
        res_json = requests.get(url, headers=header, timeout=10).json()
        song_info_list = []
        self.total_num = res_json['data']['total']
        for data in res_json['data']['info']:
            duration = data["duration"]
            # album = data["duration"]
            # suffix = "." + data["extname"],
            song_info = {
                "singer": data["singername"],
                "songName": data["songname"],
                "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
                "idOrMd5": data["hash"]
            }
            song_info_list.append(SongSearchInfo(**song_info))
        if song_info_list:
            return song_info_list
        else:
            raise NoneResultError

    def get_song_info(self, md5: str) -> SongInfo:
        """
        Get filtered song information based on song ID in CloudMusic API.

        :param md5: md5 of song.
        :return: Filtered song information in dict.
        """
        song_json = requests.get(self._song_info_url.format(md5), headers=header, timeout=4).json()
        duration = song_json["timeLength"]
        album_img = str(song_json["album_img"])

        album_id = song_json["albumid"]  # album_id = 0
        if album_id == 0:
            album = None
            year = None
        else:
            album_json = requests.get(self._album_info_url.format(album_id), headers=header, timeout=4).json()
            album = album_json["data"].get("albumname", None)
            year = album_json["data"].get("publishtime", None)

        song_info = {
            "singer": song_json["author_name"],
            "songName": song_json["songName"],
            "album": album,
            "year": year,  # 例 '2021-08-11 00:00:00'
            "trackNumber": None,  # 实在难搞w
            "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
            "genre": None}
        return SongInfo(**song_info)

    def get_lrc_info(self, md5: str) -> List[Dict[str, str]]:
        """
        Obtain the lyrics information and key to be downloaded using the MD5 value.

        :param md5: MD5 value of song.
        :return: Contains a list of basic lyrics data.
        """
        url = self._get_key_search_url.format(md5)
        res_json = requests.get(url, headers=header, timeout=4).json()
        if res_json['errcode'] != 200:
            raise requests.RequestException(res_json["info"])
        res_list = []
        for data in res_json['candidates']:
            duration = data["duration"] // 1000
            lyric_info = {
                "songName": data["song"],
                "id": data["id"],
                "key": data["accesskey"],
                "score": data["score"],
                "source": data["product_from"],
                "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}'
            }
            res_list.append(lyric_info)
        if res_list:
            return res_list
        else:
            raise NoneResultError

    def get_lrc(self, lyric_info: dict) -> KrcFile:
        """
        Get lyric content.

        :param lyric_info: The info of lyric.
        :return: Content of the lyrics.
        """
        url = self._get_lrc_url.format(lyric_info["id"], lyric_info["key"], 'krc')
        res_json = requests.get(url, timeout=4).json()
        content = res_json['content']
        result = base64.b64decode(content.encode())

        krc_file = KrcFile()
        krc_file.load_content(result)
        return krc_file


if __name__ == '__main__':
    a = KugouApi()
    print(a.search_hash("ice melt - Cö Shu Nie")[0])
    print(a.get_song_info('acca34babe1e795a6ddc49167a3c0993'))
    lrc = a.get_lrc_info('acca34babe1e795a6ddc49167a3c0993')[0]
    b = a.get_lrc(lrc)
    print(b.save_to_mrc('1.mrc'))
