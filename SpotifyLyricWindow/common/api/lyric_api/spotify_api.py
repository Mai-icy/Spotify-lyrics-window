#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
import io
import time

import base64
import requests
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo


from ..get_client_id_secret import get_client_id_secret


CLIENT_ID, CLIENT_SECRET = get_client_id_secret()


class SpotifyAuth:
    AUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    AUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret):
        self.token_info = None
        self.client_id = client_id
        self.client_secret = client_secret

        auth = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode("ascii"))
        self.auth_header = {'Authorization': 'Basic ' + auth.decode("ascii")}
        self._fetch_access_token()

    def get_token(self):
        if self.token_info["expires_at"] > int(time.time()):
            return self.token_info["access_token"]
        else:
            self._fetch_access_token()
            return self.token_info["access_token"]

    def _fetch_access_token(self):
        """获取token"""
        payload = {"grant_type": "client_credentials"}
        response = requests.post(self.AUTH_TOKEN_URL, headers=self.auth_header, data=payload)
        response.raise_for_status()
        self.token_info = response.json()
        self.token_info["expires_at"] = int(time.time()) + self.token_info["expires_in"]


class SpotifyApi:
    SEARCH_URL = "https://api.spotify.com/v1/search"

    def __init__(self):
        self.auth = SpotifyAuth(CLIENT_ID, CLIENT_SECRET)
        self.session = requests.session()

    def get_token(self):
        return {"Authorization": "Bearer {0}".format(self.auth.get_token()),
                "Content-Type": "application/json"}

    def search_data(self, keyword: str, offset: int = 0, limit=10):
        keyword = re.sub(r"|[!@#$%^&*/]+", "", keyword)
        params = {
            "query": keyword,
            "type": "track",
            "offset": offset,
            "limit": limit
        }
        res_json = self.session.get(self.SEARCH_URL, headers=self.get_token(), params=params).json()
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

    def get_song_info(self, song_id: str) -> SongInfo:
        url = "https://api.spotify.com/v1/tracks/{}".format(song_id)

        song_json = requests.get(url, headers=self.get_token()).json()
        artists_list = [info["name"] for info in song_json["artists"]]
        duration = int(song_json["duration_ms"]) // 1000
        pic_url = song_json["album"]["images"][-1]["url"]
        pic_data = requests.get(pic_url, timeout=10).content
        pic_buffer = io.BytesIO(pic_data)
        song_info = {
            "singer": ','.join(artists_list),
            "songName": song_json["name"],
            "album": song_json["album"]["name"],
            "year": song_json["album"]["release_date"][:4],
            "trackNumber": (song_json["track_number"], None),
            "duration": f'{duration // 60}:{duration % 60 // 10}{duration % 10}',
            "genre": None,
            "picBuffer": pic_buffer}
        return SongInfo(**song_info)


if __name__ == "__main__":
    t1 = SpotifyApi()
    t1.search_data("miku")
    print(t1.get_song_info("5mJ8Sj9EqT9UgpWY1RnEi2"))

