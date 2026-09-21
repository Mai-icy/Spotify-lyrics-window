#!/usr/bin/python
# -*- coding:utf-8 -*-
import platform
import sys
import threading
import time
import unicodedata
import webbrowser
from functools import wraps
from types import MethodType, SimpleNamespace

import requests
from PyQt6 import QtCore
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from common.api.exceptions import UserError, NoPermission, NetworkError, NoActiveUser
from common.api.user_api import SpotifyUserApi
from common.config import Config
from common.lyric import LyricFileManage
from common.lyric.lyric_download import download_lrc
from common.logger import get_logger, init_logging
from common.player import LrcPlayer
from common.temp_manage import TempFileManage
from common.typing import TransType, UserCurrentPlaying, MediaPropertiesInfo, MediaPlaybackInfo
from components.work_thread import thread_drive
from view.lyric_window.lyrics_window_view import LyricsWindowView
from view.setting_window import SettingWindow

is_support_winrt = False
is_support_dbus = False
is_support_macos = platform.system() == "Darwin"

if platform.system() == "Windows" and int(platform.release()) >= 10:
    from common.media_session.win_session import WindowsMediaSession
    is_support_winrt = True
if platform.system() == "Linux":
    is_support_dbus = True
    from common.media_session.linux_session import LinuxMediaSession

init_logging()
logger = get_logger(__name__)


