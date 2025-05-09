#!/usr/bin/python
# -*- coding:utf-8 -*-
import collections


MediaPlaybackInfo = collections.namedtuple("MediaPlaybackInfo",
                                           ["playStatus",
                                            "duration",
                                            "position"])

MediaPropertiesInfo = collections.namedtuple("MediaPropertiesInfo",
                                             ["title",
                                              "artist",
                                              "albumTitle",
                                              "albumArtist",
                                              "trackNumber"])
