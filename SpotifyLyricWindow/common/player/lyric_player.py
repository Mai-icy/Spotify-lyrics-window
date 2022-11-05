#!/usr/bin/python
# -*- coding:utf-8 -*-
import ctypes
import inspect
import json
import threading
import time

from common.api import SpotifyUserApi
from common.lyric_type.lyric_decode import LrcFile, MrcFile, TransType
from common.path import LRC_PATH, OFFSET_FILE_PATH


class NotLyricFound(Exception):
    """歌词文件不存在，需要下载"""


class LrcPlayer:
    def __init__(self, lyrics_window=None):
        self.lyrics_window = lyrics_window
        self.track_id = None
        self.timer_value = int(time.time() * 1000)
        self.lrc_file = LrcFile()

        self.no_lyric = True

        self.order = 0
        self.offset = 0
        self.duration = 0
        self.api_offset = self._get_offset_file("api_offset")

        self.trans_mode = TransType.NON
        self.is_pause = False

        self.thread_play_lrc = LyricThread(self)

    @staticmethod
    def _set_offset_file(track_id, offset):
        with OFFSET_FILE_PATH.open(encoding="utf-8") as f:
            data_json = json.load(f)
        data_json[track_id] = offset
        with OFFSET_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(data_json, indent=4, ensure_ascii=False))

    @staticmethod
    def _get_offset_file(track_id):
        with OFFSET_FILE_PATH.open(encoding="utf-8") as f:
            data_json = json.load(f)
        return data_json.get(track_id, 0)

    def set_track(self, track_id, duration, *, no_lyric=False):
        """change the current lrc. the duration is used to auto next song"""
        if self.track_id and self.offset:
            self._set_offset_file(self.track_id, self.offset)
        if self.api_offset:
            self._set_offset_file("api_offset", self.api_offset)

        self.track_id = track_id
        self.offset = self._get_offset_file(track_id)
        self.no_lyric = no_lyric
        self.duration = duration

        self.timer_value = int(time.time() * 1000)
        if not no_lyric:
            self._reload_lrc_data()
        else:
            self.lrc_file = LrcFile()

    def get_time(self) -> int:
        return int(time.time() * 1000) - self.timer_value + self.offset

    def modify_offset(self, modify_value):
        self.offset += modify_value

    def modify_api_offset(self, modify_value):
        """the 'progress_ms' of web api is inaccurate. use api_offset to make up for it"""
        self.api_offset += modify_value

    def _reload_lrc_data(self) -> None:
        """
        Make the in-class data correspond to the lyrics file data.
        :return: None
        """
        if self.no_lyric:
            return
        lrc_path = LRC_PATH / (self.track_id + '.mrc')
        if lrc_path.exists():
            self.lrc_file = MrcFile(lrc_path)
        else:
            raise NotLyricFound("未找到歌词文件")

    @staticmethod
    def is_lyric_exist(track_id: str) -> bool:
        lrc_path = LRC_PATH / (track_id + '.mrc')
        return lrc_path.exists()

    def restart_thread(self, position=0, *, api_offset=0) -> None:
        """
        Restart the thread that outputs the lyrics
        :return: None
        """
        # self._reload_lrc_data()
        if self.thread_play_lrc.is_alive():
            self.thread_play_lrc.terminate()
            self.thread_play_lrc.join()

        self.thread_play_lrc = LyricThread(self)
        if position:
            self.thread_play_lrc.set_position(position)

        if api_offset:
            # 自动切歌的时候 progress_ms 不准确，timestamp准确
            saved_api_offset = self._get_offset_file("api_offset")
            if saved_api_offset:
                self.timer_value = int(time.time() * 1000) - position - saved_api_offset
            else:
                self.timer_value = int(time.time() * 1000) - position - api_offset * 2
        else:
            self.timer_value = int(time.time() * 1000) - position
        self.thread_play_lrc.start()

    def set_trans_mode(self, mode: TransType) -> bool:
        if self.no_lyric:
            return False
        if mode == TransType.ROMAJI and len(self.lrc_file.trans_romaji_dict) == 0:
            return False
        if mode == TransType.CHINESE and len(self.lrc_file.trans_chinese_dict) == 0:
            return False
        if mode == TransType.NON:
            self.lyrics_window.set_text(2, "", 0)
        else:
            time_stamp = self.lrc_file.get_time(self.order)
            if time_stamp == -2:
                # todo
                print("TODO TODO")
            elif mode == TransType.ROMAJI:
                self.lyrics_window.set_text(2, self.lrc_file.trans_romaji_dict[time_stamp], 0)
                self.lyrics_window.set_text(1, self.lrc_file.trans_non_dict[time_stamp], 0)
            elif mode == TransType.CHINESE:
                self.lyrics_window.set_text(2, self.lrc_file.trans_chinese_dict[time_stamp], 0)
                self.lyrics_window.set_text(1, self.lrc_file.trans_non_dict[time_stamp], 0)
        self.trans_mode = mode

        # self.restart_thread()
        return True

    def show_content(self, roll_time: int) -> None:
        """
        output function, use 'print' to debug
        """
        order = self.order
        time_stamp = self.lrc_file.get_time(order)
        if time_stamp == -2:
            return
        # print(time_stamp)
        # print(self.lrc_file.trans_non_dict[time_stamp])

        if not self.lrc_file.trans_non_dict[time_stamp]:
            return

        # if self.trans_mode == TransType.CHINESE:
        #     print(self.lrc_file.trans_chinese_dict[time_stamp])
        # elif self.trans_mode == TransType.ROMAJI:
        #     print(self.lrc_file.trans_romaji_dict[time_stamp])

        if self.lyrics_window:
            self.lyrics_window.text_show_signal.emit(1, self.lrc_file.trans_non_dict[time_stamp], roll_time)
            if self.trans_mode == TransType.CHINESE:
                self.lyrics_window.text_show_signal.emit(2, self.lrc_file.trans_chinese_dict[time_stamp], roll_time)
            elif self.trans_mode == TransType.ROMAJI:
                self.lyrics_window.text_show_signal.emit(2, self.lrc_file.trans_romaji_dict[time_stamp], roll_time)


