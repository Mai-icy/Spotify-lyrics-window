#!/usr/bin/python
# -*- coding:utf-8 -*-
import abc
from typing import List
from common.song_metadata.metadata_type import SongInfo, SongSearchInfo
from common.lyric.lyric_type import LrcFile


class BaseMusicApi(abc.ABC):
    _SEARCH_SONG_ID_URL: str
    _SEARCH_SONG_INFO_URL: str
    _FETCH_LYRIC_URL: str

    @abc.abstractmethod
    def search_song_id(self, keyword: str, page: int = 1) -> List[SongSearchInfo]:
        """
        Search the basic information and id of a song.

        :param keyword: the name of track (can include the singer name)
        :param page: (offset is 10) the page of search
        :return: List[SongSearchInfo]
        """
        ...

    @abc.abstractmethod
    def search_song_info(self, song_id: str, *, download_pic: bool = False, pic_size: int = 0) -> SongInfo:
        """
        Get the detailed info of the song.

        :param song_id: the id of track (in Kugou the id is md5 value of track)
        :param download_pic: whether to download the album image
        :param pic_size: the size of album image(must be 64 or 300 or 640 in spotify)
        :return: SongInfo
        """
        ...

    @abc.abstractmethod
    def fetch_song_lyric(self, song_id: str) -> LrcFile:
        """
        Download the lyric of track.

        :param song_id: the id of track
        :return: LrcFile or KrcFile
        """
        ...
