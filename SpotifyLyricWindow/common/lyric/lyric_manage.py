#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import weakref

from common.path import LRC_PATH, LYRIC_DATA_FILE_PATH
from common.lyric.lyric_type import LrcFile, MrcFile, KrcFile
from common.lyric.lyric_error import NotLyricFound


class LyricFileManage:
    _instance = None
    _is_init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            instance = super(LyricFileManage, cls).__new__(cls, *args, **kwargs)
            cls._instance = weakref.ref(instance)
            return instance
        return cls._instance()

    def __init__(self):
        if not self._is_init:
            with LYRIC_DATA_FILE_PATH.open(encoding="utf-8") as f:
                self.lyric_data_json = json.load(f)
            keys = ["offset", "no_lyric", "title2id", "id2title"]

            for base_key in keys:
                if base_key not in self.lyric_data_json:
                    self.lyric_data_json[base_key] = {}

            self._is_init = True

    def __del__(self):
        with LYRIC_DATA_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.lyric_data_json, indent=4, ensure_ascii=False))

    @staticmethod
    def is_lyric_exist(track_id: str) -> bool:
        lrc_path = LRC_PATH / (track_id + '.mrc')
        return lrc_path.exists()

    @staticmethod
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

    def get_not_found(self, track_id: str) -> dict:
        return self.lyric_data_json["no_lyric"].get(track_id, None)

    def set_not_found(self, track_id: str, track_title: str):
        if not track_title:
            self.lyric_data_json["no_lyric"].pop(track_id)
        else:
            self.lyric_data_json["no_lyric"][track_id] = {"track_title": track_title, "last_time": int(time.time())}

    def get_title(self, track_id) -> str:
        return self.lyric_data_json["id2title"].get(track_id)

    def get_track_id(self, title) -> str:
        return self.lyric_data_json["title2id"].get(title)

    def set_track_id_map(self, track_id, title):
        self.lyric_data_json["title2id"][title] = track_id
        self.lyric_data_json["id2title"][track_id] = title

    def get_offset_file(self, track_id: str) -> int:
        return self.lyric_data_json["offset"].get(track_id, 0)

    def set_offset_file(self, track_id: str, offset: int):
        self.lyric_data_json["offset"][track_id] = offset


"""
lyric.json 文件格式
{
"offset": {}
"no_lyric":{}
"title2id":{}
"id2title":{}
}

"""

if __name__ == "__main__":
    test = LyricFileManage()
