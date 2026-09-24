# Spotify Lyrics Window 🎵

A desktop floating lyrics window for Spotify with real-time scrolling lyrics, playback controls, local lyric management, and customizable styles.

[简体中文](./README.md)

## 👀 Preview

Recorded from the current UI on macOS using English and original demo lyrics, without a live playback session. The download demo uses offline source responses with the real search, selection, and local-save workflow. Switch between Simplified Chinese and English in settings; restart to apply.

Lyrics display: drag, enlarge, and shrink the window with automatic font scaling, scroll long lines, and switch between horizontal and Unicode-aware vertical layouts.

![Lyrics display: dragging, resizing, scrolling, and layout switching](./image-folder/gif_example1.gif)

Refreshed settings: sidebar navigation, shortcuts, fonts, and colors, with style changes reflected immediately in the lyrics window.

![Refreshed settings: navigation, fonts, and colors](./image-folder/gif_example2.gif)

Lyrics library: search and download lyrics for a missing entry, then save to clear its badge; search local tracks, edit lyrics, adjust timing, and view translations.

![Lyrics library: search, download, save, missing-lyrics badges, and editing](./image-folder/gif_example3.gif)

## 📖 Overview

`Spotify Lyrics Window` is a desktop lyric tool built with `PyQt6`. It aims to provide a more flexible and desktop-native lyric experience for Spotify users.

Instead of being a simple lyric display script, this project offers a more complete desktop workflow:

- Automatic lyric scrolling and song switching
- Playback control integration
- Multi-source lyric matching and downloading
- Local lyric cache and lyric management
- Customizable window style, fonts, colors, and hotkeys

## ✨ Features

- Floating desktop lyrics window for Spotify
- Automatic lyric scrolling and track switching
- Playback control support: play, pause, previous, next
- Multiple lyric sources: Kugou, NetEase Cloud Music, and Spotify
- Local lyric cache and lyric file management
- Local search, missing-lyrics badges, editing, and per-track timing offsets
- Translation display support
- Horizontal and vertical lyric layouts
- Unicode-aware vertical orientation, preserving combining accents and emoji sequences
- Custom fonts, colors, shadows, and window styles
- Global hotkey support
- Automatic track sync correction toggle, plus global and per-track lyric offsets
- Sidebar-based settings with Simplified Chinese and English interfaces
- Windows, Linux, and macOS (Spotify Desktop) media session support

## 💡 Why This Project

Spotify on desktop still leaves room for a better lyric experience:

- You do not need to switch back to the main player just to read lyrics
- A floating lyrics window fits desktop multitasking much better
- Multiple lyric sources improve matching success and fallback reliability
- Local lyric management makes the experience more controllable and stable
- Customization makes the tool more comfortable for long-term daily use

## 🧱 Project Structure

```text
SpotifyLyricWindow/
├─ common/        # config, lyric logic, api clients, media session, player
│  ├─ macos/      # macOS window and hotkey adapters
│  └─ ui/         # fonts, localization, vertical orientation data
├─ components/    # reusable widgets, dialogs, threads, raw UI wrappers
├─ view/          # lyric window and settings pages
├─ resource/      # ui resources, images, qss, html
└─ main.py        # application entry
```

The tree shows the main runtime modules. Maintenance scripts live in [tools/](./tools/), tests in [tests/](./tests/), and platform development notes in [docs/](./docs/).

## 🛠️ Requirements

- Python 3.10+ on Windows/Linux, or 3.11+ on macOS; 3.11+ is recommended, and CI currently uses Python 3.11
- A graphical desktop: Windows 10/11, Linux, or macOS; Linux Wayland sessions currently run through XWayland / Qt xcb
- A local Spotify Desktop client for system media session integration; other playback devices rely on the Spotify API path and may not offer the same experience
- A Spotify account and a usable Spotify Developer application for authorization, metadata lookup, and API fallback

