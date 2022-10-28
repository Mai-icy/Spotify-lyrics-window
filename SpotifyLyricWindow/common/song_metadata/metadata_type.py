#!/usr/bin/python
# -*- coding:utf-8 -*-
import collections

SongInfo = collections.namedtuple("SongInfo",
                                  ["singer",
                                   "songName",
                                   "album",
                                   "year",
                                   "trackNumber",
                                   "duration",
                                   "genre"])

SongElseInfo = collections.namedtuple(
    "SongElseInfo", [
        "songPath", "suffix", "coverName", "createTime", "modifiedTime", "md5"])


SongSearchInfo = collections.namedtuple(
    "SongSearchInfo", [
        "songName", "singer", "duration", "idOrMd5"])


if __name__ == "__main__":
    pass
