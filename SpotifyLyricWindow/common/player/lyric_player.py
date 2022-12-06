#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import threading
import time
import weakref

from common.api import SpotifyUserApi
from common.lyric.lyric_type import LrcFile, TransType
from common.win_utils.get_windows_title import get_spotify_pid, get_pid_title
from common.lyric import LyricFileManage


class LrcPlayer:
    def __init__(self, lyrics_window=None):
        self.lyrics_window = lyrics_window
        self.track_id = None
        self.timer_value = int(time.time() * 1000)

        self.lrc_file = LrcFile()
        self.lyric_file_manage = LyricFileManage()

        self.no_lyric = True

        self.order = 0
        self.offset = 0
        self.duration = 0
        self.api_offset = self.lyric_file_manage.get_offset_file("api_offset")

        self.trans_mode = TransType.NON
        self.is_pause = False

        self.thread_play_lrc = LyricThread(self)
        self.thread_check_title = WindowsSpotifyTitleThread(self)

        self.title_changed_timestamp = 0

        self.is_ad = False

    def _reload_lrc_data(self):
        """Make the in-class data correspond to the lyrics file data."""
        if self.no_lyric:
            return
        self.lrc_file = self.lyric_file_manage.read_lyric_file(self.track_id)

    def set_track(self, track_id: str, duration: int, *, no_lyric=False):
        """change the current lrc. the duration is used to auto next song"""
        if self.track_id and self.offset:
            self.lyric_file_manage.set_offset_file(self.track_id, self.offset)
        if self.api_offset:
            self.lyric_file_manage.set_offset_file("api_offset", self.api_offset)

        self.track_id = track_id
        self.offset = self.lyric_file_manage.get_offset_file(track_id)
        self.no_lyric = no_lyric
        self.duration = duration

        self.timer_value = int(time.time() * 1000)
        if not no_lyric:
            self._reload_lrc_data()
        else:
            self.lrc_file = LrcFile()

    def set_trans_mode(self, mode: TransType) -> bool:
        """set the translation mode of player and refresh the displayed content"""
        if self.no_lyric:
            return False
        if mode == TransType.ROMAJI and len(self.lrc_file.trans_romaji_dict) == 0:
            return False
        if mode == TransType.CHINESE and len(self.lrc_file.trans_chinese_dict) == 0:
            return False
        if mode == TransType.NON:
            self.lyrics_window.set_lyrics_text(2, "")
        else:
            time_stamp = self.lrc_file.get_time(self.order)
            if time_stamp == -2:
                # todo
                print("TODO TODO")
            elif mode == TransType.ROMAJI:
                self.lyrics_window.set_lyrics_text(2, self.lrc_file.trans_romaji_dict[time_stamp])
                self.lyrics_window.set_lyrics_text(1, self.lrc_file.trans_non_dict[time_stamp])
            elif mode == TransType.CHINESE:
                self.lyrics_window.set_lyrics_text(2, self.lrc_file.trans_chinese_dict[time_stamp])
                self.lyrics_window.set_lyrics_text(1, self.lrc_file.trans_non_dict[time_stamp])
        self.trans_mode = mode

        # self.restart_thread()
        return True

    def start_check(self, *, times=40):
        self.thread_check_title.terminate()

        self.title_changed_timestamp = 0
        self.thread_check_title = WindowsSpotifyTitleThread(self)

        self.thread_check_title.set_times(times)
        self.thread_check_title.start()

    def get_time(self) -> int:
        return int(time.time() * 1000) - self.timer_value + self.offset

    def modify_offset(self, modify_value: int):
        self.offset += modify_value

    def modify_api_offset(self, modify_value: int):
        """the 'progress_ms' of web api is inaccurate. use api_offset to make up for it"""
        self.api_offset += modify_value

    def restart_thread(self, position=0, *, api_offset=0, is_ad=False):
        """Restart the thread that outputs the lyrics"""
        # self._reload_lrc_data()
        self.is_ad = is_ad

        if self.thread_play_lrc.is_alive():
            self.thread_play_lrc.terminate()
            self.thread_play_lrc.join()

        self.thread_play_lrc = LyricThread(self)
        if position:
            self.thread_play_lrc.set_position(position)

        if api_offset:
            # 自动切歌的时候 progress_ms 不准确，timestamp准确
            saved_api_offset = self.lyric_file_manage.get_offset_file("api_offset")
            if self.title_changed_timestamp:
                self.timer_value = self.title_changed_timestamp
                self.title_changed_timestamp = 0
                self.thread_play_lrc.start()
                return
            if saved_api_offset:
                self.timer_value = int(time.time() * 1000) - position - saved_api_offset
            else:
                self.timer_value = int(time.time() * 1000) - position - api_offset * 2
        else:
            self.timer_value = int(time.time() * 1000) - position
        self.thread_play_lrc.start()

    def show_content(self, roll_time: int):
        """output function, use 'print' to debug"""
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

    def __init__(self, player: LrcPlayer):
        super(LyricThread, self).__init__(target=self.__play_lrc_thread)
        self.stop = threading.Event()
        self.player_ = weakref.ref(player)
        self.position = 0
        self.is_running = True

    @property
    def player(self):
        return self.player_()

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

        is_title_thread = False
        if self.player.is_ad and not self.player.title_changed_timestamp:
            self.player.start_check(times=80)
            is_title_thread = True

        while self.is_running:
            self.stop.wait(1)
            if self.player.get_time() - self.player.offset > self.player.duration - 3000 and self.player.duration and \
                    not is_title_thread:
                self.player.start_check()
                is_title_thread = True

            if self.player.get_time() - self.player.offset > self.player.duration and self.player.duration:

                while self.player.is_pause and self.is_running:
                    self.stop.wait(0.3)

                self.stop.wait(0.6)
                self.player.lyrics_window.song_done_calibration_signal.emit("")
                # 依据 timestamp 为准
                return

    def terminate(self):
        self.is_running = False
        self.stop.set()


class WindowsSpotifyTitleThread(threading.Thread):
    def __init__(self, player: LrcPlayer):
        super(WindowsSpotifyTitleThread, self).__init__(target=self.check_title_changed_func)
        self.player_ = weakref.ref(player)
        self.stop = threading.Event()
        self.is_running = True
        self.max_times = 40

    @property
    def player(self):
        return self.player_()

    def set_times(self, times):
        self.max_times = times

    def check_title_changed_func(self):
        times = 0
        spotify_pid = get_spotify_pid()
        ori_title = get_pid_title(spotify_pid)
        if not ori_title:
            return
        while self.is_running:
            self.stop.wait(0.2)
            title = get_pid_title(spotify_pid)
            if title != ori_title:
                self.player.title_changed_timestamp = int(time.time() * 1000) + 800
                return
            if times == 40:
                self.player.title_changed_timestamp = 0
                return
            times += 1

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

