#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import threading
import time
import weakref

from common.api import SpotifyUserApi
from common.lyric import LyricFileManage
from common.lyric.lyric_type import LrcFile, TransType


class LrcPlayer:
    def __init__(self, output_func):
        self.output_func = output_func
        self.lyric_file_manage = LyricFileManage()
        self.timer_start_value: int = int(time.time() * 1000)

        self.track_id = ""
        self.duration = float('inf')
        self.is_pause = False
        self.trans_mode = TransType.NON

        self.track_offset = 0
        self.global_offset = 0
        self.lrc_file = LrcFile()

        self.play_done_event_func = None

        self.thread_play_lrc = LyricThread(self)
        self.thread_play_lrc.start()

    def get_time(self) -> int:
        return int(time.time() * 1000) - self.timer_start_value + self.track_offset + self.global_offset

    def set_pause(self, flag: bool):
        self.is_pause = flag

    def set_track(self, track_id: str, duration: int):
        if self.track_id and self.track_offset:
            self.lyric_file_manage.set_offset_file(self.track_id, self.track_offset)
            self.lyric_file_manage.set_offset_file("api_offset", self.global_offset)

        self.track_id = track_id
        self.duration = duration
        self.lrc_file = self.lyric_file_manage.read_lyric_file(track_id)

    def set_trans_mode(self, mode: TransType) -> bool:
        """set the translation mode of player and refresh the displayed content"""
        if self.lrc_file.empty(mode):
            return False
        self.trans_mode = mode
        self._show_last_lyric()
        return True

    def _show_last_lyric(self):
        lrc_file = self.lrc_file
        if lrc_file.empty():
            return
        order = lrc_file.get_order_position(self.get_time())
        timestamp = lrc_file.get_time(order)
        lyric_text = lrc_file.trans_non_dict[timestamp]
        while order != -1 and not lyric_text:
            order -= 1
            timestamp = lrc_file.get_time(order)
            lyric_text = lrc_file.trans_non_dict.get(timestamp)
        if order != -1:
            self.show_content(order, 0)

    def seek_to_position(self, position):
        self.timer_start_value = int(time.time() * 1000) - position
        self._show_last_lyric()
        self.thread_play_lrc.reset_position()

    def modify_offset(self, modify_value: int):
        self.track_offset += modify_value

    def modify_global_offset(self, modify_value: int):
        self.global_offset += modify_value

    def show_content(self, lyric_order, roll_time: int):
        lrc_file = self.lrc_file
        time_stamp = lrc_file.get_time(lyric_order)

        if time_stamp == -1 or not lrc_file.trans_non_dict[time_stamp].strip():
            return

        if self.output_func:  # self.lyrics_window.text_show_signal.emit
            self.output_func(1, lrc_file.trans_non_dict[time_stamp], roll_time)
            if lrc_file.empty(self.trans_mode) or self.trans_mode == TransType.NON:
                self.output_func(2, "")
            elif self.trans_mode == TransType.CHINESE:
                self.output_func(2, lrc_file.trans_chinese_dict[time_stamp], roll_time)
            elif self.trans_mode == TransType.ROMAJI:
                self.output_func(2, lrc_file.trans_romaji_dict[time_stamp], roll_time)

    def play_done_event_connect(self, func):
        self.play_done_event_func = func


class LyricThread(threading.Thread):
    def __init__(self, player: LrcPlayer):
        super(LyricThread, self).__init__(target=self._play_lyric_thread)
        self.sleep = threading.Event()

        self.player_ = weakref.ref(player)
        self.is_running = True

    def reset_position(self):
        self.sleep.set()

    def _play_lyric_thread(self):
        while self.is_running:
            if self.sleep.isSet() and self.is_running:
                self.sleep.clear()
            position = self.player.get_time()
            lyric_order = self.player.lrc_file.get_order_position(position)
            next_stamp = self.player.lrc_file.get_time(lyric_order + 1)

            if position > self.player.duration - 1000:  # 播放完毕
                if self.player.play_done_event_func and not self.player.is_pause:
                    self.player.play_done_event_func()  # 发送播放完毕信号
                self.sleep.wait()
                continue
            if next_stamp < 0 or lyric_order < 0:  # 无歌词
                self.sleep.wait(0.1)  # 开始检测何时播放完毕
                continue

            show_time = next_stamp - position

            if show_time < 0:  # 位置判断变化导致时间错误 重新获取
                continue
            self.player.show_content(lyric_order, show_time)
            self.sleep.wait(show_time / 1000)

            if self.player.is_pause and self.is_running:
                self.sleep.wait()
                continue

    def terminate(self):
        self.is_running = False
        self.sleep.set()

    @property
    def player(self):
        if not self.player_():
            self.terminate()
            sys.exit(0)
        else:
            return self.player_()


if __name__ == '__main__':

    auth = SpotifyUserApi()
    user_current_playing = auth.get_current_playing()
    lrc = LrcPlayer(print)
    lrc.set_track(user_current_playing.track_id, user_current_playing.duration)
    lrc.seek_to_position(user_current_playing.progress_ms)

    while True:
        time.sleep(1)
        print(lrc.get_time())
