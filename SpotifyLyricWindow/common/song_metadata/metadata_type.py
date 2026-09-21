#!/usr/bin/python
# -*- coding:utf-8 -*-
import collections

# artistNames 保留接口原始歌手列表；旧调用及仅有署名文本的接口可不提供。
SongInfo = collections.namedtuple("SongInfo",
                                  ["singer",
                                   "songName",
                                   "album",
                                   "year",
                                   "trackNumber",
                                   "duration",
                                   "genre",
                                   "picBuffer",
                                   "artistNames"], defaults=[()])

SongElseInfo = collections.namedtuple(
    "SongElseInfo", [
        "songPath", "suffix", "coverName", "createTime", "modifiedTime", "md5"])


SongSearchInfo = collections.namedtuple(
    "SongSearchInfo", [
        "songName", "singer", "duration", "idOrMd5"])

ArtistAliasInfo = collections.namedtuple(
    "ArtistAliasInfo", ["id", "names"])

# artistNames 按歌手分组保存别名，singerNames 仅用于生成完整署名搜索词。
SongAliasInfo = collections.namedtuple(
    "SongAliasInfo", ["id", "songNames", "singerNames", "duration", "comment", "artistNames"], defaults=[()])


if __name__ == "__main__":
    pass
