#!/usr/bin/python
# -*- coding:utf-8 -*-
import time

import requests

from components.lyric_window_view import LyricsWindowView

import sys
from functools import wraps
from types import MethodType
import webbrowser

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from components.work_thread import thread_drive
from components.setting_window.setting_window import SettingWindow

from common.config import Config
from common.api.user_api import SpotifyUserApi, UserCurrentPlaying
from common.api.api_error import UserError, NoPermission
from common.player.lyric_player import LrcPlayer, TransType
from common.download_lrc import download_lrc


class CatchError:
    def __init__(self, func):
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        try:
            return self.__wrapped__(*args, **kwargs)
        except UserError as e:
            args[0].error_msg_show_signal.emit(e)
        except requests.RequestException as e:
            new_err = Exception("Requests Error")
            args[0].error_msg_show_signal.emit(new_err)
        except Exception as e:
            raise e

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return MethodType(self, instance)


class LyricsWindow(LyricsWindowView):
    error_msg_show_signal = pyqtSignal(object)
    song_done_calibration_signal = pyqtSignal(object)
    text_show_signal = pyqtSignal(int, str, int)

    def __init__(self, parent=None):
        super(LyricsWindow, self).__init__(parent)
        self.lrc_player = LrcPlayer(self)

        self._init_common()
        self._init_signal()

        self.calibration_event()

    def _init_signal(self):
        """初始化信号"""
        super(LyricsWindow, self)._init_signal()
        
        self.account_button.clicked.connect(self.user_auth_button_event)
        self.calibrate_button.clicked.connect(self.calibration_event)
        self.next_button.clicked.connect(self.set_user_next_event)
        self.last_button.clicked.connect(self.set_user_previous_event)
        self.pause_button.clicked.connect(self.pause_resume_button_event)
        self.offsetup_button.clicked.connect(lambda: self.lrc_player.modify_offset(500))
        self.offsetdown_button.clicked.connect(lambda: self.lrc_player.modify_offset(-500))
        self.translate_button.clicked.connect(self.change_trans_button_event)
        self.settings_button.clicked.connect(self.setting_open_event)
        self.setting_window.close_signal.connect(self.setting_close_event)

        self.text_show_signal.connect(lambda row, text, roll_time: self.set_lyrics_text(row, text, roll_time=roll_time))

        self.error_msg_show_signal.connect(self._error_msg_show_event)
        self.song_done_calibration_signal.connect(lambda: self.calibration_event(use_api_offset=True))

    def _init_common(self):
        """初始化其他辅助部件"""
        self.user_trans = TransType(Config.LyricConfig.trans_type)

        self.spotify_auth = SpotifyUserApi()
        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)

        self.setting_window = SettingWindow()

    @thread_drive()
    @CatchError
    def calibration_event(self, *_, use_api_offset: bool = False, no_text_show: bool = False):
        """
        同步歌词

        :param use_api_offset: 是否使用播放偏移
        :param no_text_show: 是否显示 calibrating！ 的 正在校准提示
        """
        self.lrc_player.is_pause = True
        if not no_text_show:
            self.set_lyrics_text(1, "calibrating！")
            self.set_lyrics_text(2, " (o゜▽゜)o!")
        user_current = self.spotify_auth.get_current_playing()

        self.set_pause_button_icon(user_current.is_playing)
        self.set_lyrics_rolling(user_current.is_playing)

        if user_current.track_name == "ad":
            self.set_lyrics_text(1, "Advertising！")
            self.set_lyrics_text(2, "o(_ _)ozzZZ")
            self.lrc_player.is_pause = False
            self._refresh_player_track(user_current, no_lyric=True)
            self.lrc_player.restart_thread(0)
            return

        if not self.lrc_player.is_lyric_exist(user_current.track_id):
            user_current = self._download_lyric(user_current)
        else:
            if self.lrc_player.get_not_found_file(user_current.track_id):
                self.lrc_player.set_not_found_file(user_current.track_id, "")
            user_current = self._refresh_player_track(user_current)

        print("开始播放歌词")
        ava_trans = self.lrc_player.lrc_file.available_trans()
        self.lrc_player.is_pause = not user_current.is_playing
        self.lrc_player.set_trans_mode(self.user_trans if self.user_trans in ava_trans else TransType.NON)
        if use_api_offset:
            self.lrc_player.restart_thread(user_current.progress_ms, api_offset=user_current.api_offset)
        else:
            self.lrc_player.restart_thread(user_current.progress_ms)

    @thread_drive()
    @CatchError
    def set_user_next_event(self, *_):
        """播放下一首歌"""
        self.spotify_auth.set_user_next()
        time.sleep(0.5)
        self.calibration_event(no_text_show=True)

    @thread_drive()
    @CatchError
    def set_user_previous_event(self, *_):
        """播放上一首歌"""
        self.spotify_auth.set_user_previous()
        time.sleep(0.5)
        self.calibration_event(no_text_show=True)

    @thread_drive()
    @CatchError
    def pause_resume_button_event(self, *_):
        """暂停/恢复 播放 事件"""
        current_user = self.spotify_auth.get_current_playing()
        if current_user.is_playing:
            self.spotify_auth.set_user_pause()
            self.calibration_event(no_text_show=True)
            self.set_pause_button_icon(False)
            self.set_lyrics_rolling(False)
        else:
            self.spotify_auth.set_user_resume()
            self.calibration_event(no_text_show=True)
            self.set_pause_button_icon(True)
            self.set_lyrics_rolling(True)

    @CatchError
    def change_trans_button_event(self, *_):
        """更改当前的翻译"""
        ava_trans = self.lrc_player.lrc_file.available_trans()
        if len(ava_trans) > 1:
            index_ = (ava_trans.index(self.lrc_player.trans_mode) + 1) % len(ava_trans)
            self.lrc_player.set_trans_mode(ava_trans[index_])
            self.user_trans = self.lrc_player.trans_mode
            Config.LyricConfig.trans_type = self.user_trans.value

    @thread_drive()
    @CatchError
    def user_auth_button_event(self, *_):
        """获取用户api权限"""
        self.lrc_player.is_pause = True

        self.set_lyrics_text(1, "正在获取授权链接")
        self.set_lyrics_text(2, "(灬°ω°灬)")

        auth_url = self.spotify_auth.auth.get_user_auth_url()
        webbrowser.open_new(auth_url)
        self.set_lyrics_text(1, "请根据页面完成授权")
        self.set_lyrics_text(2, "ヾ(≧ ▽ ≦)ゝ")

        self.spotify_auth.auth.receive_user_auth_code()
        self.set_lyrics_text(1, "正在获取验证")
        self.set_lyrics_text(2, "ヾ(≧ ▽ ≦)ゝ")
        self.spotify_auth.auth.get_user_access_token()
        self.set_lyrics_text(1, "验证成功！")
        self.calibration_event()

    def setting_open_event(self):
        if self.setting_window.isVisible():
            return
        self.set_hotkey_enable(False)
        self.setting_window.show()

    def setting_close_event(self):
        self.set_hotkey_enable(True)

    def _error_msg_show_event(self, error: Exception):
        """
        在窗口显示错误信息，而并不是程序崩溃

        :param error: 引发的错误实例
        """
        self.lrc_player.is_pause = True
        self.set_lyrics_text(1, str(error))
        self.set_lyrics_text(2, "Σっ°Д°;)っ!")
        if isinstance(error, NoPermission):
            self.delay_timer.start(2000)
            self.delay_timer.timeout.connect(self.calibration_event)

    def _refresh_player_track(self, user_current: UserCurrentPlaying = None, *, no_lyric: bool = False) \
            -> UserCurrentPlaying:
        """
        更新用户播放信息

        :param user_current: 用户播放信息
        :param no_lyric: 是否没有歌词
        :return: 返回输入的用户播放信息
        """
        if not user_current:
            user_current = self.spotify_auth.get_current_playing()
        pos, track_id = user_current.progress_ms, user_current.track_id
        duration = user_current.duration if user_current.duration else 10 * 1000
        self.lrc_player.set_track(track_id, duration, no_lyric=no_lyric)
        return user_current

    def _download_lyric(self, user_current: UserCurrentPlaying) -> UserCurrentPlaying:
        """
        根据 用户播放信息 下载歌词

        :param user_current: 用户播放信息
        :return: 返回输入的用户播放信息
        """
        found_data = self.lrc_player.get_not_found_file(user_current.track_id)
        if found_data and int(time.time()) - found_data["last_time"] < 24 * 3600:
            self.set_lyrics_text(1, f"{user_current.track_name} - {user_current.artist}")
            self.set_lyrics_text(2, f"no lyric found")
            return self._refresh_player_track(no_lyric=True)
        else:
            self.set_lyrics_text(1, "searching for lyric!")
            self.set_lyrics_text(2, f"(〃'▽'〃)")
            try:
                if not download_lrc(f"{user_current.track_name} - {user_current.artist}", user_current.track_id):
                    self.lrc_player.set_not_found_file(user_current.track_id,
                                                       f"{user_current.track_name} - {user_current.artist}")
                    self.set_lyrics_text(1, f"{user_current.track_name} - {user_current.artist}")
                    self.set_lyrics_text(2, f"no lyric found")
                    return self._refresh_player_track(no_lyric=True)
            except requests.RequestException:
                # TODO 归并错误
                print("TOTOTOTOTOTOTOTO DOOOOO ITTTTTTTTTTTTTT!!!!!!")
                self.lrc_player.set_not_found_file(user_current.track_id,
                                                   f"{user_current.track_name} - {user_current.artist}")
                self.set_lyrics_text(1, f"{user_current.track_name} - {user_current.artist}")
                self.set_lyrics_text(2, f"no lyric found")
                return self._refresh_player_track(no_lyric=True)
            # 成功下载
            return self._refresh_player_track()


if __name__ == "__main__":
    # 适配2k等高分辨率屏幕,低分辨率屏幕可以缺省
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = LyricsWindow()
    myWin.show()
    sys.exit(app.exec_())
