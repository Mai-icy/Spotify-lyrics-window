#!/usr/bin/python
# -*- coding:utf-8 -*-

import asyncio
import time
from collections import namedtuple
from functools import wraps, partial
from io import BytesIO
from types import MethodType

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    GlobalSystemMediaTransportControlsSession as MediaSession,
    GlobalSystemMediaTransportControlsSessionMediaProperties as MediaProperties)
from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions

MediaPlaybackInfo = namedtuple("MediaPlaybackInfo", ["playStatus", "duration", "position"])
MediaPropertiesInfo = namedtuple("MediaPropertiesInfo", ["title", "artist", "albumTitle", "albumArtist", "trackNumber"])


class NoSpotifyRunning(Exception):
    """Spotify并没有在此台机器运行"""


def TimesCallOnce(times):
    """将多次的函数触发转为一次"""
    return partial(_TimesCallOnce, times=times)


class _TimesCallOnce:
    def __init__(self, func, times):
        wraps(func)(self)
        self.last_time = 0
        self.ava_times = 0

        self.call_time = times

    def __call__(self, *args, **kwargs):
        if time.time() - self.last_time < 0.5:
            self.ava_times += 1
        else:
            self.ava_times = 1
            self.last_time = time.time()
        if self.ava_times >= self.call_time:
            self.ava_times = 0
            self.last_time = 0
            return self.__wrapped__(*args, **kwargs)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return MethodType(self, instance)


