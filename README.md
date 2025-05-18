# Spotify-lyrics-window

## 📄Introduce 介绍

**scrolling lyrics window of spotify**
spotify 歌词滚动窗口

## 🤔Features 特性

- Lyric Api from Kugou, NetEase CloudMusic and Spotify. 歌词来源于网易云酷狗以及Spotify

- Operable control to play songs. 可以操控播放

- Lyrics automatically play scroll as well as switch. 自动根据音乐切换歌词以及滚动

- You can customize the font and color of the lyrics. 歌词支持多种样式

- You can manage and download lyric 你可以自己管理下载和编辑歌词

## 💿How to use 使用

1. Get your own spotify client id and secret from [spotify developer](https://developer.spotify.com/dashboard/). 从spotify开发者面板获取您的app id和密码
2. Create a developer app and edit its setting. 打开新创建的应用并且编辑设置
3. add ```http://127.0.0.1:8888/callback``` to your **Redirect URIs** setting. 将该网址加入此设置项
4. Run the program and open setting page. Put your client_id and client_secret in it. 运行程序并打开设置窗口输入您获取到的app id以及密码
5. Click the user icon in the window to complete the authorization. 点击窗口的用户图标完成授权
6. click the sure and enjoy it! 😋 按下确定，然后试试！


## ⚠️ notice 注意
 - if you need proxy, fill your `proxy_ip` in the `resource/setting.toml` such as `http:127.0.0.1:2333`, only spotify through the proxy. 如果需要代理，请在`resource/setting.toml`中填写代理ip，只有spotify会使用代理。
 - sp_dc requires you to get and fill in the `resource/setting.toml` yourself. 如果需要获取spotify的歌词，需要手动填入sp_dc在配置文件中
 - The spotify api has instability biases that this project uses to connect to MediaSession. spotify api有不稳定偏差，本项目使用连接MediaSession来解决

## 🎼 example 用例

Play the lyrics 播放歌词

![1](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example1.gif)

Customize the style of the lyrics 自定义歌词的风格

![2](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example2.gif)

Manage and download Lyrics 管理和下载歌词

![3](https://github.com/Mai-icy/Spotify-lyrics-window/blob/main/image-folder/gif_example3.gif)

## 📝 TODO

- [x] basic function 基本功能
- [x] Use the palette to customize the colors 使用调色盘自定义颜色
- [x] Manually adjust the lyrics file  手动调整歌词文件
- [x] Download the lyrics file by api  手动下载歌词文件
- [x] Common settings page 设置常规页面
- [x] Lyrics displayed vertically 竖向歌词显示
- [x] Beautify the window 美化窗口
- [x] More lyric api 更多的歌词api
- [x] update 更新至pyqt6以支持维护
- [x] support Linux 支持 linux
- [ ] Use qfluentwidget
- [ ] etc.
