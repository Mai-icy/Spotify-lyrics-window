"""Build a local, ad-hoc signed macOS app with the current Python environment."""
import argparse
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='1.12.0', help='Bundle version (default: 1.12.0)')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        parser.error('macOS packaging must run on macOS')
    if not re.fullmatch(r'\d+\.\d+\.\d+', args.version):
        parser.error('--version must use major.minor.patch, for example 1.12.0')

    root = Path(__file__).resolve().parents[2]
    arch = platform.machine()
    work = root / 'build' / '.work' / 'macos' / arch
    dist = root / 'dist' / 'macos' / arch
    iconset = work / 'LyricsIcon.iconset'
    iconset.mkdir(parents=True, exist_ok=True)
    source_icon = root / 'SpotifyLyricWindow/resource/ui/images/LyricsIcon.png'
    for size in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            suffix = '@2x' if scale == 2 else ''
            pixels = str(size * scale)
            subprocess.run(['/usr/bin/sips', '-z', pixels, pixels, str(source_icon),
                            '--out', str(iconset / f'icon_{size}x{size}{suffix}.png')],
                           check=True, stdout=subprocess.DEVNULL)
    icon = work / 'LyricsIcon.icns'
    subprocess.run(['/usr/bin/iconutil', '-c', 'icns', str(iconset), '-o', str(icon)], check=True)

    env = dict(os.environ, SLW_BUNDLE_VERSION=args.version, SLW_BUNDLE_ICON=str(icon))
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm',
                    '--workpath', str(work / 'pyinstaller'), '--distpath', str(dist),
                    str(root / 'build/macos/SpotifyLyricsWindow.spec')], cwd=root, env=env, check=True)
    app = dist / 'Spotify Lyrics Window.app'
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(app)], check=True)
    print(f'Built: {app}\nLocal ad-hoc signature only; not notarized for distribution.')


if __name__ == '__main__':
    main()
