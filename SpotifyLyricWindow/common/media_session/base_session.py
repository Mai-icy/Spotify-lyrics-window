#!/usr/bin/python
# -*- coding:utf-8 -*-
import abc
from io import BytesIO
from common.media_session.media_session_type import MediaPropertiesInfo, MediaPlaybackInfo

class BaseMediaSession:

    def get_current_media_properties(self, session=None) -> MediaPropertiesInfo:
        ...

    def get_current_playback_info(self, session=None) -> MediaPlaybackInfo:
        ...

    def is_connected(self) -> bool:
        ...

    def connect_spotify(self):
        ...

    def pause_media(self) -> bool:
        ...

    def play_media(self) -> bool:
        ...

    def skip_next_media(self) -> bool:
        ...

    def skip_previous_media(self) -> bool:
        ...

    def play_pause_media(self) -> bool:
        ...

    def seek_to_position_media(self, position):
        ...

    def playback_info_changed_connect(self, func):
        ...

    def media_properties_changed_connect(self, func):
        ...

    def timeline_properties_changed_connect(self, func):
        ...




