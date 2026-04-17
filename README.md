# Spotify Lyrics Window 🎵

一个面向 Spotify 的桌面悬浮歌词窗口，支持实时滚动歌词、播放控制、本地歌词管理与样式自定义。

[English README](./README.en.md)

## 👀 项目预览

播放时实时显示歌词：

![Play lyrics](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example1.gif)

自定义歌词样式：

![Customize style](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example2.gif)

管理和下载本地歌词：

![Manage lyrics](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example3.gif)

## 📖 项目简介

`Spotify Lyrics Window` 是一个基于 `PyQt6` 的桌面歌词工具，目标是为 Spotify 提供更自由、更接近桌面原生体验的悬浮歌词窗口。

相比只展示歌词的简单脚本，这个项目提供了更完整的桌面使用体验：

- 播放时自动切歌与滚动
- 播放控制联动
- 多歌词源匹配与下载
- 本地歌词缓存与管理
- 支持窗口样式、字体、颜色、快捷键等自定义

## ✨ 功能亮点

- Spotify 桌面悬浮歌词窗口
- 歌词自动滚动与自动切换
- 支持播放、暂停、上一首、下一首
- 多歌词来源：酷狗、网易云、Spotify
- 本地歌词缓存与歌词文件管理
- 支持翻译歌词显示
- 横向 / 纵向歌词显示模式
- 支持字体、颜色、阴影、窗口样式自定义
- 支持全局快捷键
- 支持 Windows 与 Linux 媒体会话

## 💡 为什么做这个项目

Spotify 在桌面端的歌词体验仍然有不少可以改进的地方，这个项目主要希望解决这些问题：

- 听歌时不需要频繁切回主播放器看歌词
- 浮窗歌词更适合边工作边听歌的桌面场景
- 多歌词源可以提高歌词匹配成功率
- 本地歌词管理可以让歌词体验更稳定、可控
- 自定义能力更适合长期使用

## 🧱 项目结构

```text
SpotifyLyricWindow/
├─ common/        # 配置、歌词逻辑、API 客户端、媒体会话、播放器
├─ components/    # 可复用组件、对话框、线程、UI 包装
├─ view/          # 歌词窗口与设置页面
├─ resource/      # UI 资源、图片、QSS、HTML
└─ main.py        # 程序入口
```

## 🛠️ 运行环境

- Python 3.10 及以上
- Spotify 账号
- Spotify Desktop 客户端，或当前有活跃的 Spotify 播放会话
- 一个 Spotify Developer 应用

## 📦 安装步骤

1. 克隆仓库
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 前往 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) 创建应用
4. 在应用设置中添加以下回调地址：

```text
http://127.0.0.1:8888/callback
```

## 🚀 使用方法

1. 启动程序：

```bash
cd SpotifyLyricWindow
python main.py
```

2. 打开设置窗口
3. 填入 `client_id` 和 `client_secret`
4. 点击账号按钮完成 Spotify 授权
5. 在 Spotify 中开始播放音乐
6. 享受悬浮歌词体验

## ⚙️ 配置说明

- 如果需要代理，可在 `SpotifyLyricWindow/resource/setting.toml` 中设置 `spotify_proxy_ip`
- 如果需要依赖 `sp_dc` 的 Spotify 歌词能力，需要手动在配置文件中填写
- 歌词目录、临时目录等路径支持在配置中自定义

## 🌟 当前项目特点

- 不是简单脚本，而是完整的桌面应用形态
- 除了歌词显示，也覆盖了歌词下载与管理流程
- 集成了播放控制与媒体会话能力
- 已具备继续演进为正式桌面工具的基础

## 🗺️ 路线图

- [x] 基础歌词窗口与播放联动
- [x] 颜色自定义
- [x] 手动调整歌词
- [x] 通过 API 下载歌词
- [x] 设置页面
- [x] 纵向歌词显示
- [x] 窗口样式优化
- [x] 多歌词 API 支持
- [x] 升级到 PyQt6
- [x] 支持 Linux
- [ ] 更完整的英文本地化
- [ ] 更现代的 UI 与设置体验
- [ ] 更完善的打包与发布流程
- [ ] 更稳健的错误处理与诊断信息
- [ ] 自动化测试与 CI

## 🔧 后续改进建议

如果你打算继续更新这个项目，比较值得优先投入的方向有：

- 重构线程与同步逻辑，提升稳定性
- 改进 token 存储和配置安全性
- 优化设置页与首次使用引导
- 为歌词解析、配置读写、歌词匹配补充测试
- 提供更完整的 Windows 发布包和版本说明

## 📄 许可证

本项目基于 [GPL-3.0](./LICENSE) 开源。
