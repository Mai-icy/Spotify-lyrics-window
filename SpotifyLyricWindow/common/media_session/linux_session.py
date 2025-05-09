#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QMetaType, QVariant
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage, QDBusObjectPath, QDBusVariant
from PyQt6.QtWidgets import QApplication

from common.media_session.base_session import BaseMediaSession
from common.media_session.media_session_type import MediaPropertiesInfo, MediaPlaybackInfo


# dbus-monitor --session "type='signal',interface='org.mpris.MediaPlayer2.Player',member='Seeked'"

# dbus-monitor --session "type='signal',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged'"


class LinuxMediaSession(QObject, BaseMediaSession):
    """Linux 下的异步媒体信号监听器"""
    playback_info_changed = pyqtSignal(dict)
    media_properties_changed = pyqtSignal(dict)
    timeline_properties_changed = pyqtSignal(dict)

    SERVICE = "org.mpris.MediaPlayer2.spotify"
    PATH = "/org/mpris/MediaPlayer2"

    PROP_INTERFACE = "org.freedesktop.DBus.Properties"
    PLAYER_INTERFACE = "org.mpris.MediaPlayer2.Player"

    def __init__(self,):
        super().__init__()
        self.playback_info_changed_func = None
        self.media_properties_changed_func = None
        self.timeline_properties_changed_func = None
        self._is_connect = False

        self._init_dbus()

        self.connect_spotify()

    def _init_dbus(self):
        self.session_bus = QDBusConnection.sessionBus()

        self.properties_interface = QDBusInterface(
            self.SERVICE,
            self.PATH,
            self.PROP_INTERFACE,
            self.session_bus
        )
        
        self.interface_player = QDBusInterface(
            self.SERVICE,
            self.PATH,
            self.PLAYER_INTERFACE,
            self.session_bus
        )

        get_args = [self.SERVICE, self.PATH, self.PROP_INTERFACE, "Get"]

        self.metadata_req = QDBusMessage.createMethodCall(*get_args)
        self.metadata_req.setArguments([self.PLAYER_INTERFACE, "Metadata"])

        self.position_req = QDBusMessage.createMethodCall(*get_args)
        self.position_req.setArguments([self.PLAYER_INTERFACE, "Position"])

        self.playback_req = QDBusMessage.createMethodCall(*get_args)
        self.playback_req.setArguments([self.PLAYER_INTERFACE, "PlaybackStatus"])

        self.position_req = QDBusMessage.createMethodCall(*get_args)
        self.position_req.setArguments([self.PLAYER_INTERFACE, "Position"])

    def get_current_media_properties(self, session=None) -> MediaPropertiesInfo:
        res_metadata = self.session_bus.call(self.metadata_req)
        metadata = res_metadata.arguments()[0]
        info = MediaPropertiesInfo(
            title=metadata.get("xesam:title"),
            artist=", ".join(metadata.get("xesam:artist")),
            albumTitle=metadata.get("xesam:album"),
            albumArtist=", ".join(metadata.get("xesam:albumArtist")),
            trackNumber=metadata.get("xesam:trackNumber")
        )
        return info


    def get_current_playback_info(self, session=None) -> MediaPlaybackInfo:
        res_playback = self.session_bus.call(self.playback_req)
        res_position = self.session_bus.call(self.position_req)
        res_metadata = self.session_bus.call(self.metadata_req)

        playback = res_playback.arguments()[0]
        position = res_position.arguments()[0]
        metadata = res_metadata.arguments()[0]

        info = MediaPlaybackInfo(
            playStatus=4 if playback=="Playing" else 5,
            duration=metadata.get("mpris:length") // 1000,
            position=position // 1000
        )
        return info

    def is_connected(self) -> bool:
        return self.properties_interface.isValid()

    def connect_spotify(self):
        self.properties_interface.isValid()

    def pause_media(self) -> bool:
        if self.interface_player.isValid():
            self.interface_player.call("Pause")
        return self.interface_player.isValid()

    def play_media(self) -> bool:
        if self.interface_player.isValid():
            self.interface_player.call("Play")
        return self.interface_player.isValid()

    def skip_next_media(self) -> bool:
        """播放下一首"""
        if self.interface_player.isValid():
            self.interface_player.call("Next")
        return self.interface_player.isValid()

    def skip_previous_media(self) -> bool:
        """播放上一首"""
        if self.interface_player.isValid():
            self.interface_player.call("Previous")
        return self.interface_player.isValid()

    def play_pause_media(self) -> bool:
        """切换播放状态的 暂停/播放"""
        if self.interface_player.isValid():
            self.interface_player.call("PlayPause")
        return self.interface_player.isValid()

    def seek_to_position_media(self, position):
        res_metadata = self.session_bus.call(self.metadata_req)
        metadata = res_metadata.arguments()[0]
        track_id = metadata.get("mpris:trackid", "")
        track_path = QDBusObjectPath(track_id)
        v = QVariant(position)
        v.convert(QMetaType(QMetaType.Type.LongLong.value))
        self.interface_player.call("SetPosition", track_path, v)

    def playback_info_changed_connect(self, func):
        """绑定pyqt的信号"""
        self.playback_info_changed_func = func

    def media_properties_changed_connect(self, func):
        """绑定pyqt的信号"""
        self.media_properties_changed_func = func

    def timeline_properties_changed_connect(self, func):
        """绑定pyqt的信号"""
        self.timeline_properties_changed_func = func

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = LinuxMediaSession()
    # print(player.get_current_media_properties())
    # print(player.get_current_playback_info())
    print(player.seek_to_position_media(100))

    sys.exit(app.exec())