## 📦 Installation

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Mai-icy/Spotify-lyrics-window.git
cd Spotify-lyrics-window
python -m venv .venv
```

2. Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies from the repository root. Platform markers select the platform-specific packages automatically:

```bash
python -m pip install -r requirements.txt
```

4. Create or select an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and register the redirect URI used by the code:

```text
http://127.0.0.1:8888/callback
```

Do not replace the IP address with `localhost`; Spotify requires an explicit loopback IP. See [Redirect URIs](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri). Local port 8888 must be available during authorization.

Development mode is not available to every account without additional setup: the app owner currently needs Premium, and other users must be allowlisted. Consult [Spotify's development mode documentation](https://developer.spotify.com/documentation/web-api/concepts/quota-modes) for account eligibility and quotas.

## 🚀 Usage

1. Start the application:

```bash
cd SpotifyLyricWindow
python main.py
```

2. Open settings from the lyrics window or the system tray / macOS menu bar menu
3. Under General → Spotify connection, enter `client_id` and `client_secret`, then click Apply credentials
4. Click the account button to finish Spotify authorization
5. Start playing music in Spotify
6. Enjoy the floating lyrics window

### Platform Support and Limitations

| Platform | Media session implementation | Notes |
| --- | --- | --- |
| Windows | WinRT system media sessions | Platform dependencies install automatically |
| Linux | QtDBus / MPRIS | Requires a desktop session bus and Spotify's MPRIS service |
| macOS | MediaRemote / Now Playing | Matches Spotify Desktop only; uses private API |

macOS automatically installs the pinned [macos-mediaremote-python](https://pypi.org/project/macos-mediaremote-python/0.1.0a1/) package, whose wheel includes Intel / Apple Silicon native resources without a local CMake build. It is imported on demand when initializing the macOS media session; Windows/Linux neither install nor import it. Background events reach the main thread through Qt signals.

The dependency is currently alpha, and private APIs can break after system updates. An unavailable backend uses the existing Spotify API fallback, so account configuration is still required. See the [macOS development notes](./docs/macos.md) for native resources, threading, and control limitations.

- macOS hides the Dock icon by default. Use the menu bar icon to show lyrics, open settings, or quit. The topmost panel supports all-Spaces and fullscreen-auxiliary behavior, but coverage over every fullscreen app or Stage Manager scenario is not guaranteed. Lyrics-window shadows are disabled on macOS to avoid dark glyph borders.
- Global shortcuts have platform restrictions: macOS may require Accessibility permission for the launching terminal / Python application, and Wayland input monitoring is limited by XWayland. See [pynput's platform limitations](https://pynput.readthedocs.io/en/latest/limitations.html).
- Vertical layout uses Unicode 17.0 default orientations and permitted fallbacks while preserving character clusters. Font-specific vertical glyph substitutions are not implemented, and missing font glyphs cannot be supplied by orientation rules.

## ⚙️ Configuration Notes

Settings are saved to `SpotifyLyricWindow/resource/setting.toml` when the settings window closes; the file is created on first launch. Quit the app before editing it manually to avoid having your edits overwritten by the running settings.

- **General**: language, close behavior, window position, global lyric offset, and lyric / cache folders. Language and folder changes require a restart.
- **Automatic track sync correction**: enabled by default. After an automatic track change, it waits about 0.7 seconds and seeks both playback and lyrics back to the beginning. Disabling it avoids that reset but may cause timing drift; it does not run on every manual track change.
- **Appearance and shortcuts**: orientation, always-on-top, separate original / translation fonts, colors, and global shortcuts. Unavailable Windows fonts fall back to installed fonts on macOS.
- **Lyrics library**: search, download, edit, export, delete, and per-track offset. Global and per-track offsets use seconds; positive values advance the lyrics.
- **Separate proxies**: under **General → Network proxies**, enter HTTP/HTTPS proxies for Spotify API, NetEase Cloud Music, and Kugou (for example, `http://127.0.0.1:7890`), then click **Apply proxies**. Changes affect subsequent requests without restarting or entering Spotify app credentials. Leave blank to use default networking, which may include system or environment proxies. The corresponding keys under `[CommonConfig.ClientConfig]` are `spotify_proxy_ip`, `cloudmusic_proxy_ip`, and `kugou_proxy_ip`.
- **Spotify lyrics credentials**: fill in `sp_dc` in the same section when using that lyric source. It serves a different purpose from `client_id` / `client_secret` and can expire. Source availability depends on the network and upstream services; not every song has downloadable lyrics.

Do not publish `client_secret`, `sp_dc`, or login data in `resource/token` and `resource/lyric_token`. When reporting an issue, include a redacted `SpotifyLyricWindow/resource/error.log` and your OS / Python versions.

## 🧪 Development and Testing

After installing runtime dependencies, run from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Committed tests cover configuration, lyric matching and downloading, file management, playback logic, and authorization. [CI](./.github/workflows/ci.yml) currently runs on Windows/macOS with Python 3.11. These tests do not connect to live Spotify or establish full desktop coverage for shortcuts, always-on-top behavior, and media sessions. Use an isolated clone and test configuration to avoid initializing or modifying everyday data.

## 🗺️ Roadmap

- [x] Basic lyric window and playback flow
- [x] Color customization
- [x] Manual lyric adjustment
- [x] Lyric download via API
- [x] Settings pages
- [x] Vertical lyric mode
- [x] Better window styling
- [x] Multiple lyric APIs
- [x] PyQt6 upgrade
- [x] Linux support
- [x] macOS media session and window support
- [x] Simplified Chinese and English interfaces
- [x] Modern UI and settings experience
- [x] Unicode vertical orientation and character-cluster handling
- [x] Automatic track sync toggle, separate proxies, and missing-lyrics badges
- [x] Automated tests and CI (Windows / macOS)
- [ ] Improve Windows / Linux / macOS packaging, native resource collection, and releases
- [ ] Add regression coverage for rapid track changes, overlapping calibrations, session reconnection, and download failures
- [ ] Improve error messages, diagnostics, and login credential storage
- [ ] Improve first-run onboarding and add more interface languages
- [ ] Linux CI and broader cross-platform desktop regression coverage

## 📄 License

This project is licensed under [GPL-3.0](./LICENSE).

Vertical orientation data is derived from Unicode and includes the [Unicode data license](./licenses/UNICODE-LICENSE.txt).
