#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

from common.path import OFFSET_FILE_PATH


def get_offset_file(track_id: str) -> int:
    """get the offset from offset.json"""
    with OFFSET_FILE_PATH.open(encoding="utf-8") as f:
        data_json = json.load(f)
    return data_json.get(track_id, 0)


def set_offset_file(track_id: str, offset: int):
    """save the offset to offset.json"""
    with OFFSET_FILE_PATH.open(encoding="utf-8") as f:
        data_json = json.load(f)
    data_json[track_id] = offset
    with OFFSET_FILE_PATH.open("w", encoding="utf-8") as f:
        f.write(json.dumps(data_json, indent=4, ensure_ascii=False))




