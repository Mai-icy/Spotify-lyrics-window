#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import re
import time
from typing import List

import requests

from common.api.api_error import NoneResultError
from common.lyric_type.lyric_decode import LrcFile, TransType
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo


class CloudMusicWebApi:
    _search_url = 'https://music.163.com/api/search/get/web?&s={}&type=1&offset={}&total=true&limit=20'
    _song_info_url = 'http://music.163.com/api/song/detail/?id={}&ids=[{}]'
    _download_lrc_url = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1&rv=-1'  # get 需要歌曲id

    def get_song_info(self, song_id: str) -> SongInfo:
        """
        Get filtered song information based on song ID in CloudMusic API.

        :param song_id: song ID in API.
        :return: Filtered song information in dict.
        """
        res_json = requests.post(self._song_info_url.format(song_id, song_id), timeout=10).json()
        if res_json['code'] == 400 or res_json['code'] == 406:
            raise requests.RequestException("访问过于频繁或接口失效")
        song_json = res_json['songs'][0]
        artists_list = [info["name"] for info in song_json["artists"]]
        # todo genre 曲目风格在json中并未找到
        duration = song_json["duration"] // 1000

        pic_url = song_json["album"]["picUrl"]
        pic_data = requests.get(pic_url, timeout=10).content
        pic_buffer = io.BytesIO(pic_data)

        song_info = {
            "singer": ','.join(artists_list),
            "songName": song_json["name"],
            "album": song_json["album"]["name"],
            "year": str(time.localtime(song_json["album"]["publishTime"] // 1000).tm_year),
            "trackNumber": (song_json["no"], song_json["album"]["size"]),
            "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
            "genre": None,
            "picBuffer": pic_buffer}
        song_info = SongInfo(**song_info)
        return song_info

    def search_data(self, keyword: str, page: int = 0) -> List[SongSearchInfo]:
        """
        Get rough information about search term results songs.

        :param page: page of search api
        :param keyword: keyword
        :return: A list containing brief information about the search results.
        """
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)
        res_json = requests.post(self._search_url.format(keyword, page * 20), timeout=4).json()
        res_list = []
        if res_json["result"] == {} or res_json['code'] == 400 or res_json["result"]['songCount'] == 0:  # 该关键词没有结果数据
            raise NoneResultError
        for data in res_json["result"]["songs"]:
            duration = data["duration"] // 1000
            artists_list = []
            for artist_info in data["artists"]:
                artists_list.append(artist_info["name"])
            song_data = {
                "idOrMd5": str(data['id']),
                "songName": data['name'],
                "singer": ','.join(artists_list),
                "duration": '%d:%d%d' % (duration // 60, duration % 60 // 10, duration % 10),
            }
            res_list.append(SongSearchInfo(**song_data))
        return res_list

    def get_lrc(self, song_id: str) -> LrcFile:
        """
        Download the lyrics file of the corresponding song.
        """
        res_json = requests.get(self._download_lrc_url.format(song_id), timeout=10).json()
        lrc_file = LrcFile()
        lrc_file.load_content(res_json['lrc']['lyric'], TransType.NON)
        if res_json.get('tlyric', None):
            lrc_file.load_content(res_json['tlyric']['lyric'], TransType.CHINESE)
        if res_json.get('romalrc', None):
            lrc_file.load_content(res_json['romalrc']['lyric'], TransType.ROMAJI)
        return lrc_file


if __name__ == '__main__':
    # todo 各种错误的排查
    a = CloudMusicWebApi()
    print(a.search_data("ブルーノート - 水槽")[0].idOrMd5)
    # lrc = a.get_lrc(a.search_data("ice melt - Cö Shu Nie")[0].idOrMd5)
    # print(lrc.trans_romaji_dict)
    # lrc.save_to_mrc("1.mrc")



    # print(a.search_data('CheerS-Claris', 0))
    # b = a.get_song_info("1900488879")
    # print(b)
    # print(b.get_content('romaji'))
    # a.download_lrc(1887467089)
