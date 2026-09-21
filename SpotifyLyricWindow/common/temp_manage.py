#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import json
import threading
import time
import weakref
from functools import wraps
from common.path import TEMP_DATA_FILE_PATH, TEMP_IMAGE_PATH


def temp_file_locked(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return func(self, *args, **kwargs)
    return wrapper


class TempFileManage:
    """临时文件管理类（单例）"""
    _instance = None
    _is_init = False
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            instance = cls._instance() if cls._instance else None
            if instance is None:
                instance = super(TempFileManage, cls).__new__(cls, *args, **kwargs)
                cls._instance = weakref.ref(instance)
            return instance

    @temp_file_locked
    def __init__(self):
        if not self._is_init:
            with TEMP_DATA_FILE_PATH.open(encoding="utf-8") as f:
                self.temp_data_json = json.load(f)
            keys = ["image", "musicbrainz"]

            for base_key in keys:
                if base_key not in self.temp_data_json:
                    self.temp_data_json[base_key] = {}

            self._is_init = True

    @temp_file_locked
    def delete_temp_image(self, track_id):
        """删除对应的缓存图片"""
        file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
        if file_path.exists():
            file_path.unlink()
        self.temp_data_json["image"].pop(track_id)

    @temp_file_locked
    def save_temp_image(self, track_id, img_io: io.BytesIO):
        """将下载到的图片载入临时文件文件夹"""
        if not img_io:
            return
        self.temp_data_json["image"][track_id] = {"last_time": int(time.time())}
        self.json_save()
        file_path = TEMP_IMAGE_PATH / (track_id + ".jpg")
        file_path.write_bytes(img_io.getvalue())

    @temp_file_locked
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

    @temp_file_locked
    def get_musicbrainz_cache(self, key: str):
        """返回有效的元数据缓存；None 表示未缓存，False 表示已查询但未匹配。"""
        data = self.temp_data_json['musicbrainz'].get(key)
        if data and data['expires'] > time.time():
            return data['data']
        return None

    @temp_file_locked
    def save_musicbrainz_cache(self, key: str, data, expire_seconds: int = 2592000):
        """保存已确认的元数据，默认有效期30天，不保存网络错误。"""
        self.temp_data_json['musicbrainz'][key] = {'expires': int(time.time()) + expire_seconds, 'data': data}
        self.json_save()

    @temp_file_locked
    def auto_clean_temp(self):
        """自动清理临时文件，最近一次使用距今3天将被清除"""
        for temp_id in list(self.temp_data_json["image"].keys()):
            if int(time.time()) - self.temp_data_json["image"][temp_id]["last_time"] >= 259200:
                self.delete_temp_image(temp_id)
        for key, data in list(self.temp_data_json['musicbrainz'].items()):
            if data['expires'] <= time.time():
                self.temp_data_json['musicbrainz'].pop(key)
        self.json_save()

    @temp_file_locked
    def clean_all_temp(self):
        """清理掉所有的临时图片和元数据缓存"""
        for temp_id in list(self.temp_data_json["image"].keys()):
            self.delete_temp_image(temp_id)
        self.temp_data_json['musicbrainz'].clear()
        self.json_save()

    @temp_file_locked
    def json_save(self):
        with TEMP_DATA_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.temp_data_json, indent=4, ensure_ascii=False))
