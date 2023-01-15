#!/usr/bin/python
# -*- coding:utf-8 -*-
from enum import Enum

from common.lyric.lyric_type import TransType, LrcFile, KrcFile, MrcFile
from common.song_metadata.metadata_type import SongInfo, SongElseInfo, SongSearchInfo
from common.win_utils.media_session import MediaPlaybackInfo, MediaPropertiesInfo, MediaSession, MediaProperties
from common.api.user_api.user_api import UserCurrentPlaying
from typing import List, Dict


class DisplayMode(Enum):
    Horizontal = 0
    Vertical = 1






