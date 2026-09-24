"""macOS Now Playing events, lazily using macos-mediaremote-python."""
import asyncio
import logging
import math
import sys
import threading
import time
from dataclasses import dataclass

from PyQt6.QtCore import QCoreApplication, QObject, QTimer, pyqtSignal, pyqtSlot

from common.media_session.base_session import BaseMediaSession
from common.media_session.media_session_type import MediaPlaybackInfo, MediaPropertiesInfo


logger = logging.getLogger("spotify_lyrics_window." + __name__)


# 只读取 Spotify 自身的时间轴，避免系统会话在恢复窗口时错误归零。
# 参数由 subprocess 独立传入，不把歌曲名拼进脚本。
_SPOTIFY_POSITION_SCRIPT = '''
on run argv
    if application "Spotify" is not running then return "mismatch"
    tell application "Spotify"
        set currentSong to current track
        set songID to id of currentSong
        if name of currentSong is not (item 1 of argv) then return "mismatch"
        if artist of currentSong is not (item 2 of argv) then return "mismatch"
        if album of currentSong is not (item 3 of argv) then return "mismatch"
        set songPosition to player position
        set songState to player state as text
        if id of current track is not songID then return "mismatch"
        return (songPosition as text) & linefeed & songState
    end tell
end run
'''


class _MediaRemoteStream(threading.Thread):
    """Own the package's asyncio subscription without touching Qt widgets."""

    def __init__(self, client, received, failed):
        super().__init__(name="MediaRemote", daemon=True)
        self.client = client
        self.received = received
        self.failed = failed
        self._stopping = threading.Event()
        self._lock = threading.Lock()
        self._loop = None
        self._task = None
        self._script_retry_at = 0

    def run(self):
        try:
            asyncio.run(self._subscribe())
        except asyncio.CancelledError:
            pass
        except Exception as error:
            if not self._stopping.is_set():
                self.failed(str(error))

    async def _subscribe(self):
        with self._lock:
            self._loop = asyncio.get_running_loop()
            self._task = asyncio.current_task()
        try:
            if self._stopping.is_set():
                return
            async with self.client.stream() as events:
                async for state in events:
                    if self._stopping.is_set():
                        return
                    data = await self._verify_position(dict(state.raw) if state else {})
                    if self._stopping.is_set():
                        return
                    self.received(data, time.monotonic(), time.time())
            if not self._stopping.is_set():
                raise RuntimeError("MediaRemote stream ended")
        finally:
            with self._lock:
                self._loop = self._task = None

    async def _verify_position(self, data):
        """后台核验后再发出事件；失败回退 MediaRemote，不阻塞 Qt 或持续轮询。"""
        if (data.get("bundleIdentifier") != MacMediaSession.TARGET_ID or
                data.get("isAdvertisement") or not data.get("title") or
                data.get("durationMicros") is None or time.monotonic() < self._script_retry_at):
            return data
        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                "/usr/bin/osascript", "-e", _SPOTIFY_POSITION_SCRIPT, "--",
                data["title"], data.get("artist") or "", data.get("album") or "",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            output, error = await asyncio.wait_for(process.communicate(), timeout=2)
            if process.returncode:
                if b"-1743" in error:  # 用户拒绝自动化权限，本次运行不再尝试。
                    self._script_retry_at = float("inf")
                raise ValueError("Spotify AppleScript query failed")
            if output.strip() == b"mismatch":
                # 查询期间已切歌，暂时断开旧会话，等待新通知或 API 校准。
                return {}
            position, state = output.decode("utf-8").strip().splitlines()
            position = float(position.replace(",", "."))
            if not math.isfinite(position) or position < 0 or state not in ("playing", "paused", "stopped"):
                raise ValueError("Invalid Spotify AppleScript position")
            logger.debug("Spotify AppleScript progress: track=%s, position_ms=%s, state=%s",
                         data["title"], round(position * 1000), state)
            return dict(data, elapsedTimeMicros=round(position * 1000000),
                        timestampEpochMicros=round(time.time() * 1000000),
                        playing=state == "playing", playbackRate=1 if state == "playing" else 0)
        except (OSError, ValueError, OverflowError, asyncio.TimeoutError):
            self._script_retry_at = max(self._script_retry_at, time.monotonic() + 30)
            logger.warning("Spotify AppleScript unavailable; using MediaRemote progress", exc_info=True)
            return data
        finally:
            if process is not None and process.returncode is None:
                process.kill()
                await process.communicate()

    def stop(self):
        with self._lock:
            if self._stopping.is_set():
                return
            self._stopping.set()
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._task.cancel)


