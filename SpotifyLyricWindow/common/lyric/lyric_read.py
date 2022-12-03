#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time

from common.path import LRC_PATH, NOT_FOUND_LRC_FILE_PATH
from common.lyric.lyric_type import LrcFile, MrcFile, KrcFile
from common.lyric.lyric_error import NotLyricFound


def is_lyric_exist(track_id: str) -> bool:
    lrc_path = LRC_PATH / (track_id + '.mrc')
    return lrc_path.exists()


def get_not_found_file(track_id: str) -> dict:
    with NOT_FOUND_LRC_FILE_PATH.open(encoding="utf-8") as f:
        data_json = json.load(f)
    return data_json.get(track_id, None)


def set_not_found_file(track_id: str, track_title: str):
    with NOT_FOUND_LRC_FILE_PATH.open(encoding="utf-8") as f:
        data_json = json.load(f)
    if not track_title:
        data_json.pop(track_id)
    else:
        data_json[track_id] = {"track_title": track_title, "last_time": int(time.time())}
    with NOT_FOUND_LRC_FILE_PATH.open("w", encoding="utf-8") as f:
        f.write(json.dumps(data_json, indent=4, ensure_ascii=False))


def read_lyric_file(track_id: str):
    for file in LRC_PATH.iterdir():
        if file.name.startswith(track_id):
            if file.suffix == ".mrc":
                return MrcFile(file)
            elif file.suffix == ".lrc":
                return LrcFile(file)
            elif file.suffix == ".krc":
                return KrcFile(file)
    else:
        raise NotLyricFound("未找到歌词文件")








