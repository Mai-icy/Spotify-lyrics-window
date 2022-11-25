#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
from pathlib import Path
BASE_PATH = Path(__file__).parent.parent

TOKEN_PATH = BASE_PATH / Path(r"resource/token")
LRC_PATH = BASE_PATH / Path(r"download/lyrics")
CLIENT_ID_SECRET_PATH = BASE_PATH / Path(r"resource/client_id_secret.json")

OFFSET_FILE_PATH = LRC_PATH / "offset.json"
NOT_FOUND_LRC_FILE_PATH = LRC_PATH / "not_found_lyric.json"

SETTING_TOML_PATH = BASE_PATH / Path(r"resource/setting.toml")


def path_check():
    """check the path, if not exists, create it"""
    if not LRC_PATH.exists():
        LRC_PATH.mkdir(parents=True)
    if not CLIENT_ID_SECRET_PATH.exists():
        with CLIENT_ID_SECRET_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"client_id": "", "client_secret": ""}, indent=4, ensure_ascii=False))
    for path_ in (OFFSET_FILE_PATH, NOT_FOUND_LRC_FILE_PATH):
        if not path_.exists():
            with path_.open("w", encoding="utf-8") as f:
                f.write(json.dumps({}, indent=4, ensure_ascii=False))
    if not SETTING_TOML_PATH.exists():
        SETTING_TOML_PATH.write_text("")


path_check()
