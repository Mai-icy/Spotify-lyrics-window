# Spotify Lyrics Window 🎵

A desktop floating lyrics window for Spotify with real-time scrolling lyrics, playback controls, local lyric management, and customizable styles.

[简体中文](./README.md)

## 👀 Preview

Real-time lyrics while music is playing:

![Play lyrics](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example1.gif)

Customize lyric styles:

![Customize style](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example2.gif)

Manage and download local lyrics:

![Manage lyrics](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example3.gif)

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
- Translation display support
- Horizontal and vertical lyric layouts
- Custom fonts, colors, shadows, and window styles
- Global hotkey support
- Windows and Linux media session support

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
├─ components/    # reusable widgets, dialogs, threads, raw UI wrappers
├─ view/          # lyric window and settings pages
├─ resource/      # ui resources, images, qss, html
└─ main.py        # application entry
```

## 🛠️ Requirements

- Python 3.10+
- A Spotify account
- Spotify Desktop app, or an active Spotify playback session
- A Spotify Developer application

## 📦 Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
4. Add this Redirect URI in your Spotify app settings:

```text
http://127.0.0.1:8888/callback
```

## 🚀 Usage

1. Start the application:

```bash
cd SpotifyLyricWindow
python main.py
```

2. Open the settings window
3. Fill in your `client_id` and `client_secret`
4. Click the account button to finish Spotify authorization
5. Start playing music in Spotify
6. Enjoy the floating lyrics window

## ⚙️ Configuration Notes

- If you need a proxy, set `proxy_ip` in `SpotifyLyricWindow/resource/setting.toml`
- If you need Spotify lyric-related features that rely on `sp_dc`, fill it manually in the config file
- Lyric directory and temporary directory paths can be customized in the config

## 🌟 Current Project Strengths

- It is a complete desktop app rather than a simple script
- It covers both lyric display and lyric management workflows
- It integrates playback control and media session handling
- It already has a solid base for further productization

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
- [ ] Better English localization
- [ ] More modern UI and settings experience
- [ ] Better packaging and release workflow
- [ ] More robust error handling and diagnostics
- [ ] Automated tests and CI

## 🔧 Suggested Next Steps

If you plan to continue evolving this project, these areas are especially valuable:

- Refactor thread and synchronization logic for better stability
- Improve token storage and configuration safety
- Upgrade the settings UX and first-run onboarding
- Add tests for lyric parsing, config loading, and source matching
- Provide more complete Windows release packages and release notes

## 📄 License

This project is licensed under [GPL-3.0](./LICENSE).
