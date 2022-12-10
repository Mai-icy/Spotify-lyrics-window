#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import json
import time
import weakref
from common.path import TEMP_DATA_FILE_PATH, TEMP_PATH, TEMP_IMAGE_PATH


class TempFileManage:
    """临时文件管理类（单例）"""
    TEMP_IMAGE_PATH = TEMP_PATH / "image"
    _instance = None
    _is_init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            instance = super(TempFileManage, cls).__new__(cls, *args, **kwargs)
            cls._instance = weakref.ref(instance)
            return instance
        return cls._instance()

    def __init__(self):
        if not self._is_init:
            with TEMP_DATA_FILE_PATH.open(encoding="utf-8") as f:
                self.temp_data_json = json.load(f)
            keys = ["image"]

            for base_key in keys:
                if base_key not in self.temp_data_json:
                    self.temp_data_json[base_key] = {}

            self._is_init = True

    def delete_temp_image(self, track_id):
        file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
        if file_path.exists():
            file_path.unlink()
        self.temp_data_json["image"].pop(track_id)

    def save_temp_image(self, track_id, img_io: io.BytesIO):
        if not img_io:
            return
        self.temp_data_json["image"][track_id] = {"last_time": int(time.time())}
        self.json_save()
        file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
        file_path.write_bytes(img_io.getvalue())

    def get_temp_image(self, track_id) -> io.BytesIO:
        if track_id in self.temp_data_json["image"]:
            file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
            self.temp_data_json["image"][track_id]["last_time"] = int(time.time())
            self.json_save()
            return io.BytesIO(file_path.read_bytes())
        else:
            return io.BytesIO()

    def auto_clean_temp(self):
        for temp_id in self.temp_data_json["image"]:
            if int(time.time()) - self.temp_data_json["image"][temp_id]["last_time"] >= 259200:
                self.delete_temp_image(temp_id)

    def json_save(self):
        with TEMP_DATA_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.temp_data_json, indent=4, ensure_ascii=False))
