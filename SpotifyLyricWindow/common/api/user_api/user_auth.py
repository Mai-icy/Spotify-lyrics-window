#!/usr/bin/python
# -*- coding:utf-8 -*-
import base64
import random
import re
import socket
import string
import time

import requests

from common.path import TOKEN_PATH
from common.api.exceptions import NoAuthError
from common.config import cfg


class SpotifyUserAuth:
    AUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    AUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    _instance = None
    _is_init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SpotifyUserAuth, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not self._is_init:
            self.user_token_info = None
            self.client_token_info = None
            self.state = None
            self.auth_code = None
            self.client_id = cfg.get(cfg.client_id)
            self.client_secret = cfg.get(cfg.client_secret)
            self.proxy_ip = cfg.get(cfg.proxy_ip)
            self.proxy = {"https": self.proxy_ip} if self.proxy_ip else {}
            auth = base64.b64encode((self.client_id + ":" + self.client_secret).encode("ascii"))
            self.auth_client_header = {'Authorization': 'Basic ' + auth.decode("ascii")}
            if TOKEN_PATH.exists():
                self.user_token_info = eval(TOKEN_PATH.read_text("utf-8"))
            # self._fetch_client_access_token()

            self._is_init = True

    def load_client_config(self):
        self.client_id = cfg.get(cfg.client_id)
        self.client_secret = cfg.get(cfg.client_secret)
        self.proxy_ip = cfg.get(cfg.proxy_ip)
        self.proxy = {"https": self.proxy_ip} if self.proxy_ip else {}

        auth = base64.b64encode((self.client_id + ":" + self.client_secret).encode("ascii"))
        self.auth_client_header = {'Authorization': 'Basic ' + auth.decode("ascii")}
        try:
            self._fetch_client_access_token()
        except NotImplementedError:
            raise NotImplementedError("请检查client_id以及client_secret是否正确")

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
        auth_code = requests.get(self.AUTH_AUTHORIZE_URL, url_param, proxies=self.proxy)
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
        self.user_token_info = requests.post(self.AUTH_TOKEN_URL, data=form, headers=self.auth_client_header, proxies=self.proxy).json()
        self.user_token_info["expires_at"] = int(time.time()) + self.user_token_info["expires_in"]
        self.save_token()

    def get_fresh_access_token(self):
        refresh_token = self.user_token_info["refresh_token"]
        payloads = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        self.user_token_info = requests.post(self.AUTH_TOKEN_URL, headers=self.auth_client_header, data=payloads, proxies=self.proxy).json()
        if not self.user_token_info.get("expires_in"):
            # print(self.user_token_info)  # {'error': 'invalid_grant', 'error_description': 'Refresh token revoked'}
            raise NoAuthError("请先引导用户完成验证")
        if not self.user_token_info.get("refresh_token"):
            self.user_token_info["refresh_token"] = refresh_token
        self.user_token_info["expires_at"] = int(time.time()) + self.user_token_info["expires_in"]
        self.save_token()

    def save_token(self):
        TOKEN_PATH.write_text(str(self.user_token_info), encoding="utf-8")

    def access_token(self):
        if not self.user_token_info:
            raise NoAuthError("请先引导用户完成验证")
        if int(time.time()) < self.user_token_info["expires_at"]:
            return self.user_token_info['access_token']
        else:
            self.get_fresh_access_token()
            return self.user_token_info['access_token']

    def auth_main(self):
        """for test"""
        print(self.get_user_auth_url())
        self.receive_user_auth_code()
        self.get_user_access_token()

    def get_client_token(self):
        if self.client_token_info["expires_at"] > int(time.time()):
            return self.client_token_info["access_token"]
        else:
            self._fetch_client_access_token()
            return self.client_token_info["access_token"]

    def _fetch_client_access_token(self):
        """获取token"""
        payload = {"grant_type": "client_credentials"}
        response = requests.post(self.AUTH_TOKEN_URL, headers=self.auth_client_header, data=payload, proxies=self.proxy)
        if response.json().get("error") == 'invalid_client':
            raise NotImplementedError("请在设置输入您的client_id以及client_secret")
        response.raise_for_status()
        self.client_token_info = response.json()
        self.client_token_info["expires_at"] = int(time.time()) + self.client_token_info["expires_in"]


if __name__ == "__main__":
    tt = SpotifyUserAuth()

    print(tt.get_user_auth_url())
    print(tt.receive_user_auth_code())
    tt.get_user_access_token()
    print(tt.user_token_info)
    # print(tt.get_fresh_access_token())
    # tt.get_fresh_access_token()
    input()
