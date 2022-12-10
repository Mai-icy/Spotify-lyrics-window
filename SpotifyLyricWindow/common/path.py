#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
from pathlib import Path
BASE_PATH = Path(__file__).parent.parent

LRC_PATH = BASE_PATH / Path(r"download/lyrics")
TEMP_PATH = BASE_PATH / Path(r"download/temp")
TEMP_IMAGE_PATH = TEMP_PATH / "image"

TOKEN_PATH = BASE_PATH / Path(r"resource/token")

LYRIC_DATA_FILE_PATH = LRC_PATH / "lyric.json"
TEMP_DATA_FILE_PATH = TEMP_PATH / "temp.json"

SETTING_TOML_PATH = BASE_PATH / Path(r"resource/setting.toml")


def path_check():
    """check the path, if not exists, create it"""
    for dir_ in (LRC_PATH, TEMP_PATH, TEMP_IMAGE_PATH):
        if not dir_.exists():
            dir_.mkdir(parents=True)

    for json_file in (LYRIC_DATA_FILE_PATH, TEMP_DATA_FILE_PATH):
        if not json_file.exists():
            with json_file.open("w", encoding="utf-8") as f:
                f.write(json.dumps({}, indent=4, ensure_ascii=False))

    if not SETTING_TOML_PATH.exists():
        SETTING_TOML_PATH.write_text("")


path_check()