def player_state_locked(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._calibration_lock:
            return func(self, *args, **kwargs)
    return wrapper


class CatchError:
    def __init__(self, func):
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        def show_error(error):
            request_id = kwargs.get("_calibration_id")
            if request_id is None:
                args[0].error_msg_show_signal.emit(error)
            else:
                args[0].calibration_error_signal.emit(request_id, error)

        try:
            return self.__wrapped__(*args, **kwargs)
        except UserError as e:
            show_error(e)
        except requests.RequestException as e:
            logger.exception("Requests error in %s", self.__wrapped__.__name__)
            new_err = Exception("Requests Error")
            show_error(new_err)
        except NotImplementedError as e:
            show_error(str(e))
        except NetworkError as e:
            show_error(str(e))
        except Exception as e:
            logger.exception("Unhandled error in %s", self.__wrapped__.__name__)
            show_error("Unknown Error. Refer to log (resource/error.log)")

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return MethodType(self, instance)


class LyricsWindow(LyricsWindowView):
    error_msg_show_signal = pyqtSignal(object)
    text_show_signal = pyqtSignal(int, str, int)
    pause_icon_signal = pyqtSignal(bool)
    account_enabled_signal = pyqtSignal(bool)
    delay_calibration_signal = pyqtSignal(int)
    calibration_error_signal = pyqtSignal(int, object)

    def __init__(self, parent=None):
        super(LyricsWindow, self).__init__(parent)

        self._manual_skip_flag = True

        self._init_common()
        self._init_lrc_player()
        self._init_signal()
        self._init_media_session()

        self.calibration_event(use_api_position=True)

    def _re_init(self):
        """重新初始化"""
        super(LyricsWindow, self)._re_init()
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
        self.offsetup_button.clicked.connect(self.lyric_offset_add_event)
        self.offsetdown_button.clicked.connect(self.lyric_offset_minus_event)
        self.translate_button.clicked.connect(self.change_trans_button_event)
        self.settings_button.clicked.connect(self._setting_window_show_event)

        self.error_msg_show_signal.connect(self._error_msg_show_event)
        self.text_show_signal.connect(self.set_lyrics_text)
        self.pause_icon_signal.connect(self.set_pause_button_icon)
        self.account_enabled_signal.connect(self.account_button.setEnabled)
        self.delay_calibration_signal.connect(self.delay_timer.start)
        self.lrc_player.play_done_event_connect(self.player_done_event)

    def _init_lrc_player(self):
        """初始化歌词播放器"""
        self.lrc_player = LrcPlayer(output_func=self.text_show_signal.emit)
        self.lrc_player.set_trans_mode(self.user_trans)

    def _init_common(self):
        """初始化其他辅助部件"""
        self._calibration_lock = threading.RLock()
        self._calibration_id = 0
        self.calibration_error_signal.connect(self._calibration_error_event)
        self.lyric_file_manage = LyricFileManage()
        self.temp_manage = TempFileManage()

        self.user_trans = TransType(Config.LyricConfig.trans_type)

        self.spotify_auth = SpotifyUserApi()
        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self.calibration_event)

        if not hasattr(self, "setting_window"):
            self.setting_window = None  # 初始化为空，在打开的时候被定义，关闭的时候被释放

    def _init_media_session(self):
        """初始化 media session"""
        if is_support_winrt:
            self.media_session = WindowsMediaSession()

            self.media_session.media_properties_changed_connect(self.media_properties_changed)
            self.media_session.playback_info_changed_connect(self.playback_info_changed)
            self.media_session.timeline_properties_changed_connect(self.timeline_properties_changed)
        elif is_support_dbus:
            self.media_session = LinuxMediaSession()

            self.media_session.media_properties_changed_connect(self.media_properties_changed)
            self.media_session.playback_info_changed_connect(self.playback_info_changed)
            self.media_session.timeline_properties_changed_connect(self.timeline_properties_changed)
        elif is_support_macos:
            from common.media_session.mac_session import MacMediaSession

            self.media_session = MacMediaSession(self)
            self.media_session.media_properties_changed_connect(self.media_properties_changed)
            self.media_session.playback_info_changed_connect(self.playback_info_changed)
            self.media_session.timeline_properties_changed_connect(self.timeline_properties_changed)
            self.media_session.disconnected.connect(self._mac_media_session_disconnected)
        else:
            self.media_session = SimpleNamespace()
            self.media_session.is_connected = lambda: False
            self.media_session.connect_spotify = lambda: False

    def player_done_event(self):
        """当前歌曲播放的事件"""
        self._manual_skip_flag = False
        if not self.media_session.is_connected():
            self.calibration_event()

    def _mac_media_session_disconnected(self):
        self.calibration_event(no_text_show=True, use_api_position=True)

    @player_state_locked
    def _clear_player_state(self):
        """清空当前歌词上下文，避免旧歌词在无活跃用户时被重新唤起"""
        self._calibration_id += 1
        self.lrc_player.set_pause(True)
        self.lrc_player.set_track("", 0)
        self.lrc_player.seek_to_position(0, is_show_last_lyric=False)
        self._manual_skip_flag = True

    def _has_active_track(self) -> bool:
        return bool(self.lrc_player.track_id)

    @player_state_locked
    def media_properties_changed(self, info: MediaPropertiesInfo):
        # Even a cached track switch must invalidate pending API/download work.
        self._calibration_id += 1
        if not self._has_active_track():
            self.calibration_event(no_text_show=True)
            return
        self.lrc_player.set_pause(True)

        track_title = f"{info.title} - {info.artist}"
        track_id = self.lyric_file_manage.get_id(track_title)
        if track_id and not self.lyric_file_manage.get_not_found(track_id):  # 如果可以通过title直接获取id, 则不走api渠道
            playback_info = self.media_session.get_current_playback_info()
            self.lrc_player.set_track(track_id, playback_info.duration)
            if not self._manual_skip_flag:
                # 自动切换到下一首歌 将会有将近700ms的歌曲准备时间导致时间定位不准确
                if Config.CommonConfig.is_auto_track_sync:
                    time.sleep(0.7)
                    self.media_session.seek_to_position_media(0)
                    self.lrc_player.seek_to_position(0)
                else:
                    self.lrc_player.seek_to_position(playback_info.position)
                self._manual_skip_flag = True
            self.lrc_player.set_pause(not (playback_info.playStatus == 4))
        else:
            if not self._manual_skip_flag:
                # 自动切换到下一首歌 将会有将近700ms的歌曲准备时间导致时间定位不准确
                if Config.CommonConfig.is_auto_track_sync:
                    time.sleep(0.7)
                    self.media_session.seek_to_position_media(0)
                    self.lrc_player.seek_to_position(0)
                self._manual_skip_flag = True
            else:
                # 手动切换到下一首歌 可能会有延迟也可能没有，故不做处理
                time.sleep(0.5)  # 等待api反应过来
            self.calibration_event()

    @player_state_locked
    def playback_info_changed(self, info: MediaPlaybackInfo):
        if not self._has_active_track():
            return
        self.lrc_player.seek_to_position(info.position)
        is_playing = info.playStatus == 4  # 4 代表正在播放 实际播放的枚举值为4
        self.lrc_player.set_pause(not is_playing)
        self.set_pause_button_icon(is_playing)
        self.set_lyrics_rolling(is_playing)

    @player_state_locked
    def timeline_properties_changed(self, info: MediaPlaybackInfo):
        if not self._manual_skip_flag or not self._has_active_track():
            return
        if info.position < 500 or self.lrc_player.is_pause:
            # 由于切换到下一首歌会同时触发timeline和properties的变化信号，利用position<500过滤掉切换歌时候的timeline信号
            self.lrc_player.seek_to_position(info.position, is_show_last_lyric=False)
            return
        self.lrc_player.seek_to_position(info.position)

    def calibration_event(self, *_, no_text_show: bool = False, use_api_position: bool = False):
        # Allocate before starting the thread: request order, not completion
        # order, determines which calibration may update the player.
        with self._calibration_lock:
            self._calibration_id += 1
            request_id = self._calibration_id
        self._run_calibration(no_text_show=no_text_show, use_api_position=use_api_position,
                              _calibration_id=request_id)

    @player_state_locked
    def _calibration_error_event(self, request_id, error):
        if request_id == self._calibration_id:
            self._error_msg_show_event(error)

    def _calibration_matches_session(self, user_current, properties):
        """Never combine an API track ID with another session's track name."""
        if not self.media_session.is_connected():
            return properties is None
        current = self.media_session.get_current_media_properties()
        if properties is None or current != properties or not user_current.track_id:
            return False
        normalize = lambda title: unicodedata.normalize("NFKC", title or "").strip().casefold()
        playback = self.media_session.get_current_playback_info()
        return (normalize(user_current.track_name) == normalize(current.title) and
                bool(user_current.duration and playback.duration) and
                abs(user_current.duration - playback.duration) <= 2000)

    @thread_drive()
    @CatchError
    def _run_calibration(self, *, no_text_show=False, use_api_position=False, _calibration_id):
        """
        同步歌词

        :param no_text_show: 是否显示 ‘校准中！’ 的 正在校准提示
        :param use_api_position: 是否使用api的时间进行校准
        """
        with self._calibration_lock:
            if _calibration_id != self._calibration_id:
                return
            properties = (self.media_session.get_current_media_properties()
                          if self.media_session.is_connected() else None)
            if not no_text_show:
                self.text_show_signal.emit(1, self.tr("校准中！"), 0)
                self.text_show_signal.emit(2, self.tr(" (o゜▽゜)o!"), 0)

        # Spotify's web API can lag behind the desktop notification. Retry a
        # bounded number of times, without holding the player lock over I/O.
        for attempt in range(3):
            with self._calibration_lock:
                if _calibration_id != self._calibration_id:
                    return
            user_current = self.spotify_auth.get_current_playing()
            with self._calibration_lock:
                if _calibration_id != self._calibration_id:
                    return
                if self._calibration_matches_session(user_current, properties):
                    break
            if attempt == 2:
                logger.warning("Ignoring calibration: API and media session tracks do not match")
                return
            time.sleep(0.5)

        with self._calibration_lock:
            if _calibration_id != self._calibration_id:
                return
            if not user_current.track_id:  # 正在播放非音乐（track）
                self.text_show_signal.emit(1, user_current.track_name + "!", 0)
                self.text_show_signal.emit(2, self.tr("o(_ _)ozzZZ"), 0)
                self._clear_player_state()
                return
            track_id = user_current.track_id

        if not self.lyric_file_manage.is_lyric_exist(user_current.track_id):
            user_current = self._download_lyric(user_current, _calibration_id=_calibration_id)
            if user_current is None:
                return

        with self._calibration_lock:
            if _calibration_id != self._calibration_id:
                return
            if (user_current.track_id != track_id or
                    not self._calibration_matches_session(user_current, properties)):
                self.delay_calibration()
                return
            if properties is not None:
                track_title = f"{properties.title} - {properties.artist}"
                if self.lyric_file_manage.get_title(track_id) != track_title:
                    self.lyric_file_manage.set_track_id_map(track_id, track_title)
            if self.lyric_file_manage.get_not_found(user_current.track_id):  # 歌词文件存在 但 被记录为不存在
                if self.lyric_file_manage.is_lyric_exist(user_current.track_id):
                    self.lyric_file_manage.set_not_found(user_current.track_id, "")
            self.lrc_player.set_pause(True)
            user_current = self._refresh_player_track(user_current)
            self.pause_icon_signal.emit(user_current.is_playing)
            self.set_lyrics_rolling(user_current.is_playing)
            self.lrc_player.set_pause(not user_current.is_playing)

            if not self.media_session.is_connected() or use_api_position:
                self.lrc_player.seek_to_position(user_current.progress_ms)
            elif is_support_macos:
                self.lrc_player.seek_to_position(self.media_session.get_current_playback_info().position)

    @thread_drive()
    @CatchError
    def set_user_next_event(self, *_):
        """播放下一首歌"""
        if self.media_session.is_connected() and self.media_session.skip_next_media():
            return
        self.spotify_auth.set_user_next()
        time.sleep(0.5)
        self.calibration_event(no_text_show=True)

    @thread_drive()
    @CatchError
    def set_user_previous_event(self, *_):
        """播放上一首歌"""
        if self.media_session.is_connected() and self.media_session.skip_previous_media():
            return
        self.spotify_auth.set_user_previous()
        time.sleep(0.5)
        self.calibration_event(no_text_show=True)

    @thread_drive()
    @CatchError
    def pause_resume_button_event(self, *_):
        """暂停/恢复 播放 事件"""
        if self.media_session.is_connected() and self.media_session.play_pause_media():
            return

        current_user = self.spotify_auth.get_current_playing()
        if current_user.is_playing:
            self.spotify_auth.set_user_pause()
            self.calibration_event(no_text_show=True)
            self.pause_icon_signal.emit(False)
            self.set_lyrics_rolling(False)
        else:
            self.spotify_auth.set_user_resume()
            self.calibration_event(no_text_show=True)
            self.pause_icon_signal.emit(True)
            self.set_lyrics_rolling(True)

    @CatchError
    def change_trans_button_event(self, *_):
        """更改当前的翻译为下一个 可用的 翻译"""
        ava_trans = self.lrc_player.lrc_file.available_trans()
        if len(ava_trans) > 1:
            index_ = (ava_trans.index(self.lrc_player.trans_mode) + 1) % len(ava_trans)
            self.set_trans_mode(ava_trans[index_])

    @thread_drive()
    @CatchError
    def user_auth_button_event(self, *_):
        """获取用户api权限"""
        self.lrc_player.is_pause = True

        self.text_show_signal.emit(1, self.tr("正在获取授权链接"), 0)
        self.text_show_signal.emit(2, self.tr("(灬°ω°灬)"), 0)

        auth_url = self.spotify_auth.auth.get_user_auth_url()
        webbrowser.open_new(auth_url)
        # driver = webdriver.Edge()
        # driver.get(auth_url)

        self.text_show_signal.emit(1, self.tr("请根据页面完成授权"), 0)
        self.text_show_signal.emit(2, self.tr("ヾ(≧ ▽ ≦)ゝ"), 0)
        try:
            if not self.spotify_auth.auth.is_listen:
                self.spotify_auth.auth.receive_user_auth_code()
        except OSError:
            self.account_enabled_signal.emit(True)
            raise UserError(self.tr("端口8888被占用，请检查端口占用"))

        # driver.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")
        # sp_dc_dict = driver.get_cookie("sp_dc") or {}
        # sp_dc = sp_dc_dict.get("value")
        # driver.quit()

        self.text_show_signal.emit(1, self.tr("正在获取验证"), 0)
        self.text_show_signal.emit(2, self.tr("ヾ(≧ ▽ ≦)ゝ"), 0)

        # Config.CommonConfig.ClientConfig.sp_dc = sp_dc
        # 模拟浏览器行为会导致登陆被阻止，放弃自动获取sp_dc的行为，改为用户自己添加。
        self.spotify_auth.auth.get_user_access_token()
        self.text_show_signal.emit(1, self.tr("验证成功！"), 0)
        self.calibration_event()

    def lyric_offset_add_event(self):
        """调整偏移事件  歌词前进"""
        self.lrc_player.modify_offset(500)

    def lyric_offset_minus_event(self):
        """调整偏移事件  歌词后退"""
        self.lrc_player.modify_offset(-500)

    def _setting_window_destroyed_event(self):
        """设置窗口关闭连接事件"""
        # 设置窗口已经关闭释放内存，此时self.setting_window为nullptr，将此处定义为None
        self.setting_window = None

    def _setting_window_show_event(self):
        """显示设置窗口事件，新建一个窗口对象"""
        if self.setting_window is None:
            self.setting_window = SettingWindow(lyric_window=self)
            self.setting_window.destroyed.connect(self._setting_window_destroyed_event)
            self.setting_window.show()
        if is_support_macos and QApplication.platformName() == 'cocoa':
            # With no Dock entry, the tray must also recover an existing window.
            # Do not call SettingWindow.show() again: it reloads in-progress edits.
            from common.macos.window import activate_application
            activate_application()
            window = QApplication.activeModalWidget() or self.setting_window
            if window.isMinimized():
                window.showNormal()
            window.raise_()
            window.activateWindow()

    def set_trans_mode(self, mode: TransType):
        """
        设置当前翻译

        :param mode: 翻译的模式
        """
        self.lrc_player.set_trans_mode(mode)
        self.user_trans = mode
        Config.LyricConfig.trans_type = self.user_trans.value

    def _error_msg_show_event(self, error: Exception):
        """
        在窗口显示错误信息，而并不是程序崩溃

        :param error: 引发的错误实例
        """
        self.lrc_player.is_pause = True
        if isinstance(error, NoActiveUser):
            self._clear_player_state()
        self.text_show_signal.emit(1, self.tr(str(error)), 0)
        self.text_show_signal.emit(2, self.tr("Σっ°Д°;)っ!"), 0)
        if isinstance(error, NoPermission):
            self.delay_calibration()

    def delay_calibration(self):
        """延时触发校准事件"""
        self.delay_calibration_signal.emit(2000)

    def _refresh_player_track(self, user_current: UserCurrentPlaying = None) -> UserCurrentPlaying:
        """
        更新用户播放信息

        :param user_current: 用户播放信息
        :return: 返回输入的用户播放信息
        """
        if not user_current:
            user_current = self.spotify_auth.get_current_playing()
        pos, track_id = user_current.progress_ms, user_current.track_id
        duration = user_current.duration if user_current.duration else 10 * 1000
        self.lrc_player.set_track(track_id, duration)
        return user_current

    @CatchError
    def _download_lyric(self, user_current: UserCurrentPlaying, *, _calibration_id=None) -> UserCurrentPlaying:
        """
        根据 用户播放信息 下载歌词

        :param user_current: 用户播放信息
        :return: 返回输入的用户播放信息
        """
        with self._calibration_lock:
            if _calibration_id is not None and _calibration_id != self._calibration_id:
                return
            found_data = self.lyric_file_manage.get_not_found(user_current.track_id)
            recently_missing = found_data and int(time.time()) - found_data["last_time"] < 24 * 3600
            if not recently_missing:
                self.text_show_signal.emit(1, self.tr("查找歌词中！"), 0)
                self.text_show_signal.emit(2, self.tr("(〃'▽'〃)"), 0)
        if recently_missing:
            # 最近 24h 内自动下载过但是失败 将在 24h 后重试 24h 内将不重试
            is_success = False
        else:
            is_success = download_lrc(f"{user_current.track_name} - {user_current.artist}", user_current.track_id)
        with self._calibration_lock:
            if _calibration_id is not None and _calibration_id != self._calibration_id:
                return
            if not is_success:
                if not recently_missing:
                    self.lyric_file_manage.set_not_found(user_current.track_id,
                                                         f"{user_current.track_name} - {user_current.artist}")
                self.text_show_signal.emit(1, f"{user_current.track_name} - {user_current.artist}", 0)
                self.text_show_signal.emit(2, self.tr("无歌词"), 0)
            if not recently_missing:
                self.delay_calibration()
        return self.spotify_auth.get_current_playing()

    def closeEvent(self, event: QCloseEvent):
        with self._calibration_lock:
            self._calibration_id += 1
        if is_support_macos:
            self.media_session.close()
        self.delay_timer.stop()
        self.lrc_player.close()
        del self.lrc_player
        del self.lyric_file_manage
        self.temp_manage.auto_clean_temp()
        super(LyricsWindow, self).closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = LyricsWindow()
    myWin.show()
    sys.exit(app.exec())
