#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
from collections import namedtuple

import requests

from common.api.api_error import *
from common.api.user_api.user_auth import SpotifyUserAuth

UserCurrentPlaying = namedtuple("UserCurrentPlaying", ["progress_ms", "artist", "track_name", "is_playing", "track_id",
                                                       "duration", "api_offset"])


class SpotifyUserApi:
    USER_PLAYER_URL = "https://api.spotify.com/v1/me/player/"

    def __init__(self):
        self.auth = SpotifyUserAuth()

    def _get_auth_header(self):
        auth_header = {
            "Authorization": f"Bearer {self.auth.access_token()}",
            "Content-Type": "application/json"
        }
        return auth_header

    def get_current_playing(self):
        start_time = int(time.time() * 1000)
        res = self._player_http("get", "currently-playing")
        end_time = int(time.time() * 1000)
        offset = end_time - start_time
        res_json = res.json()
        progress_ms = res_json["progress_ms"]
        is_playing = res_json["is_playing"]
        timestamp = res_json["timestamp"]
        if res_json['currently_playing_type'] == "ad":
            return UserCurrentPlaying(progress_ms, None, "ad", is_playing, None, None, offset)
        artist = ", ".join(art["name"] for art in res_json["item"]["artists"])
        if res_json['item'] is None:
            # 用户还在加载歌曲时，item为None
            time.sleep(0.5)
            return self.get_current_playing()

        track_name = res_json["item"]["name"]
        track_id = res_json["item"]["id"]
        duration = res_json["item"]["duration_ms"]
        print(f"正在播放{track_name} - {artist}")
        print(progress_ms)
        print(f"播放状态{is_playing}")
        print(track_id)
        return UserCurrentPlaying(progress_ms, artist, track_name, is_playing, track_id, duration, offset)

    def _get_user_devices(self):
        res_json = self._player_http("get", "devices").json()
        if len(res_json['devices']):
            return res_json['devices'][0]['id']
        else:
            raise NoDevicesError("No device available!")

    def set_user_pause(self):
        return self._player_http("put", "pause", device_id=self._get_user_devices()).json()

    def set_user_resume(self):
        return self._player_http("put", "play", device_id=self._get_user_devices()).json()

    def set_user_next(self):
        return self._player_http("post", "next", device_id=self._get_user_devices()).json()

    def set_user_previous(self):
        return self._player_http("post", "previous", device_id=self._get_user_devices()).json()

    def seek_to_position(self, position_ms):
        return self._player_http("put", "seek", device_id=self._get_user_devices(), position_ms=position_ms).json()

    def _player_http(self, method, url_suffix, **kwargs):
        url = self.USER_PLAYER_URL + url_suffix
        func = getattr(requests, method)
        res = func(url, headers=self._get_auth_header(), params=kwargs)
        if res.status_code == 204:
            raise NoActiveUser("no user active")
        res_json = res.json()
        if res_json.get("error") and res_json.get("error").get('reason') == 'PREMIUM_REQUIRED':
            raise NoPermission("Premium required!")
        return res


if __name__ == "__main__":
    tt = SpotifyUserApi()
    tt.get_current_playing()