@dataclass(frozen=True)
class _Snapshot:
    identity: tuple
    pid: int
    properties: MediaPropertiesInfo
    playback: MediaPlaybackInfo
    captured_at: float
    rate: float
    source_timing: tuple


class MacMediaSession(QObject, BaseMediaSession):
    """Subscribe to system events and expose the existing media-session contract.

    Construct on the Qt GUI thread. The package owns the native helper;
    getters use an immutable cache, and controls run on existing worker threads.
    Only the Spotify Desktop Now Playing session is accepted. All public times
    are milliseconds; package controls use seconds and raw events use microseconds.
    """

    media_properties_changed = pyqtSignal(object)
    playback_info_changed = pyqtSignal(object)
    timeline_properties_changed = pyqtSignal(object)
    disconnected = pyqtSignal()
    _payload_received = pyqtSignal(object, float, float)
    _stream_failed = pyqtSignal(str)

    TARGET_ID = "com.spotify.client"
    STARTUP_TIMEOUT_MS = 10000
    CONTROL_TIMEOUT_SECONDS = 5
    MAX_BUFFER_BYTES = 1024 * 1024
    SEEK_THRESHOLD_MS = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self._snapshot = None
        self._closed = False
        self._failed = False
        self._client = None
        self._worker = None
        self._payload_received.connect(self._receive_payload)
        self._stream_failed.connect(self._fail)
        self._start_timer = QTimer(self)
        self._start_timer.setSingleShot(True)
        self._start_timer.timeout.connect(self._start_stream)

        app = QCoreApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.close)
        self._start_timer.start(0)

    def _start_stream(self):
        if self._closed or self._failed or self._worker is not None:
            return
        if sys.platform != "darwin":
            self._fail("MediaRemote is only available on macOS")
            return
        try:
            # Optional platform dependency: importing this module starts nothing.
            from macos_mediaremote import MediaRemote

            self._client = MediaRemote(timeout=self.CONTROL_TIMEOUT_SECONDS,
                                       initialization_timeout=self.STARTUP_TIMEOUT_MS / 1000,
                                       max_output_bytes=self.MAX_BUFFER_BYTES)
            self._worker = _MediaRemoteStream(self._client, self._payload_received.emit,
                                              self._stream_failed.emit)
            self.destroyed.connect(self._worker.stop)
            self._worker.start()
        except Exception as error:
            self._fail(f"Cannot start macos-mediaremote-python: {error}")

    @pyqtSlot(object, float, float)
    def _receive_payload(self, data, captured_at, epoch_now):
        try:
            self._accept_payload(data, captured_at, epoch_now)
        except (ValueError, TypeError, KeyError, OverflowError):
            self._fail("MediaRemote returned an invalid event")

    @pyqtSlot(str)
    def _fail(self, reason):
        if self._closed or self._failed:
            return
        self._failed = True
        self._disconnect()
        logger.warning("%s; using Spotify API fallback", reason)
        if self._worker is not None:
            self._worker.stop()
        # Do not endlessly relaunch a helper rejected by the OS. A healthy stream
        # stays subscribed through Spotify exits/restarts without polling.

    @staticmethod
    def _number(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Invalid MediaRemote number")
        return number

    def _accept_payload(self, data, captured_at, epoch_now):
        if self._closed or self._failed:
            return
        if data.get("bundleIdentifier") != self.TARGET_ID or data.get("isAdvertisement"):
            self._disconnect()
            return
        # Metadata can arrive in stages. Wait for LrcPlayer's timing fields.
        if (not data.get("title") or data.get("durationMicros") is None or
                data.get("elapsedTimeMicros") is None or not isinstance(data.get("playing"), bool)):
            self._disconnect()
            return
        duration = max(0, round(self._number(data["durationMicros"]) / 1000))
        position = max(0, self._number(data["elapsedTimeMicros"]) / 1000)
        playing = data["playing"]
        rate = max(0, self._number(data.get("playbackRate", 1))) if playing else 0
        timestamp = data.get("timestampEpochMicros")
        if timestamp is not None:
            age = max(0, epoch_now - self._number(timestamp) / 1000000)
            position += age * 1000 * rate
        position = min(duration, round(position))
        pid = int(data.get("processIdentifier") or 0)
        properties = MediaPropertiesInfo(
            title=data["title"], artist=data.get("artist") or "",
            albumTitle=data.get("album") or "", albumArtist="",
            trackNumber=int(data.get("trackNumber") or 0),
        )
        if not all(isinstance(value, str) for value in properties[:4]):
            raise ValueError("Invalid MediaRemote metadata")
        # Spotify regenerates contentItemIdentifier even on pause/seek. It is a
        # system content item ID, not a stable Spotify track ID.
        identity = (pid, properties.title, properties.artist, properties.albumTitle)
        previous = self._snapshot
        source_timing = (data["elapsedTimeMicros"], timestamp)
        if (not playing and previous is not None and previous.identity == identity and
                previous.source_timing == source_timing):
            # A pause notification may precede the updated position/timestamp.
            # Freeze the interpolated position instead of jumping to an old sample.
            position = self._position_at(previous, captured_at)
        current = _Snapshot(identity, pid, properties,
                            MediaPlaybackInfo(4 if playing else 5, duration, position),
                            captured_at, rate, source_timing)
        self._snapshot = current
        track_changed = previous is None or previous.identity != current.identity
        properties_changed = track_changed or previous.properties != current.properties
        state_changed = previous is None or previous.playback.playStatus != current.playback.playStatus
        timeline_changed = previous is None or (
            abs(position - self._position_at(previous, captured_at)) > self.SEEK_THRESHOLD_MS or
            previous.playback.duration != duration or previous.rate != rate
        )

        if properties_changed:
            self.media_properties_changed.emit(properties)
        if track_changed or state_changed:
            self.playback_info_changed.emit(current.playback)
        if track_changed or state_changed or timeline_changed:
            self.timeline_properties_changed.emit(current.playback)

    def _disconnect(self):
        previous = self._snapshot
        self._snapshot = None
        if previous is not None and not self._closed:
            position = self._position_at(previous, time.monotonic())
            self.playback_info_changed.emit(previous.playback._replace(playStatus=5, position=position))
            self.disconnected.emit()

    @staticmethod
    def _position_at(snapshot, now):
        position = snapshot.playback.position
        position += max(0, round((now - snapshot.captured_at) * 1000 * snapshot.rate))
        return min(position, snapshot.playback.duration)

    def get_current_media_properties(self, session=None) -> MediaPropertiesInfo:
        snapshot = self._snapshot
        return snapshot.properties if snapshot else MediaPropertiesInfo("", "", "", "", 0)

    def get_current_playback_info(self, session=None) -> MediaPlaybackInfo:
        snapshot = self._snapshot
        if snapshot is None:
            return MediaPlaybackInfo(5, 0, 0)
        return snapshot.playback._replace(position=self._position_at(snapshot, time.monotonic()))

    def is_connected(self) -> bool:
        return not self._closed and not self._failed and self._snapshot is not None

    def connect_spotify(self) -> bool:
        """The subscription reconnects when Spotify becomes the system player."""
        return self.is_connected()

    def _control(self, operation, value) -> bool:
        snapshot = self._snapshot
        client = self._client
        if not self.is_connected() or snapshot is None or snapshot.pid <= 0 or client is None:
            return False

        async def dispatch():
            # The package controls global Now Playing. Recheck the owner, but
            # this is not an atomic session lock and cannot eliminate all races.
            current = await client.get()
            if (not self.is_connected() or current is None or
                    current.bundle_identifier != self.TARGET_ID or
                    current.raw.get("processIdentifier") != snapshot.pid):
                return False
            if operation == "seek":
                await client.seek(value)
            else:
                await getattr(client, operation)()
            return True

        try:
            return asyncio.run(dispatch())
        except Exception:
            logger.warning("MediaRemote control failed or timed out", exc_info=True)
            return False

    def pause_media(self) -> bool:
        return self._control("pause", None)

    def play_media(self) -> bool:
        return self._control("play", None)

    def skip_next_media(self) -> bool:
        return self._control("next_track", None)

    def skip_previous_media(self) -> bool:
        return self._control("previous_track", None)

    def play_pause_media(self) -> bool:
        return self._control("toggle_play_pause", None)

    def seek_to_position_media(self, position) -> bool:
        """Accept milliseconds; the PyPI client's public seek uses seconds."""
        try:
            position = self._number(position)
        except (ValueError, TypeError, OverflowError):
            return False
        if position < 0 or position * 1000 > 2**63 - 1:
            return False
        return self._control("seek", position / 1000)

    def playback_info_changed_connect(self, func):
        self.playback_info_changed.connect(func)

    def media_properties_changed_connect(self, func):
        self.media_properties_changed.connect(func)

    def timeline_properties_changed_connect(self, func):
        self.timeline_properties_changed.connect(func)

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._snapshot = None
        self._start_timer.stop()
        if self._worker is not None:
            self._worker.stop()
            if self._worker.ident is not None:
                self._worker.join(timeout=3)
                if self._worker.is_alive():
                    logger.warning("MediaRemote subscription is still shutting down")
