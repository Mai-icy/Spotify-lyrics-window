#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests

from components.lyric_window_view import LyricsWindowView

import sys
from functools import wraps
from types import MethodType
import webbrowser
import typing

from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from components.work_thread import thread_drive

from common.api.user_api import SpotifyUserApi, UserCurrentPlaying
from common.api.api_error import UserError
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

    def __init__(self, parent=None):
        super(LyricsWindow, self).__init__(parent)
        self.lrc_player = LrcPlayer(self)
        self.spotify_auth = SpotifyUserApi()
        self._init_signal()

        self.user_trans = TransType.NON

    def _init_signal(self):
        self.account_button.clicked.connect(self.user_auth_event)
        self.calibrate_button.clicked.connect(self.calibration_event)
        self.next_button.clicked.connect(self.set_user_next_event)
        self.last_button.clicked.connect(self.set_user_previous_event)
        self.pause_button.clicked.connect(self.set_user_pause_event)
        self.offsetup_button.clicked.connect(lambda: self.lrc_player.modify_offset(500))
        self.offsetdown_button.clicked.connect(lambda: self.lrc_player.modify_offset(-500))
        self.translate_button.clicked.connect(self.change_trans_event)

        self.error_msg_show_signal.connect(self.error_msg_show_event)
        self.song_done_calibration_signal.connect(lambda: self.calibration_event(use_timestamp=True))

    def error_msg_show_event(self, error):
        self.lrc_player.is_pause = True
        self.set_text(1, str(error), 0)
        self.set_text(2, "Σっ°Д°;)っ!", 0)

    @thread_drive(None)
    @CatchError
    def calibration_event(self, *_, use_timestamp=False):
        self.set_text(1, "calibrating！", 0)
        self.set_text(2, " (o゜▽゜)o!", 0)
        user_current = self.spotify_auth.get_current_playing()
        if user_current.track_name == "ad":
            self.set_text(1, "Advertising！", 0)
            self.set_text(2, "o(_ _)ozzZZ", 0)
            self._refresh_player_track(user_current, no_lyric=True)
            self.lrc_player.restart_thread(0)
            return

        if not self.lrc_player.is_lyric_exist(user_current.track_id):
            user_current = self._download_lyric(user_current)
        else:
            user_current = self._refresh_player_track()

        print("开始播放歌词")
        ava_trans = self.lrc_player.lrc_file.available_trans()
        self.lrc_player.is_pause = not user_current.is_playing
        self.lrc_player.set_trans_mode(self.user_trans if self.user_trans in ava_trans else TransType.NON)
        if use_timestamp:
            self.lrc_player.restart_thread(0, timestamp=user_current.timestamp)
        else:
            self.lrc_player.restart_thread(user_current.progress_ms)

    def _refresh_player_track(self, user_current=None, *, no_lyric=False):
        if not user_current:
            user_current = self.spotify_auth.get_current_playing()
        pos, track_id = user_current.progress_ms, user_current.track_id
        duration = user_current.duration if user_current.duration else 10 * 1000
        self.lrc_player.set_track(track_id, duration, no_lyric=no_lyric)
        return user_current

    def _download_lyric(self, user_current: UserCurrentPlaying) -> UserCurrentPlaying:
        self.set_text(1, "searching for lyric!", 0)
        self.set_text(2, f"(〃'▽'〃)", 0)
        try:
            if not download_lrc(f"{user_current.track_name} - {user_current.artist}", user_current.track_id):
                self.set_text(1, f"{user_current.track_name} - {user_current.artist}", 0)
                self.set_text(2, f"no lyric found", 0)
                return self._refresh_player_track(no_lyric=True)
        except requests.RequestException:
            # TODO 归并错误
            print("TOTOTOTOTOTOTOTO DOOOOO ITTTTTTTTTTTTTT!!!!!!")
            self.set_text(1, f"{user_current.track_name} - {user_current.artist}", 0)
            self.set_text(2, f"no lyric found", 0)
            return self._refresh_player_track(no_lyric=True)
        return self._refresh_player_track()

    @thread_drive(None)
    @CatchError
    def set_user_next_event(self, *_):
        self.spotify_auth.set_user_next()
        self.calibration_event()

    @thread_drive(None)
    @CatchError
    def set_user_previous_event(self, *_):
        self.spotify_auth.set_user_previous()
        self.calibration_event()

    @thread_drive(None)
    @CatchError
    def set_user_pause_event(self, *_):
        self.spotify_auth.set_user_pause()
        self.calibration_event()


    @CatchError
    def change_trans_event(self, *_):
        ava_trans = self.lrc_player.lrc_file.available_trans()
        if len(ava_trans) > 1:
            index_ = (ava_trans.index(self.lrc_player.trans_mode) + 1) % len(ava_trans)
            self.lrc_player.set_trans_mode(ava_trans[index_])
            self.user_trans = self.lrc_player.trans_mode

    @thread_drive(None)
    @CatchError
    def user_auth_event(self, *_):
        self.lrc_player.is_pause = True

        self.set_text(1, "正在获取授权链接", 0)
        self.set_text(2, "(灬°ω°灬)", 0)

        auth_url = self.spotify_auth.auth.get_user_auth_url()
        webbrowser.open_new(auth_url)
        self.set_text(1, "请根据页面完成授权", 0)
        self.set_text(2, "ヾ(≧ ▽ ≦)ゝ", 0)

        self.spotify_auth.auth.receive_user_auth_code()
        self.set_text(1, "正在获取验证", 0)
        self.set_text(2, "ヾ(≧ ▽ ≦)ゝ", 0)
        self.spotify_auth.auth.get_user_access_token()
        self.set_text(1, "验证成功！", 0)
        self.calibration_event()


if __name__ == "__main__":
    # 适配2k等高分辨率屏幕,低分辨率屏幕可以缺省
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myWin = LyricsWindow()
    # myWin.set_text(1, 'test', 1)
    # myWin.set_text(2, 'test', 1)
    myWin.show()
    sys.exit(app.exec_())
