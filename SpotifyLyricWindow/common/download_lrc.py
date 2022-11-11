#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests

from common.api import *
from common.song_metadata.compare_metadata import compare_song_info
from common.path import LRC_PATH

cloud_api = CloudMusicWebApi()
kugou_api = KugouApi()
spotify_api = SpotifyApi()


def download_lrc(track_name: str, track_id: str, *, min_score=74) -> bool:
    """download lyric by the track_id. Kugou and Cloud Api were used."""
    file_name = LRC_PATH / f"{track_id}.mrc"

    # min_score = 74  # 最低相似度评分

    spotify_info = spotify_api.get_song_info(track_id)
    try:
        cloud_song_id = cloud_api.search_data(track_name)[0].idOrMd5
        cloud_song_info = cloud_api.get_song_info(cloud_song_id)
    except NoneResultError:
        cloud_song_info = cloud_song_id = None
    try:
        kugou_song_md5 = kugou_api.search_hash(track_name)[0].idOrMd5
        kugou_song_info = kugou_api.get_song_info(kugou_song_md5)
    except NoneResultError:
        kugou_song_info = kugou_song_md5 = None

    score_cloud = compare_song_info(cloud_song_info, spotify_info)
    score_kugou = compare_song_info(kugou_song_info, spotify_info)
    # print(score_cloud, score_kugou)

    if score_kugou >= score_cloud and score_kugou > min_score:
        try:
            lrc_info = kugou_api.get_lrc_info(kugou_song_md5)[0]
            lrc = kugou_api.get_lrc(lrc_info)
            if not lrc.empty():
                lrc.save_to_mrc(str(file_name))
                return True
        except requests.RequestException:
            score_kugou = 0

    if score_cloud >= score_kugou and score_cloud > min_score:
        try:
            lrc = cloud_api.get_lrc(cloud_song_id)
            if not lrc.empty():
                lrc.save_to_mrc(str(file_name))
                return True
        except requests.RequestException:
            pass
    return False


if __name__ == "__main__":
    # download_lrc("蜜蜂 - DUSTCELL", "6oDv2ylQf1fiqOMp7UWcV8")
    # download_lrc("インナアチャイルド - 理芽", "2VviHaihEuSsYo6OOqxJ7m")
    # download_lrc("ice melt - Cö Shu Nie", "07JUoZ3jQ0kr9DwFJeOGlr")
    # download_lrc("ブルーノート - 水槽", "3Ug6cD9VZE2J9eHc5jCASh")
    # download_lrc("Void - DUSTCELL", "5QnnLbeNiTPQn68agY3i6D")
    # download_lrc("蜜蜂 - DUSTCELL", "6oDv2ylQf1fiqOMp7UWcV8")
    pass




