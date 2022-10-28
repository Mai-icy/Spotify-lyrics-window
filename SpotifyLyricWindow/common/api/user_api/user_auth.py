#!/usr/bin/python
# -*- coding:utf-8 -*-
import time

import requests
import base64
import random
import string
import socket
import re

from ..get_client_id_secret import get_client_id_secret
from common.path import TOKEN_PATH
from ..api_error import NoAuthError

CLIENT_ID, CLIENT_SECRET = get_client_id_secret()


class SpotifyUserAuth:
    AUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    AUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self):
        self.token_info = None
        self.state = None
        self.auth_code = None
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET

        auth = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode("ascii"))
        self.auth_client_header = {'Authorization': 'Basic ' + auth.decode("ascii")}
        if TOKEN_PATH.exists():
            self.token_info = eval(TOKEN_PATH.read_text("utf-8"))

    @staticmethod
    def _generate_random_state():
        """随机生成16位字符"""
        return ''.join(random.sample(string.ascii_letters, 16))

    @staticmethod
    def _generate_scope_data():
        """访问权限范围"""
        scope_list = [
            'user-read-playback-state',
            'user-modify-playback-state',
            'playlist-read-private',
            'playlist-read-collaborative',
            'user-read-currently-playing',
            'user-read-playback-position',
            'user-read-recently-played'
        ]
        return " ".join(scope_list)

    def get_user_auth_url(self) -> str:
        self.state = self._generate_random_state()
        url_param = {
            "client_id": self.client_id,
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8888/callback',
            'scope': self._generate_scope_data(),
            'state': self.state
        }
        # suffix_url = "?" + "&".join(f"{it[0]}={it[1]}" for it in url_param.items())
        auth_code = requests.get(self.AUTH_AUTHORIZE_URL, url_param)
        return auth_code.url

    def receive_user_auth_code(self) -> str:
        receive_address = ('127.0.0.1', 8888)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(receive_address)
        server.listen(5)
        client, addr = server.accept()
        raw_data = client.recv(1024).decode("utf-8")

        data_pattern = re.compile(r"/callback\?code=(.*)&state=(.*) HTTP/1.1")

        auth_code, state = data_pattern.findall(raw_data)[0]
        if state == self.state:
            # 返回页面
            response = "HTTP/1.1 200 OK\r\n"
            response += "\r\n"
            client.send(response.encode("utf-8"))
            with open("resource/html/auth_done.html", "rb") as f:
                html_content = f.read()
            client.send(html_content)
            client.recv(1024)  # 确保发回html页面提示用户关闭
            self.auth_code = auth_code
            return auth_code
        else:
            raise Exception("验证失败")

    def get_user_access_token(self):
        if not self.auth_code:
            raise NoAuthError("请先完成用户验证")
        form = {
            "code": self.auth_code,
            "redirect_uri": "http://localhost:8888/callback",
            "grant_type": 'authorization_code'
        }
        self.token_info = requests.post(self.AUTH_TOKEN_URL, data=form, headers=self.auth_client_header).json()
        self.token_info["expires_at"] = int(time.time()) + self.token_info["expires_in"]
        self.save_token()

    def get_fresh_access_token(self):
        refresh_token = self.token_info["refresh_token"]
        payloads = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        self.token_info = requests.post(self.AUTH_TOKEN_URL, headers=self.auth_client_header, data=payloads).json()
        if not self.token_info.get("refresh_token"):
            self.token_info["refresh_token"] = refresh_token
        self.token_info["expires_at"] = int(time.time()) + self.token_info["expires_in"]
        self.save_token()

    def save_token(self):
        TOKEN_PATH.write_text(str(self.token_info), encoding="utf-8")

    def access_token(self):
        if not self.token_info:
            raise NoAuthError("请先引导用户完成验证")
        if int(time.time()) < self.token_info["expires_at"]:
            return self.token_info['access_token']
        else:
            self.get_fresh_access_token()
            return self.token_info['access_token']

    def auth_main(self):
        """for test"""
        print(self.get_user_auth_url())
        self.receive_user_auth_code()
        self.get_user_access_token()


if __name__ == "__main__":
    tt = SpotifyUserAuth()

    print(tt.get_user_auth_url())
    print(tt.receive_user_auth_code())
    tt.get_user_access_token()
    print(tt.token_info)
    # print(tt.get_fresh_access_token())
    # tt.get_fresh_access_token()
    input()
