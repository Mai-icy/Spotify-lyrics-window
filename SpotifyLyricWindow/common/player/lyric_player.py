#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import threading
import time
import weakref

from enum import Enum
from common.typing import LrcFile, TransType, MrcFile


class PlayerState(Enum):
    StoppedState = 0
    PlayingState = 1
    PausedState = 2


class LrcPlayer:
    def __init__(self, output_func=None):
        self._output_func = output_func

        self._lyric = LrcFile()
        self._duration = float("INF")
        self._state = PlayerState.StoppedState

        self._timer_start_value: int = int(time.time() * 1000)  # 计时器实现原理，当前时间减去开始时间

        self._lyric_offset = 0
        self._global_offset = 0
        self.trans_mode = TransType.NON

        self.play_done_event_func = None

        self.thread_play_lrc = LyricThread(self)
        self.thread_play_lrc.start()

    def current_lyric(self) -> LrcFile:
        return self._lyric

    @property
    def duration(self):
        return self._duration

    @property
    def state(self):
        return self._state

    @property
    def position(self):
        return int(time.time() * 1000) - self._timer_start_value + self._lyric_offset + self._global_offset

    @property
    def lyric_offset(self):
        return self._lyric_offset

    @property
    def global_offset(self):
        return self._global_offset

    def set_trans_mode(self, mode: TransType):
        self.trans_mode = mode
        self._show_last_lyric()

    def set_position(self, position: int, *, is_show_last_lyric=True):
        self._timer_start_value = int(time.time() * 1000) - position

        if is_show_last_lyric:
            self._show_last_lyric()

        self.thread_play_lrc.reset_position()

    def set_lyric(self, lrc: LrcFile, duration: int):
        self._lyric_offset = 0
        self._state = PlayerState.StoppedState
        self._lyric = lrc
        self._duration = duration
        # self._timer_start_value = int(time.time() * 1000)
        self.thread_play_lrc.reset_position()

    def set_offset(self, offset: int):
        self._lyric_offset = offset

    def set_global_offset(self, offset: int):
        self._global_offset = offset

    def pause(self):
        self._state = PlayerState.PausedState

    def play(self):
        self._state = PlayerState.PlayingState

    def stop(self):
        self._state = PlayerState.StoppedState

    def close(self):
        self.thread_play_lrc.terminate()

    def _show_last_lyric(self):
        """显示上一句非空白的歌词"""
        lrc_file = self.current_lyric()
        if lrc_file.empty():
            return
        order = lrc_file.get_order_position(self.position)
        timestamp = lrc_file.get_time(order)
        lyric_text = lrc_file.trans_non_dict[timestamp]
        while order != -1 and not lyric_text:
            order -= 1
            timestamp = lrc_file.get_time(order)
            lyric_text = lrc_file.trans_non_dict.get(timestamp)
        if order != -1:
            self.output_event(order, 0)

    def output_event(self, lyric_order, roll_time):
        """输出歌词"""
        print("output")
        lrc_file = self.current_lyric()
        time_stamp = lrc_file.get_time(lyric_order)

        if time_stamp == -1 or not lrc_file.trans_non_dict[time_stamp].strip():
            return

        output_func = self._output_func
        if output_func:  # self.lyrics_window.text_show_signal.emit
            output_func(1, lrc_file.trans_non_dict[time_stamp], roll_time)
            if lrc_file.empty(self.trans_mode) or self.trans_mode == TransType.NON:
                output_func(2, "", 0)
            elif self.trans_mode == TransType.CHINESE:
                output_func(2, lrc_file.trans_chinese_dict[time_stamp], roll_time)
            elif self.trans_mode == TransType.ROMAJI:
                output_func(2, lrc_file.trans_romaji_dict[time_stamp], roll_time)

    def play_done_event_connect(self, func):
        """播放完毕的信号连接"""
        self.play_done_event_func = func


class LyricThread(threading.Thread):
    def __init__(self, player: LrcPlayer):
        super(LyricThread, self).__init__(target=self._play_lyric_thread)
        self.sleep = threading.Event()
        self.sleep.is_set()

        self.player_ = weakref.ref(player)
        self.is_running = True

    def reset_position(self):
        self.sleep.set()

    def _play_lyric_thread(self):
        while self.is_running:
            if self.sleep.is_set() and self.is_running:
                self.sleep.clear()

            position = self.player.position
            lrc_file = self.player.current_lyric()

            lyric_order = lrc_file.get_order_position(position)
            next_stamp = lrc_file.get_time(lyric_order + 1)

            if position > self.player.duration - 1000:  # 播放完毕
                if self.player.state == PlayerState.PlayingState:
                    self.player.stop()
                    if self.player.play_done_event_func:
                        self.player.play_done_event_func()  # 发送播放完毕信号
                self.sleep.wait()
                continue

            if next_stamp < 0 or lyric_order < 0:  # 无歌词
                self.sleep.wait(0.1)  # 开始检测何时播放完毕
                continue

            show_time = next_stamp - position

            if show_time < 0:  # 位置判断变化导致时间错误 重新获取
                continue
            self.player.output_event(lyric_order, show_time)
            self.sleep.wait(show_time / 1000)

            if self.player.state != PlayerState.PlayingState and self.is_running:
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
    player = LrcPlayer(print)

    lrc_ = MrcFile(f"../../download/lyrics/0loZ1KfQSLJxYR0Y7dImKN.mrc")

    player.set_lyric(lrc_, 9999999)
    player.play()
