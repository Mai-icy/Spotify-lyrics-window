#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
from pathlib import Path

from common.config import Config

BASE_PATH = Path(__file__).parent.parent

ORI_LRC_PATH = BASE_PATH / Path(r"download/lyrics")
ORI_TEMP_PATH = BASE_PATH / Path(r"download/temp")

path_config = Config.CommonConfig.PathConfig
if path_config.lyrics_file_path:
    LRC_PATH = Path(path_config.lyrics_file_path)
else:
    LRC_PATH = ORI_LRC_PATH

if path_config.temp_file_path:
    TEMP_PATH = Path(path_config.temp_file_path)
else:
    TEMP_PATH = ORI_TEMP_PATH

TEMP_IMAGE_PATH = TEMP_PATH / "image"

TOKEN_PATH = BASE_PATH / Path(r"resource/token")
LYRIC_TOKEN_PATH = BASE_PATH / Path(r"resource/lyric_token")

LYRIC_DATA_FILE_PATH = LRC_PATH / "lyric.json"
TEMP_DATA_FILE_PATH = TEMP_PATH / "temp.json"

SETTING_TOML_PATH = BASE_PATH / Path(r"resource/setting.toml")

ERROR_LOG_PATH = BASE_PATH / Path(r"resource/error.log")


def path_check():
    """check the path, if not exists, create it"""
    for dir_ in (LRC_PATH, TEMP_PATH, TEMP_IMAGE_PATH):
        if not dir_.exists():
            dir_.mkdir(parents=True)

    for json_file in (LYRIC_DATA_FILE_PATH, TEMP_DATA_FILE_PATH):
        if not json_file.exists():
            with json_file.open("w", encoding="utf-8") as f:
                f.write(json.dumps({}, indent=4, ensure_ascii=False))


path_check()