class LyricThread(threading.Thread):

    def __init__(self, player):
        super(LyricThread, self).__init__(target=self.__play_lrc_thread)
        self.stop = threading.Event()
        self.player = player
        self.position = 0
        self.is_running = True

    def set_position(self, position):
        self.position = position

    def __play_lrc_thread(self) -> None:
        if not self.is_running:
            return

        self.stop.wait(0.1)
        if self.position:
            position = self.position
        else:
            position = self.player.get_time()

        if not self.player.no_lyric:
            self.player.order = self.player.lrc_file.get_order_position(position)
            if self.player.order == -1:
                return
            if self.player.order == 0:
                self.player.show_content(self.player.lrc_file.get_time(1) - self.player.get_time())
                self.player.order += 1  # 第一句的时间需要被忽略
            else:
                time_stamp = self.player.lrc_file.get_time(self.player.order + 1)
                if time_stamp == -2:
                    self.player.show_content(0)
                self.player.show_content(time_stamp - self.player.get_time())

            while self.is_running:
                sleep_time = self.player.lrc_file.get_time(self.player.order + 1) - self.player.get_time()
                if sleep_time > 100:
                    self.stop.wait(sleep_time / 1000)

                if self.player.is_pause and self.is_running:
                    while self.player.is_pause and self.is_running:  # 当被暂停，让线程停滞
                        self.stop.wait(0.1)
                    continue  # todo 小bug 如果暂停和开始都存在于self.stop.wait时间 只会影响到下一句
                elif self.player.lrc_file.get_time(self.player.order) - self.player.get_time() > 0 and \
                        self.player.order > 2:
                    # 分别排除了self.order被作为下标为负数的情况 和 歌词文件时间标注重复问题
                    # print("時間異常")
                    self.stop.wait(0.1)
                    self.__play_lrc_thread()
                    return
                self.player.order += 1

                if not self.is_running:
                    return
                time_stamp = self.player.lrc_file.get_time(self.player.order + 1)
                if time_stamp == -2:
                    self.player.show_content(0)
                    break
                else:
                    roll_time = self.player.lrc_file.get_time(self.player.order + 1) - self.player.get_time()
                    self.player.show_content(roll_time)

        while self.is_running:
            self.stop.wait(1)
            if self.player.get_time() - self.player.offset > self.player.duration and self.player.duration:

                while self.player.is_pause and self.is_running:
                    self.stop.wait(0.3)

                self.stop.wait(0.6)
                print(self.player.duration, self.player.get_time())
                self.player.lyrics_window.song_done_calibration_signal.emit("")
                # 依据 timestamp 为准
                return

    def terminate(self):
        self.is_running = False
        self.stop.set()


if __name__ == '__main__':
    # LRC_PATH = '..\\..\\resource\\Lyric\\'
    # print(find_lrc_path('bc37903410ef6f94014563c51da60743'))
    auth = SpotifyUserApi()
    pos, track_id_ = auth.get_current_playing()
    lrc = LrcPlayer(track_id_)
    lrc.trans_mode = 1

    lrc.restart_thread(pos)
    while True:
        time.sleep(1)
        print(lrc.get_time())

