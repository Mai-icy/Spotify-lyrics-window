#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import json
import time
import weakref
from common.path import TEMP_DATA_FILE_PATH, TEMP_IMAGE_PATH


class TempFileManage:
    """临时文件管理类（单例）"""
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
        """删除对应的缓存图片"""
        file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
        if file_path.exists():
            file_path.unlink()
        self.temp_data_json["image"].pop(track_id)

    def save_temp_image(self, track_id, img_io: io.BytesIO):
        """将下载到的图片载入临时文件文件夹"""
        if not img_io:
            return
        self.temp_data_json["image"][track_id] = {"last_time": int(time.time())}
        self.json_save()
        file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
        file_path.write_bytes(img_io.getvalue())

    def get_temp_image(self, track_id) -> io.BytesIO:
        """获取临时缓存的图片，若不存在，则返回空io对象"""
        if track_id in self.temp_data_json["image"]:
            file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
            if not file_path.exists():
                self.delete_temp_image(track_id)
                return io.BytesIO()
            self.temp_data_json["image"][track_id]["last_time"] = int(time.time())
            self.json_save()
            return io.BytesIO(file_path.read_bytes())
        else:
            return io.BytesIO()

    def auto_clean_temp(self):
        """自动清理临时文件，最近一次使用距今3天将被清除"""
        for temp_id in list(self.temp_data_json["image"].keys()):
            if int(time.time()) - self.temp_data_json["image"][temp_id]["last_time"] >= 259200:
                self.delete_temp_image(temp_id)

    def clean_all_temp(self):
        """清理掉所有的临时图片"""
        for temp_id in list(self.temp_data_json["image"].keys()):
            self.delete_temp_image(temp_id)

    def json_save(self):
        with TEMP_DATA_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.temp_data_json, indent=4, ensure_ascii=False))
