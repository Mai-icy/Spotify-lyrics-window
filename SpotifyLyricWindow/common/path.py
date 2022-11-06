#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
from pathlib import Path

TOKEN_PATH = Path(r"resource/token")
LRC_PATH = Path(r"download/lyrics")
CLIENT_ID_SECRET_PATH = Path(r"resource/client_id_secret.json")

OFFSET_FILE_PATH = LRC_PATH / "offset.json"


def path_check():
    """check the path, if not exists, create it"""
    if not LRC_PATH.exists():
        LRC_PATH.mkdir(parents=True)
    if not CLIENT_ID_SECRET_PATH.exists():
        with CLIENT_ID_SECRET_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"client_id": "", "client_secret": ""}, indent=4, ensure_ascii=False))
    if not OFFSET_FILE_PATH.exists():
        with OFFSET_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps({}, indent=4, ensure_ascii=False))


path_check()
