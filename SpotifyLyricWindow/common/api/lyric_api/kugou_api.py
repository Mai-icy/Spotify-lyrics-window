#!/usr/bin/python
# -*- coding:utf-8 -*-
import base64
import io
import re
from typing import List, Dict

import requests

from common.api.exceptions import NoneResultError, NetworkError
from common.api.lyric_api.base_lyric_api import BaseMusicApi
from common.lyric.lyric_type import KrcFile
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo


class KugouApi(BaseMusicApi):
    _SEARCH_SONG_ID_URL = 'http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={}&page={' \
                          '}&pagesize=20&showtype=1 '
    _SEARCH_SONG_INFO_URL = 'http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={}'
    _FETCH_LYRIC_URL = 'http://lyrics.kugou.com/download?ver=1&client=pc&id={}&accesskey={}&fmt={}&charset=utf8'

    _GET_KEY_SEARCH_URL = 'http://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={}'
    _SEARCH_ALBUM_INFO_URL = 'http://mobilecdn.kugou.com/api/v3/album/info?albumid={}&plat=0&pagesize=100&area_code=1'

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0a1) Gecko/20110623 Firefox/7.0a1 Fennec/7.0a1'}

    # 获取hash值需要搜索关键词。获取access_key和id需要hash值。下载歌词文件需要access_key和id

    def search_song_id(self, keyword: str, page: int = 1) -> List[SongSearchInfo]:
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)
        url = self._SEARCH_SONG_ID_URL.format(keyword, page)
        try:
            res_json = requests.get(url, headers=self.header, timeout=4, proxies={"https": None, "http": None}).json()
        except requests.exceptions.RequestException as e:
            raise NetworkError("酷狗查询歌词失败") from e

        song_info_list = []

        for data in res_json['data']['info']:
            duration = data["duration"]
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
            raise NoneResultError("该搜索词无对应歌曲")

    def search_song_info(self, md5: str, *, download_pic: bool = False, pic_size: int = 0) -> SongInfo:
        try:
            song_json = requests.get(self._SEARCH_SONG_INFO_URL.format(md5), headers=self.header, timeout=4,
                                     proxies={"https": None, "http": None}).json()
        except requests.RequestException as e:
            raise NetworkError("酷狗搜索歌词信息失败") from e

        if song_json.get("errcode") != 0:
            raise NetworkError("无法获取kugou歌词")

        duration = song_json["timeLength"]
        album_img = str(song_json["album_img"])
        year = album = None
        album_id = song_json["albumid"]  # if not found, the 'album_id' is 0
        if album_id:
            try:
                album_json = requests.get(self._SEARCH_ALBUM_INFO_URL.format(album_id),
                                          headers=self.header, timeout=4, proxies={"https": None, "http": None}).json()
            except requests.RequestException as e:
                raise NetworkError("酷狗搜索歌词专辑信息失败") from e
            album = album_json["data"].get("albumname", None)
            year = album_json["data"].get("publishtime", None)  # like '2021-08-11 00:00:00'

        if not pic_size:
            pic_url = album_img.format(size=pic_size)
        else:
            pic_url = album_img.replace("/{size}/", "/")  # original pic

        if download_pic and pic_url:
            try:
                pic_data = requests.get(pic_url, timeout=10, proxies={"https": None, "http": None}).content
            except requests.RequestException as e:
                raise NetworkError("酷狗获取专辑图片失败") from e
            pic_buffer = io.BytesIO(pic_data)
        else:
            pic_buffer = None

        song_info = {
            "singer": song_json["author_name"],
            "songName": song_json["songName"],
            "album": album,
            "year": year[:4] if year else None,
            "trackNumber": None,
            "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
            "genre": None,
            "picBuffer": pic_buffer
        }
        return SongInfo(**song_info)

    def fetch_song_lyric(self, song_id: str) -> KrcFile:
        lrc_info_list = self._get_lrc_info(song_id)
        return self._get_lrc(lrc_info_list[0])

    def _get_lrc_info(self, md5: str) -> List[Dict[str, str]]:
        """
        Obtain the lyrics information and key to be downloaded using the MD5 value.

        :param md5: MD5 value of song.
        :return: Contains a list of basic lyrics data.
        """
        url = self._GET_KEY_SEARCH_URL.format(md5)
        try:
            res_json = requests.get(url, headers=self.header, timeout=4, proxies={"https": None, "http": None}).json()
        except requests.RequestException as e:
            raise NetworkError("获取酷狗歌词信息失败") from e
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
            raise NoneResultError("该下载歌词无内容")

    def _get_lrc(self, lyric_info: dict) -> KrcFile:
        """
        Get lyric content.

        :param lyric_info: The info of lyric.
        :return: Content of the lyrics.
        """
        url = self._FETCH_LYRIC_URL.format(lyric_info["id"], lyric_info["key"], 'krc')
        try:
            res_json = requests.get(url, timeout=4, proxies={"https": None, "http": None}).json()
        except requests.RequestException as e:
            raise NetworkError("酷狗下载歌词失败") from e
        content = res_json['content']
        result = base64.b64decode(content.encode())

        krc_file = KrcFile()
        krc_file.load_content(result)
        return krc_file


if __name__ == '__main__':
    from pprint import pprint

    test_api = KugouApi()
    print("\n----test----(search_song_id)")
    pprint(test_api.search_song_id("miku"))
    print("\n----test----(search_song_info)")
    print(test_api.search_song_info("acca34babe1e795a6ddc49167a3c0993"))
    print("\n----test----(fetch_song_lyric)")
    pprint(test_api.fetch_song_lyric("acca34babe1e795a6ddc49167a3c0993").trans_non_dict)
