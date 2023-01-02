#!/usr/bin/python
# -*- coding:utf-8 -*-
import asyncio

from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager


async def get_media_session():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()

    if current_session and current_session.source_app_user_model_id == "Spotify.exe":
        return current_session
    else:
        return


def get_time():
    current_session = asyncio.run(get_media_session())
    if not current_session:
        raise Exception
    timeline_info = current_session.get_timeline_properties()
    position = timeline_info.position.duration / 10000
    return position


if __name__ == '__main__':
    print(get_time())