class WindowsMediaSession:
    """
    winrt参考：
    https://learn.microsoft.com/zh-cn/uwp/api/windows.media.control.globalsystemmediatransportcontrolssession
    对于python的winrt需要修改函数名为下划线命名法
    """
    def __init__(self):
        self.TARGET_ID = "Spotify.exe"

        self.playback_info_changed_func = None
        self.media_properties_changed_func = None
        self.timeline_properties_changed_func = None

        self._is_connect = False

        self.connect_spotify()

    def _init_signal_func(self, session):
        """连接 MediaSession 信号函数"""
        # 播放状态变化的时候触发
        self.playback_info_changed_token = session.add_playback_info_changed(self._playback_info_changed_func)
        # 切换歌曲的时候触发
        self.media_properties_changed_token = session.add_media_properties_changed(self._media_properties_changed_func)
        # 时间线变化的时候触发
        self.timeline_properties_changed_token = session.add_timeline_properties_changed(
            self._timeline_properties_changed_func)

        self._is_connect = True

    async def _get_media_session(self) -> MediaSession:
        """获取当前的 MediaSession"""
        session_manager = await MediaManager.request_async()
        all_sessions = session_manager.get_sessions()
        for current_session in all_sessions:
            if current_session and current_session.source_app_user_model_id == self.TARGET_ID:
                if not self._is_connect:
                    self._init_signal_func(current_session)
                return current_session
        self._is_connect = False
        raise NoSpotifyRunning

    async def _media_async_operate(self, operate, *args) -> bool:
        """MediaSession 对应操作函数"""
        session = await self._get_media_session()
        if not session:
            return False
        func = getattr(session, operate)
        res_flag = await func(*args)
        return res_flag

    async def _get_media_properties(self, session=None) -> MediaProperties:
        """获取 session 对应的 MediaProperties (见文档) """
        if not session:
            session = await self._get_media_session()
        media_properties = await session.try_get_media_properties_async()
        return media_properties

    @staticmethod
    async def _read_stream_into_buffer(stream_ref, buffer):
        """创建读取内存流， 配合完成读取歌曲缩略图"""
        readable_stream = await stream_ref.open_read_async()
        readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)

    def _playback_info_changed_func(self, session: MediaSession, event):
        """信号对应函数，将会同步触发对应函数并传输当前播放状态"""
        if self.playback_info_changed_func:
            info = self.get_current_playback_info()
            self.playback_info_changed_func(info)

    @TimesCallOnce(2)
    def _media_properties_changed_func(self, session: MediaSession, event):
        """信号对应函数，将会同步触发对应函数并传输当前播放状态"""
        if self.media_properties_changed_func:
            info = self.get_current_media_properties(session)
            self.media_properties_changed_func(info)

    @TimesCallOnce(3)
    def _timeline_properties_changed_func(self, session: MediaSession, event):
        """信号对应函数，将会同步触发对应函数并传输当前播放状态"""
        if self.timeline_properties_changed_func:
            info = self.get_current_playback_info()
            self.timeline_properties_changed_func(info)

    def get_current_media_properties(self, session=None) -> MediaPropertiesInfo:
        """获取对应 session 的 MediaProperties 并进行重新包装返回"""
        if not session:
            session = asyncio.run(self._get_media_session())
        media_properties = asyncio.run(self._get_media_properties(session))

        info = MediaPropertiesInfo(
            title=media_properties.title,
            artist=media_properties.artist,
            albumTitle=media_properties.album_title,
            albumArtist=media_properties.album_artist,
            trackNumber=media_properties.track_number
        )
        return info

    def get_current_playback_info(self, session=None) -> MediaPlaybackInfo:
        """获取对应 session 的 播放器状态 并进行重新包装返回"""
        if not session:
            session = asyncio.run(self._get_media_session())
        timeline_properties = session.get_timeline_properties()
        playback_info = session.get_playback_info()
        info = MediaPlaybackInfo(
            playStatus=playback_info.playback_status,
            duration=timeline_properties.end_time.duration // 10000,
            position=timeline_properties.position.duration // 10000  # position并不会实时更新 而是每过一段时间更新一次 会触发信号
        )
        return info

    def is_connected(self) -> bool:
        """是否连接上spotify桌面应用"""
        return self._is_connect

    def connect_spotify(self):
        """尝试连接spotify桌面应用"""
        if self._is_connect:
            return True
        try:
            asyncio.run(self._get_media_session())
        except NoSpotifyRunning:
            ...

    def pause_media(self) -> bool:
        """暂停音乐"""
        return asyncio.run(self._media_async_operate("try_pause_async"))

    def play_media(self) -> bool:
        """播放音乐"""
        return asyncio.run(self._media_async_operate("try_play_async"))

    def skip_next_media(self) -> bool:
        """播放下一首"""
        return asyncio.run(self._media_async_operate("try_skip_next_async"))

    def skip_previous_media(self) -> bool:
        """播放上一首"""
        if self.get_current_playback_info().position > 2500:
            asyncio.run(self._media_async_operate("try_skip_previous_async"))
        # 需要操作两次才能回到上一首
        return asyncio.run(self._media_async_operate("try_skip_previous_async"))

    def play_pause_media(self) -> bool:
        """切换播放状态的 暂停/播放"""
        return asyncio.run(self._media_async_operate("try_toggle_play_pause_async"))

    def seek_to_position_media(self, position):
        """转到position处进行播放"""
        return asyncio.run(self._media_async_operate("try_change_playback_position_async", position))

    def get_current_thumbnail(self) -> BytesIO:
        """获取当前播放歌曲的缩略图"""
        media_properties = asyncio.run(self._get_media_properties())
        thumb_stream_ref = media_properties.thumbnail

        thumb_read_buffer = Buffer(500000)  # 0.5MB
        asyncio.run(self._read_stream_into_buffer(thumb_stream_ref, thumb_read_buffer))

        buffer_reader = DataReader.from_buffer(thumb_read_buffer)
        byte_buffer = buffer_reader.read_bytes(thumb_read_buffer.length)

        pic = BytesIO(bytearray(byte_buffer))
        return pic

    def playback_info_changed_connect(self, func):
        """绑定pyqt的信号"""
        self.playback_info_changed_func = func

    def media_properties_changed_connect(self, func):
        """绑定pyqt的信号"""
        self.media_properties_changed_func = func

    def timeline_properties_changed_connect(self, func):
        """绑定pyqt的信号"""
        self.timeline_properties_changed_func = func


if __name__ == '__main__':
    test_manage = WindowsMediaSession()
    for i in range(100):
        test_manage.connect_spotify()
        print(test_manage.is_connected())
        time.sleep(2)

    time.sleep(1000000)
