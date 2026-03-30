#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

from common.api.user_api import user_auth
from common.api.user_api.user_auth import SpotifyUserAuth


def test_load_token_from_json(tmp_path, monkeypatch):
    token_file = tmp_path / "token"
    token_file.write_text(json.dumps({"access_token": "abc", "expires_at": 123}), encoding="utf-8")

    monkeypatch.setattr(user_auth, "TOKEN_PATH", token_file)

    data = SpotifyUserAuth._load_token()

    assert data == {"access_token": "abc", "expires_at": 123}


def test_load_token_from_legacy_dict_text(tmp_path, monkeypatch):
    token_file = tmp_path / "token"
    token_file.write_text("{'access_token': 'abc', 'expires_at': 123}", encoding="utf-8")

    monkeypatch.setattr(user_auth, "TOKEN_PATH", token_file)

    data = SpotifyUserAuth._load_token()

    assert data == {"access_token": "abc", "expires_at": 123}


def test_load_token_returns_none_for_invalid_content(tmp_path, monkeypatch):
    token_file = tmp_path / "token"
    token_file.write_text("not a valid token payload", encoding="utf-8")

    monkeypatch.setattr(user_auth, "TOKEN_PATH", token_file)

    assert SpotifyUserAuth._load_token() is None


def test_save_token_writes_utf8_json(tmp_path, monkeypatch):
    token_file = tmp_path / "token"
    monkeypatch.setattr(user_auth, "TOKEN_PATH", token_file)

    auth = SpotifyUserAuth.__new__(SpotifyUserAuth)
    auth.user_token_info = {"access_token": "abc", "refresh_token": "中文", "expires_at": 123}

    SpotifyUserAuth.save_token(auth)

    assert json.loads(token_file.read_text(encoding="utf-8")) == auth.user_token_info


def test_get_user_auth_url_uses_prepared_request():
    auth = SpotifyUserAuth.__new__(SpotifyUserAuth)
    auth.client_id = "client-id"
    auth.state = None
    auth._generate_scope_data = lambda: "scope-a scope-b"
    auth._generate_random_state = lambda: "fixed-state"

    url = SpotifyUserAuth.get_user_auth_url(auth)

    assert "client_id=client-id" in url
    assert "response_type=code" in url
    assert "state=fixed-state" in url
    assert auth.state == "fixed-state"
