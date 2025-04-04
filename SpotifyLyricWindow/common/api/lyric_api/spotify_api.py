#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import re
import time

import json
import pyotp
import requests

from common.api.user_api.user_auth import SpotifyUserAuth
from common.api.lyric_api.base_lyric_api import BaseMusicApi
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo
from common.config import Config
from common.api.exceptions import UserError, NetworkError
from common.lyric.lyric_type import LrcFile
from common.path import LYRIC_TOKEN_PATH


class SpotifyApi(BaseMusicApi):
    _SEARCH_SONG_ID_URL = "https://api.spotify.com/v1/search?query={}&type=track&offset={}&limit=10"
    _SEARCH_SONG_INFO_URL = "https://api.spotify.com/v1/tracks/{}"
    _FETCH_LYRIC_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{}?format=json&market=from_token"

    _TOKEN_URL = 'https://open.spotify.com/get_access_token?reason=transport&productType=web_player'
    _SERVER_TIME_URL = 'https://open.spotify.com/server-time'
    _SECRET_BASE32 = 'GU2TANZRGQ2TQNJTGQ4DONBZHE2TSMRSGQ4DMMZQGMZDSMZUG4'
    # 参考 https://github.com/akashrchandran/spotify-lyrics-api/
    
    def __init__(self):
        self.auth = SpotifyUserAuth()

        self.web_session = requests.Session()
        dc_token = Config.CommonConfig.ClientConfig.sp_dc
        self.sp_dc = dc_token

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
        self._check_token_expired()
        lyric_token = self._load_lyric_token()

        url = self._FETCH_LYRIC_URL.format(song_id)

        proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
        proxy = {"https": proxy_ip} if proxy_ip else {}

        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "referer": "https://open.spotify.com/",
            "origin": "https://open.spotify.com/",
            "accept": "application/json",
            "app-platform": "WebPlayer",
            "spotify-app-version": "1.2.61.20.g3b4cd5b2",
            "authorization": "Bearer {0}".format(lyric_token["accessToken"])
        }

        lrc_file = LrcFile()
        try:
            res = requests.get(url, headers=header, proxies=proxy)
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

    def _check_token_expired(self):
        cache_data = self._load_lyric_token()
        if 'accessToken' not in cache_data or cache_data['expiration'] < int(time.time() * 1000):
            self._get_lyric_token()

    def _get_lyric_token(self):
        server_time = self._get_server_time()
        totp = self._generate_totp(server_time)
        params = {
            'reason': 'transport',
            'productType': 'web_player',
            'totp': totp,
            'totpServer': totp,
            'totpVer': '5',
            'sTime': str(server_time),
            'cTime': str(server_time) + '.233'
        }
        headers = {
            'Referer': 'https://open.spotify.com/',
            'Origin': 'https://open.spotify.com/',
            'Cookie': f'sp_dc={self.sp_dc}'
        }
        response = requests.get(self._TOKEN_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('isAnonymous'):
            raise UserError("请在配置文件更新sp_dc")

        lyric_token = {'accessToken': data['accessToken'], 'expiration': data['accessTokenExpirationTimestampMs']}
        with LYRIC_TOKEN_PATH.open("w") as f:
            json.dump(lyric_token, f)
        return lyric_token

    def _get_server_time(self):
        proxy_ip = Config.CommonConfig.ClientConfig.proxy_ip
        proxy = {"https": proxy_ip} if proxy_ip else {}
        headers = {
            'Referer': 'https://open.spotify.com/',
            'Origin': 'https://open.spotify.com/',
            'Cookie': f'sp_dc={self.sp_dc}'
        }
        response = requests.get(self._SERVER_TIME_URL, headers=headers, proxies=proxy)
        if response.status_code != 200:
            raise NetworkError("spotify服务器时间获取失败")
        return response.json()['serverTime']

    def _generate_totp(self, server_time):
        totp = pyotp.TOTP(self._SECRET_BASE32, interval=30, digest='sha1')
        return totp.at(int(server_time))

    @staticmethod
    def _load_lyric_token():
        if LYRIC_TOKEN_PATH.exists():
            with LYRIC_TOKEN_PATH.open('r') as f:
                return json.load(f)
        return {}


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

