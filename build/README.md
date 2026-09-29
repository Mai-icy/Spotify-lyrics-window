# 桌面打包

按平台放置构建配置，先实现 `macos/`；Windows / Linux 后续分别添加，不能在 macOS 上交叉打包。
构建中间文件在 `build/.work/`，成品在 `dist/`，都不提交到 Git。`build/` 本身是源码目录，不要整体删除。

## macOS 本地测试包

使用 Python 3.11+ 的独立虚拟环境，在仓库根目录执行：

```sh
python -m pip install -r requirements.txt -r build/macos/requirements.txt
python build/macos/build.py --version 1.12.0
```

脚本使用当前 Python 环境及其架构，生成应用图标，调用 PyInstaller，再验证本地 ad-hoc 签名。
重复构建会替换相同架构下的旧构建产物；不会清理源码或应用的用户数据。版本参数只设置包元数据，不创建 Git tag。

Apple Silicon 产物：`dist/macos/arm64/Spotify Lyrics Window.app`。
Intel 需在 x86_64 Python 和依赖环境下单独构建，产物在 `dist/macos/x86_64/`；当前不生成 universal2。
分发或移动时使用整个 `.app`，不要单独复制其中的可执行文件或符号链接。

### 打包内容和系统要求

- 采用 onedir `.app`，包含 Python、PyQt6、样式、翻译、静态数据、应用图标及项目许可证。
- 收集 PyPI `macos-mediaremote-python` 的原生 framework、Perl 脚本、上游许可证和包元数据；不重新下载第三方仓库。
- MediaRemote 仍按需导入，原生 helper 使用系统 `/usr/bin/perl`，进度辅助使用系统 `/usr/bin/osascript`。
- 图标从现有 `LyricsIcon.png` 自动转换；应用默认隐藏 Dock 图标，通过菜单栏图标操作。
- Qt 6.11 的最低要求为 macOS 13；实际产物还受 Python 和其他原生依赖限制。Info.plist 记录 Qt 与 Python 构建目标中的较高值，不代表所有旧系统已验证。
- 本机 Homebrew Python 3.14 的构建目标为 macOS 26，因此本机测试包至少需要 macOS 26。要支持更旧的系统，需换用支持目标系统的 Python / 依赖环境并实机验证，不能只降低 Info.plist 的版本号。

### 用户数据与权限

macOS **打包版**将用户数据放在：

```text
~/Library/Application Support/Spotify Lyrics Window/
├─ resource/       # setting.toml、token、lyric_token、error.log
└─ download/
   ├─ lyrics/      # 默认歌词及索引
   └─ temp/        # 默认缓存
```

自定义歌词和缓存目录继续有效；只读资源仍从应用包加载。源码运行的路径以及 Windows/Linux 行为不变。
不会把开发机的配置、凭据、日志或下载文件打进包，也不会自动迁移源码版的数据。
首次启动需重新配置账号；如需复用旧数据，请退出两个版本后自行迁移，并检查配置中的路径。

快捷键默认关闭且无绑定。启用时为打包后的应用授予辅助功能和输入监控权限；Spotify 进度辅助可能另需自动化授权。
源码启动时给终端/Python 的授权不保证适用于 `.app`，重建 ad-hoc 签名也可能需要重新授权。

### 本地包不等于正式发布包

当前只做 ad-hoc 签名，没有 Apple Developer ID 签名、公证、DMG 或自动更新。
下载到其他机器后可能被 Gatekeeper 拦截；不要要求用户全局关闭系统安全检查。
正式发布前还需补充 Developer ID 签名、自动化相关 entitlement、公证与 stapling、依赖许可证审查，以及目标系统回归。

本地验证重点：首次启动、中文/英文与明暗主题、设置开关、资源加载、下载和缓存写入、MediaRemote helper、Spotify 自动化授权、快捷键、关闭重开及覆盖安装后的数据保留。
构建成功或签名验证通过，不等于这些交互全部通过。

参考：[PyInstaller macOS 签名与事件处理](https://pyinstaller.org/en/stable/feature-notes.html#macos-binary-code-signing)、[打包资源路径](https://pyinstaller.org/en/stable/runtime-information.html)、[Qt 支持平台](https://doc.qt.io/qt-6/supported-platforms.html)。
