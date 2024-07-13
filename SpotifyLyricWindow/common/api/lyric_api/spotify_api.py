#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import re

import requests

from common.api.user_api.user_auth import SpotifyUserAuth
from common.api.lyric_api.base_lyric_api import BaseMusicApi
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo
from common.config import Config
from common.api.exceptions import UserError, NetworkError
from common.lyric.lyric_type import LrcFile


class SpotifyApi(BaseMusicApi):
    _SEARCH_SONG_ID_URL = "https://api.spotify.com/v1/search?query={}&type=track&offset={}&limit=10"
    _SEARCH_SONG_INFO_URL = "https://api.spotify.com/v1/tracks/{}"
    _FETCH_LYRIC_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{}?format=json&market=from_token"

    _TOKEN_URL = 'https://open.spotify.com/get_access_token?reason=transport&productType=web_player'

    def __init__(self):
        self.auth = SpotifyUserAuth()

        self.web_session = requests.Session()
        dc_token = Config.CommonConfig.ClientConfig.sp_dc
        self.web_session.cookies.set('sp_dc', dc_token)
        self.web_session.headers['User-Agent'] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, "
                                                  "like Gecko) Chrome/101.0.4951.41 Safari/537.36")
        self.web_session.headers['app-platform'] = 'WebPlayer'

        self.is_login = False
        # self._web_login()

    def _web_login(self):
        proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
        proxy = {"https": proxy_ip} if proxy_ip else {}
        try:
            req = self.web_session.get(self._TOKEN_URL, allow_redirects=False, proxies=proxy)
            token = req.json()
            self.web_session.headers['authorization'] = f"Bearer {token['accessToken']}"
            self.is_login = True
        except Exception as e:
            raise UserError("请在配置文件更新sp_dc") from e

    def search_song_id(self, keyword: str, page: int = 1):
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)

        url = self._SEARCH_SONG_ID_URL.format(keyword, (page - 1) * 10)

        proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
        proxy = {"https": proxy_ip} if proxy_ip else {}
        try:
            res_json = requests.get(url, headers=self._get_token(), proxies=proxy).json()
        except requests.RequestException as e:
            raise NetworkError("spotify查找歌曲失败") from e
        song_info_list = []
        for data in res_json['tracks']['items']:
            artists_list = [info["name"] for info in data["artists"]]
            duration = data["duration_ms"] // 1000
            song_info = {
                "singer": ','.join(artists_list),
                "songName": data["name"],
                "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
                "idOrMd5": data["id"]
            }
            song_info_list.append(SongSearchInfo(**song_info))
        return song_info_list

    def search_song_info(self, song_id: str, *, download_pic: bool = False, pic_size: int = 0):
        url = self._SEARCH_SONG_INFO_URL.format(song_id)
        proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
        proxy = {"https": proxy_ip} if proxy_ip else {}
        try:
            song_json = requests.get(url, headers=self._get_token(), proxies=proxy).json()
        except requests.RequestException as e:
            raise NetworkError("spotify查询歌曲数据失败") from e
        if song_json.get("error"):
            raise NetworkError("spotify查询歌曲数据失败")

        duration = int(song_json["duration_ms"]) // 1000

        if download_pic:
            if not pic_size:
                pic_size = 640

            pic_jsons = [pic_url for pic_url in song_json["album"]["images"] if pic_url['height'] == pic_size]
            if pic_jsons:
                pic_json = pic_jsons[0]
                pic_url = pic_json["url"]
                proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
                proxy = {"https": proxy_ip} if proxy_ip else {}
                pic_data = requests.get(pic_url, timeout=10, proxies=proxy).content
                pic_buffer = io.BytesIO(pic_data)
            else:
                pic_buffer = None
        else:
            pic_buffer = None

        song_info = {
            "singer": ','.join(info["name"] for info in song_json["artists"]),
            "songName": song_json["name"],
            "album": song_json["album"]["name"],
            "year": song_json["album"]["release_date"][:4],
            "trackNumber": (song_json["track_number"], None),
            "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
            "genre": None,
            "picBuffer": pic_buffer}
        return SongInfo(**song_info)

    def fetch_song_lyric(self, song_id: str):
        if not self.is_login:
            self._web_login()

        url = self._FETCH_LYRIC_URL.format(song_id)

        proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
        proxy = {"https": proxy_ip} if proxy_ip else {}

        lrc_file = LrcFile()
        try:
            res = self.web_session.get(url, proxies=proxy)
        except requests.RequestException:
            raise NetworkError("spotify歌词api获取失败")
        if res.status_code == requests.status_codes.codes.not_found:
            return lrc_file
        if res.status_code == requests.status_codes.codes.unauthorized:
            self.is_login = False
            raise UserError("web 会话未登录")
        if res.status_code in (requests.status_codes.codes.forbidden, requests.status_codes.codes.bad):
            self.is_login = False
            raise UserError("web token已失效, 请重新获取")

        res_json = res.json()

        for line in res_json['lyrics']['lines']:
            lrc_file.trans_non_dict[int(line['startTimeMs'])] = line['words']

        return lrc_file

    def _get_token(self):
        return {"Authorization": "Bearer {0}".format(self.auth.get_client_token()),
                "Content-Type": "application/json"}


if __name__ == "__main__":
    from pprint import pprint

    test_api = SpotifyApi()
    test_api.auth.load_client_config()
    print("\n----test----(search_song_id)")
    pprint(test_api.search_song_id("miku"))
    print("\n----test----(search_song_info)")
    print(test_api.search_song_info("5mJ8Sj9EqT9UgpWY1RnEi2", download_pic=True))
    print("\n----test----(fetch_song_lyric)")
    pprint(test_api.fetch_song_lyric("6CIQOFf01zQ9qJaqhD6rlH").trans_non_dict)

