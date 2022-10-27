# coding : utf-8
import json
import threading
import time
import ctypes
import inspect
from pathlib import Path

from common.lyric_type.lyric_decode import LrcFile, MrcFile, TransType
from common.api import SpotifyUserApi


class NotLyricFound(Exception):
    """歌词文件不存在，需要下载"""


class LrcPlayer:
    LRC_PATH = Path("download\\lyrics")
    offset_file_path = LRC_PATH / "offset.json"

    def __init__(self, lyrics_window=None):
        self.lyrics_window = lyrics_window
        self.track_id = None
        self.timer_value = int(time.time() * 1000)
        self.lrc_file = LrcFile()

        self.no_lyric = True

        self.offset = 0
        self.duration = 0

        self.trans_mode = TransType.NON
        self.is_pause = False

        self.thread_play_lrc = threading.Thread(target=self.__play_lrc_thread)

    def _set_offset_file(self, track_id, offset):
        with self.offset_file_path.open(encoding="utf-8") as f:
            data_json = json.load(f)
        data_json[track_id] = offset
        with self.offset_file_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(data_json, indent=4, ensure_ascii=False))

    def _get_offset_file(self, track_id):
        if not self.offset_file_path.exists():
            self.LRC_PATH.mkdir(parents=True)
            with self.offset_file_path.open("w", encoding="utf-8") as f:
                f.write(json.dumps({}, indent=4, ensure_ascii=False))
        with self.offset_file_path.open(encoding="utf-8") as f:
            data_json = json.load(f)
        return data_json.get(track_id, 0)

    def set_track(self, track_id, duration, *, no_lyric=False) -> None:
        if self.track_id and self.offset:
            self._set_offset_file(self.track_id, self.offset)

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

    def _reload_lrc_data(self) -> None:
        """
        Make the in-class data correspond to the lyrics file data.
        :return: None
        """
        if self.no_lyric:
            return
        lrc_path = self.LRC_PATH / (self.track_id + '.mrc')
        if lrc_path.exists():
            self.lrc_file = MrcFile(lrc_path)
        else:
            raise NotLyricFound("未找到歌词文件")

    def is_lyric_exist(self, track_id) -> bool:
        lrc_path = self.LRC_PATH / (track_id + '.mrc')
        return lrc_path.exists()

    def restart_thread(self, position=0, *, timestamp=0) -> None:
        """
        Restart the thread that outputs the lyrics
        :return: None
        """
        # self._reload_lrc_data()
        if self.thread_play_lrc.is_alive():
            stop_thread(self.thread_play_lrc)
        if position:
            self.thread_play_lrc = threading.Thread(target=self.__play_lrc_thread, args=(position,))
        else:
            self.thread_play_lrc = threading.Thread(target=self.__play_lrc_thread)
        if timestamp:
            # 自动切歌的时候 progress_ms 不准确，timestamp准确
            self.timer_value = timestamp
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

    def __play_lrc_thread(self, position=None) -> None:
        time.sleep(0.1)
        if position:
            position = position
        else:
            position = self.get_time()

        if not self.no_lyric:
            self.order = self.lrc_file.get_order_position(position)
            if self.order == -1:
                return
            if self.order == 0:
                self.__show_content(self.lrc_file.get_time(1) - self.get_time())
                self.order += 1  # 第一句的时间需要被忽略
            else:
                time_stamp = self.lrc_file.get_time(self.order + 1)
                if time_stamp == -2:
                    self.__show_content(0)
                self.__show_content(time_stamp - self.get_time())

            while True:
                sleep_time = self.lrc_file.get_time(self.order + 1) - self.get_time()
                if sleep_time > 100:
                    time.sleep(sleep_time / 1000)

                if self.is_pause:
                    while self.is_pause:  # 当被暂停，让线程停滞
                        time.sleep(0.1)
                    continue  # todo 小bug 如果暂停和开始都存在于time.sleep时间 只会影响到下一句
                elif self.lrc_file.get_time(self.order) - self.get_time() > 0 and self.order > 2:
                    # 分别排除了self.order被作为下标为负数的情况 和 歌词文件时间标注重复问题
                    print("時間異常")
                    time.sleep(0.1)
                    self.__play_lrc_thread()
                    return
                self.order += 1

                time_stamp = self.lrc_file.get_time(self.order + 1)
                if time_stamp == -2:
                    self.__show_content(0)
                    break
                else:
                    roll_time = self.lrc_file.get_time(self.order + 1) - self.get_time()
                    self.__show_content(roll_time)

        while True:
            time.sleep(1)
            if self.get_time() - self.offset > self.duration and self.duration:

                while self.is_pause:
                    time.sleep(0.3)

                time.sleep(0.6)
                print(self.duration, self.get_time())
                self.lyrics_window.song_done_calibration_signal.emit("")

                # 依据 timestamp 为准
                return

    def __show_content(self, roll_time: int) -> None:
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
            self.lyrics_window.set_text(1, self.lrc_file.trans_non_dict[time_stamp], roll_time)
            if self.trans_mode == TransType.CHINESE:
                self.lyrics_window.set_text(2, self.lrc_file.trans_chinese_dict[time_stamp], roll_time)
            elif self.trans_mode == TransType.ROMAJI:
                self.lyrics_window.set_text(2, self.lrc_file.trans_romaji_dict[time_stamp], roll_time)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


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

