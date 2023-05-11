#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import weakref

from common.path import LRC_PATH, LYRIC_DATA_FILE_PATH
from common.lyric.lyric_type import LrcFile, MrcFile, KrcFile


class LyricFileManage:
    """
    歌词管理类（单例）

    lyric.json 文件格式
    {
    "offset": {}
    "no_lyric":{}
    "id2title":{}
    }
    """
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
            keys = ["offset", "no_lyric", "id2title"]

            for base_key in keys:
                if base_key not in self.lyric_data_json:
                    self.lyric_data_json[base_key] = {}

            self.lyric_data_json["title2id"] = {}
            for id_, title in self.lyric_data_json["id2title"].items():
                self.lyric_data_json["title2id"][title] = id_

            self._is_init = True

    def __del__(self):
        LyricFileManage._instance = None
        LyricFileManage._init = False
        self.save_json()

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
            return LrcFile()

    def save_lyric_file(self, track_id: str, lrc_file: LrcFile):
        lrc_file.save_to_mrc(LRC_PATH / (track_id + ".mrc"))
        if track_id in self.lyric_data_json["no_lyric"]:
            title = self.lyric_data_json["no_lyric"][track_id]["track_title"]
            self.lyric_data_json["no_lyric"].pop(track_id)
            self.lyric_data_json["id2title"][track_id] = title
            self.save_json()

    def delete_lyric_file(self, track_id: str):
        if track_id in self.lyric_data_json["id2title"]:
            title = self.lyric_data_json["id2title"][track_id]
            self.lyric_data_json["id2title"].pop(track_id)
            self.lyric_data_json["title2id"].pop(title)
            lrc_path = LRC_PATH / (track_id + ".mrc")
            if lrc_path.exists():
                lrc_path.unlink()

        if track_id in self.lyric_data_json["no_lyric"]:
            self.lyric_data_json["no_lyric"].pop(track_id)
            self.save_json()

    def get_not_found(self, track_id: str) -> dict:
        return self.lyric_data_json["no_lyric"].get(track_id, None)

    def set_not_found(self, track_id: str, track_title: str):
        lrc_path = LRC_PATH / (track_id + ".mrc")
        if lrc_path.exists():
            lrc_path.unlink()

        if not track_title:
            self.lyric_data_json["no_lyric"].pop(track_id)
        else:
            self.lyric_data_json["no_lyric"][track_id] = {"track_title": track_title, "last_time": int(time.time())}
        self.save_json()

    def get_id(self, track_title: str):
        return self.lyric_data_json["title2id"].get(track_title)

    def get_title(self, track_id: str) -> str:
        return self.lyric_data_json["id2title"].get(track_id)

    def set_track_id_map(self, track_id: str, title: str):
        self.lyric_data_json["id2title"][track_id] = title
        self.lyric_data_json["title2id"][title] = track_id
        self.save_json()

    def get_offset_file(self, track_id: str) -> int:
        return self.lyric_data_json["offset"].get(track_id, 0)

    def set_offset_file(self, track_id: str, offset: int):
        self.lyric_data_json["offset"][track_id] = offset
        self.save_json()

    def get_tracks_id_data(self) -> dict:
        return self.lyric_data_json["id2title"]

    def get_not_found_data(self) -> dict:
        return self.lyric_data_json["no_lyric"]

    def save_json(self):
        with LYRIC_DATA_FILE_PATH.open("w", encoding="utf-8") as f:
            keys = ["offset", "no_lyric", "id2title"]
            save_json = {}
            for base_key in keys:
                save_json[base_key] = self.lyric_data_json[base_key]

            f.write(json.dumps(save_json, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    test = LyricFileManage()
