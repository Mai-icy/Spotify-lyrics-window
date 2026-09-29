# Build via: python build/macos/build.py
import os
from pathlib import Path
import platform
import sys
import sysconfig

from PyInstaller.utils.hooks import collect_data_files, copy_metadata, get_package_paths


if sys.platform != 'darwin':
    raise SystemExit('This spec must be built on macOS')

root = Path(SPECPATH).resolve().parents[1]
source = root / 'SpotifyLyricWindow'
version = os.environ.get('SLW_BUNDLE_VERSION', '1.12.0')
icon = os.environ['SLW_BUNDLE_ICON']
# Qt 6.11 requires macOS 13+. Python may require a newer OS (e.g. Homebrew).
# https://doc.qt.io/qt-6/supported-platforms.html
python_target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET') or '13.0'
minimum_os = max('13.0', python_target, key=lambda value: tuple(map(int, value.split('.'))))

# Whitelist read-only resources. Never collect local settings, tokens, logs or downloads.
datas = [(str(source / 'resource' / name), f'resource/{name}')
         for name in ('data', 'html', 'i18n', 'ui/settings')]
datas += [(str(source / 'resource/ui/lightstyle.qss'), 'resource/ui'),
          (str(root / 'LICENSE'), 'licenses'), (str(root / 'licenses'), 'licenses')]
datas += collect_data_files('macos_mediaremote', includes=['_native/**'],
                            excludes=['**/_CodeSignature/**', '**/MediaRemoteAdapter.framework/**'])
datas += copy_metadata('macos-mediaremote-python')
native = Path(get_package_paths('macos_mediaremote')[1]) / '_native/MediaRemoteAdapter.framework'
native_destination = 'macos_mediaremote/_native/MediaRemoteAdapter.framework'
datas += [(str(native / 'Resources/Info.plist'), f'{native_destination}/Resources')]

a = Analysis(
    [str(source / 'main.py')],
    pathex=[str(source)],
    binaries=[(str(native / 'MediaRemoteAdapter'), native_destination)],
    datas=datas,
    hiddenimports=['pynput.keyboard._darwin', 'pynput.mouse._darwin', 'macos_mediaremote'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['common.media_session.win_session', 'common.media_session.linux_session',
              'winrt', 'dbus', 'gi', 'tkinter', 'PyQt5', 'PySide2', 'PySide6'],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='SpotifyLyricsWindow',
    console=False,
    argv_emulation=False,
    target_arch=platform.machine(),
    codesign_identity=None,
)
coll = COLLECT(exe, a.binaries, a.datas, name='SpotifyLyricsWindow')
app = BUNDLE(
    coll,
    name='Spotify Lyrics Window.app',
    icon=icon,
    version=version,
    bundle_identifier='io.github.mai-icy.spotify-lyrics-window',
    info_plist={
        'CFBundleDisplayName': 'Spotify Lyrics Window',
        'CFBundleVersion': version,
        'CFBundleShortVersionString': version,
        'LSMinimumSystemVersion': minimum_os if '.' in minimum_os else minimum_os + '.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'NSAppleEventsUsageDescription': 'Read Spotify playback progress to keep desktop lyrics in sync.',
    },
)
