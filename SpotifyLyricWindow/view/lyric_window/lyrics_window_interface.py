#!/usr/bin/python
# -*- coding:utf-8 -*-
from system_hotkey import SystemHotkey

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui import Ui_VerticalLyricsWindow, Ui_HorizontalLyricsWindow
from components.scroll_area.text_scroll_area import TextScrollArea
from common.typing import DisplayMode
from common.config import Config


class LyricsWindowInterface(QWidget, Ui_HorizontalLyricsWindow, Ui_VerticalLyricsWindow):
    set_timer_status_signal = pyqtSignal(bool)

    setting_window_show_signal = pyqtSignal()
    lyric_window_show_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(LyricsWindowInterface, self).__init__(parent)
        # 获取设置中的歌词显示模式（竖向或者横向）
        self.display_mode = DisplayMode(Config.LyricConfig.display_mode)
        if self.display_mode == DisplayMode.Horizontal:
            super(LyricsWindowInterface, self).setupUi(self)  # 会运行 HorizontalLyricsWindow 的 setupUi
        else:
            super(Ui_HorizontalLyricsWindow, self).setupUi(self)  # 会运行 VerticalLyricsWindow 的 setupUi

        self.installEventFilter(self)  # 初始化事件过滤器

        # 界面相关
        self._init_lyrics_shadow()
        self._init_main_window()
        self._init_scroll_area()
        self._init_color_rgb()
        self._init_font()

        # 功能效果相关
        self._init_window_lock_flag()
        self._init_window_drag_flag()
        self._init_mouse_track()
        self._init_hotkey()

    def _re_init(self):
        """重新初始化布局"""
        super(LyricsWindowInterface, self).__init__(self.parent())

        self.display_mode = DisplayMode(Config.LyricConfig.display_mode)
        if self.display_mode == DisplayMode.Horizontal:
            super(LyricsWindowInterface, self).setupUi(self)  # 会运行 HorizontalLyricsWindow 的 setupUi
        else:
            super(Ui_HorizontalLyricsWindow, self).setupUi(self)  # 会运行 VerticalLyricsWindow 的 setupUi

        self.installEventFilter(self)  # 初始化事件过滤器

        self._init_lyrics_shadow()
        self._init_main_window()
        self._init_scroll_area()
        self._init_color_rgb()
        self._init_font()
        self._init_mouse_track()

    def _init_lyrics_shadow(self):
        """初始化歌词阴影"""
        self.effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(0, 0)  # 偏移
        self.effect_shadow.setBlurRadius(10)  # 阴影半径
        # self.effect_shadow.setColor(QtCore.Qt.gray)  # 阴影颜色
        self.background_frame.setGraphicsEffect(self.effect_shadow)

    def _init_main_window(self):
        """初始化界面控件以及属性"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SplashScreen)
        self.set_always_front(Config.LyricConfig.is_always_front)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.set_button_hide(True)

    def _init_scroll_area(self):
        """初始化滚动区域"""
        self.above_scrollArea = TextScrollArea(self.lyrics_frame1)
        self.lyrics_gridLayout1.addWidget(self.above_scrollArea)

        self.below_scrollArea = TextScrollArea(self.lyrics_frame2)
        self.lyrics_gridLayout2.addWidget(self.below_scrollArea)

    def _init_color_rgb(self):
        """初始化 歌词 以及 阴影 颜色"""
        # 导入配置
        if Config.LyricConfig.rgb_style != "other":
            self.set_rgb_style(Config.LyricConfig.rgb_style)
        else:
            self.set_lyrics_rgb(Config.LyricConfig.lyric_color)
            self.set_shadow_rgb(Config.LyricConfig.shadow_color)

    def _init_font(self):
        """初始化字体 字体类型 以及 大小"""
        # 导入配置
        family = Config.LyricConfig.font_family
        height = Config.CommonConfig.PositionConfig.height
        width = Config.CommonConfig.PositionConfig.width

        self.font = QtGui.QFont()
        self.font.setFamily(family)
        if self.display_mode == DisplayMode.Horizontal:
            self.font.setPixelSize(int((height - 30) / 3))
        else:
            self.font.setPixelSize(int((width - 45) / 3))
        self.above_scrollArea.setFont(self.font)
        self.below_scrollArea.setFont(self.font)

    def _init_window_drag_flag(self):
        """拖动相关变量初始化"""
        self._clicked = False

        self.x_index = self.y_index = -1
        # 在各个方向的 Qt.CursorShape
        self._drag_cursor = [
            (Qt.SizeFDiagCursor, Qt.SizeVerCursor, Qt.SizeBDiagCursor),
            (Qt.SizeHorCursor, Qt.SizeAllCursor, Qt.SizeHorCursor),
            (Qt.SizeBDiagCursor, Qt.SizeVerCursor, Qt.SizeFDiagCursor)
        ]

        self.move_DragPosition = 0

    def _init_mouse_track(self):
        """设置鼠标跟踪"""
        self.setMouseTracking(True)
        self.background_frame.setMouseTracking(True)
        self.lyrics_frame1.setMouseTracking(True)
        self.lyrics_frame2.setMouseTracking(True)
        self.above_scrollArea.setMouseTracking(True)
        self.below_scrollArea.setMouseTracking(True)
        self.buttons_frame.setMouseTracking(True)

    def _init_signal(self):
        """初始化基本信号连接"""
        self.lock_button.clicked.connect(self._lock_event)
        self.set_timer_status_signal.connect(self._set_timer_status_signal_event)

    def _init_window_lock_flag(self):
        """初始化锁定相关变量"""
        self._time_step = 20  # 刷新时间间隔

        self._is_locked = False
        self._time_count_out = 0
        self._time_count_in = 0

        self.timer = QTimer()
        self.timer.setInterval(self._time_step)
        self.timer.timeout.connect(self._update_index_timer_event)
        self.timer.start()

    def _init_hotkey(self):
        """初始化快捷键"""
        self.hotkey = SystemHotkey()

        self.signal_dic = {
            "calibrate_button": self.calibrate_button.clicked,
            "lock_button": self.lock_button.clicked,
            "close_button": self.close_button.clicked,
            "translate_button": self.translate_button.clicked,
            "next_button": self.next_button.clicked,
            "last_button": self.last_button.clicked,
            "pause_button": self.pause_button.clicked,
            "show_window": self.lyric_window_show_signal
        }
        # 导入配置
        # self.set_hotkey_enable(True)

    def set_display_mode(self, mode: DisplayMode):
        """
        NOT AVAILABLE
        设置显示 竖直 还是 水平

        :param mode: 设置显示的模式
        """
        if mode == self.display_mode:
            return

        Config.LyricConfig.display_mode = mode.value
        if mode == DisplayMode.Horizontal:
            default_pos = Config.get_default_dict()["CommonConfig"]["PositionConfig"]
        else:
            default_pos = {
                "pos_x": 1200,
                "pos_y": 200,
                "width": 150,
                "height": 700
            }

        self.hide()
        Config.CommonConfig.PositionConfig.pos_x = default_pos["pos_x"]
        Config.CommonConfig.PositionConfig.pos_y = default_pos["pos_y"]
        Config.CommonConfig.PositionConfig.width = default_pos["width"]
        Config.CommonConfig.PositionConfig.height = default_pos["height"]
        self._re_init()  # 重新初始化
        self.show()

    def set_hotkey_enable(self, flag: bool):
        """
        设置全局快捷键是否打开

        :param flag: 是否 打开
        """
        for key in self.signal_dic.keys():
            hotkeys = getattr(Config.HotkeyConfig, key)
            if hotkeys and hotkeys != "null":
                if flag and Config.HotkeyConfig.is_enable:
                    self.hotkey.register(hotkeys,
                                         callback=self.get_emit_func(self.signal_dic[key]))
                else:
                    self.hotkey.unregister(hotkeys)

    def set_signal_hotkey(self, signal_key: str, hotkeys: tuple):
        """
        设置绑定 快捷键 以触发 对应信号

        :param signal_key: 代表对应信号的键  请使用self.signal_dic内的key
        :param hotkeys: 对应快捷键 例如 ("alt", "r")
        """
        # 解除旧的绑定
        old_hotkey = getattr(Config.HotkeyConfig, signal_key)
        if old_hotkey:
            self.hotkey.unregister(old_hotkey)

        # 进行新的的绑定
        if hotkeys:
            self.hotkey.register(hotkeys, callback=self.get_emit_func(self.signal_dic[signal_key]))

        # 同步到配置
        setattr(Config.HotkeyConfig, signal_key, hotkeys)

    def set_lyrics_rgb(self, rgb: tuple):
        """
        为歌词设置颜色

        :param rgb: 对应的rgb颜色值 例如 (237, 178, 209)
        """
        stylesheet = f"color:rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
        self.above_scrollArea.set_label_stylesheet(stylesheet)
        self.below_scrollArea.set_label_stylesheet(stylesheet)
        # 同步到配置
        Config.LyricConfig.lyric_color = rgb

    def set_shadow_rgb(self, rgb: tuple):
        """
        为歌词阴影设置颜色

        :param rgb: 对应的rgb颜色值 例如 (114, 514, 191)
        """
        color = QColor(*rgb)
        self.effect_shadow.setColor(color)
        # 同步到配置
        Config.LyricConfig.shadow_color = rgb

    def set_rgb_style(self, color: str):
        """
        使用预设的 9 种颜色方案。会同时设置歌词颜色以及歌词阴影颜色

        :param color: 仅能为 "blue", "red", "violet", "green", "orange", "yellow", "brown", "cyan", "pink" 其中之一
        """
        style_dict = {
            # color   lyrics_color    shadow_color
            "blue": ((86, 152, 195), (120, 120, 120)),
            "red": ((255, 77, 109), (120, 120, 120)),
            "violet": ((153, 111, 214), (120, 120, 120)),
            "green": ((152, 201, 163), (150, 150, 150)),
            "orange": ((255, 119, 61), (120, 120, 120)),
            "yellow": ((255, 225, 80), (150, 150, 150)),
            "brown": ((176, 137, 104), (150, 150, 150)),
            "cyan": ((61, 204, 199), (120, 120, 120)),
            "pink": ((237, 178, 209), (120, 120, 120))
        }
        self.set_lyrics_rgb(style_dict[color][0])
        self.set_shadow_rgb(style_dict[color][1])

        Config.LyricConfig.rgb_style = color

    def set_font_family(self, family: str):
        """
        设置歌词字体

        :param family: 必须为原有配套字体 例如 “微软雅黑”
        """
        self.font.setFamily(family)
        self.above_scrollArea.setFont(self.font)
        self.below_scrollArea.setFont(self.font)

    def set_font_size(self, size: int, *, resize_window: bool = False):
        """
        设置字体大小，一般根据窗口高度自动调整

        :param size: 字体大小
        :param resize_window: 是否由字体大小反向设置窗口大小
        """
        self.font.setPixelSize(size)
        self.above_scrollArea.setFont(self.font)
        self.below_scrollArea.setFont(self.font)
        if resize_window:
            height = int(size * 3 + 30)
            self.resize(self.width(), height)

    def set_button_hide(self, flag: bool):
        """
        设置隐藏按钮

        :param flag: True 为隐藏
        """
        self.close_button.setHidden(flag)
        self.last_button.setHidden(flag)
        self.lock_button.setHidden(flag)
        self.account_button.setHidden(flag)
        self.next_button.setHidden(flag)
        self.offsetdown_button.setHidden(flag)
        self.offsetup_button.setHidden(flag)
        self.pause_button.setHidden(flag)
        self.settings_button.setHidden(flag)
        self.calibrate_button.setHidden(flag)
        self.translate_button.setHidden(flag)

    def set_transparent(self, flag: bool):
        """
        设置半透明背景是否可见

        :param flag: True 为隐藏
        """
        self.set_button_hide(flag)
        style_hide_sheet = "*{border:none;}"
        style_show_sheet = "*{border:none;}#background_frame{background-color: rgba(0,0,0,0.2);}"

        now_sheet = style_hide_sheet if flag else style_show_sheet
        self.setStyleSheet(now_sheet)

    def set_cursor_icon(self, cursor: Qt.CursorShape):
        """
        设置光标图标

        :param cursor: Qt.CursorShape类型
        """
        # self.setCursor(cursor)
        # self.background_frame.setCursor(cursor)
        self.buttons_frame.setCursor(cursor)
        self.above_scrollArea.setCursor(cursor)
        self.below_scrollArea.setCursor(cursor)

    def set_pause_button_icon(self, flag: bool):
        """
        设置暂停按钮图标

        :param flag: True 为暂停图标
        """
        icon = "pause.png" if flag else "continue.png"
        self.pause_button.setIcon(QtGui.QIcon(f":/pic/images/{icon}"))

    def set_lyrics_rolling(self, flag: bool):
        """
        设置歌词是否 可滚动

        :param flag: True 为 可滚动
        """
        if (flag and not self.timer.isActive()) or (not flag and self.timer.isActive()):
            self.set_timer_status_signal.emit(flag)

    def set_lyrics_text(self, rows: int, text: str, roll_time: int = 0):
        """
        设置歌词文本

        :param rows: 1 为上行歌词， 2为下面歌词
        :param text: 需要显示文本
        :param roll_time: 滚动时间
        """
        if rows == 1:
            self.above_scrollArea.set_text(text)
            self.above_scrollArea.set_roll_time(roll_time)
            self.update()
        if rows == 2:
            self.below_scrollArea.set_text(text)
            self.below_scrollArea.set_roll_time(roll_time)

    def set_always_front(self, flag: bool):
        """
        设置窗口是否在最上层

        :param flag: True 为 在最上层
        """
        if not self.isHidden():
            self.hide()
            if flag:
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()
        else:
            if flag:
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

    def enterEvent(self, event: QEvent):
        """定义鼠标移入事件,显示按钮,设置半透明背景"""
        if not self._is_locked:
            self.set_transparent(False)
            event.accept()

    def leaveEvent(self, event: QEvent):
        """定义鼠标移出事件,隐藏按钮,设置背景透明"""
        self._time_count_out = 0
        if not self._is_locked:
            self.set_transparent(True)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放后，扳机复位"""
        self._init_window_drag_flag()

    def mousePressEvent(self, event: QMouseEvent):
        """重写鼠标点击的事件"""
        if not self._is_locked and event.button() == Qt.LeftButton:
            self._clicked = True
            self.move_DragPosition = event.globalPos() - self.pos()  # 开始拖动 鼠标相对窗口的位置
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """关于 窗口拖动 以及 窗口拉伸"""
        self._time_count_in = 0
        pos = event.pos()  # QMouseEvent.pos()获取相对位置

        if not self._clicked:
            self._update_pos_index(pos)
            if self.y_index == self.x_index == 1 and self._is_locked:
                self.set_cursor_icon(Qt.ArrowCursor)
            if not self._is_locked:
                self.set_cursor_icon(self._drag_cursor[self.y_index][self.x_index])

        if self._clicked:
            if self.x_index == self.y_index == 1:  # 中间 (1, 1)
                # 拖动窗口 不改变大小
                if self.move_DragPosition:
                    self.move(event.globalPos() - self.move_DragPosition)
            elif self.x_index + self.y_index >= 3:  # 右下角 或者 下 或者 右 [(2, 2), (1, 2), (2, 1)]
                # x_index为2 代表宽度(右边)被拖动  y_index为2 代表高度(下边)被拖动。 如果被拖动，使用光标的值
                height = pos.y() if self.y_index == 2 else self.height()
                width_ = pos.x() if self.x_index == 2 else self.width()
                self.resize(width_, height)
            else:  # 左上角 或者 上 或者 左 或者 右上角 或者 左下角[(0, 0), (1, 0), (0, 1), (2, 0), (0, 2)]
                # 由于Qt特性 窗口扩大只支持右下方，故涉及 左 以及 上 的拖动需要先设置位置，再设置大小
                if self.x_index == 0:  # 左端被拉动
                    # 如果下端被拉动，则使用光标的y坐标 即(0, 2)
                    new_geometry_y = pos.y() if self.y_index == 2 else self.height()

                    if not (self.width() == self.minimumWidth() and pos.x() > 0):
                        self.setGeometry(
                            self.geometry().x() + pos.x(),
                            self.geometry().y(),
                            self.width() - pos.x(),
                            new_geometry_y)

                if self.y_index == 0:  # 上端被拉动
                    # 如果右端被拉动，则使用光标的y坐标 即(2, 0)
                    new_geometry_x = pos.x() if self.x_index == 2 else self.width()

                    if not ((self.height() == self.minimumHeight() and pos.y() > 0)
                            or (self.height() == self.maximumHeight() and pos.y() < 0)):
                        self.setGeometry(
                            self.geometry().x(),
                            self.geometry().y() + pos.y(),
                            new_geometry_x,
                            self.height() - pos.y())

            # 更改字体大小
            if self.display_mode == DisplayMode.Horizontal:
                self.set_font_size(int((self.height() - 30) / 3))
            else:
                self.set_font_size(int((self.width() - 45) / 3))

        event.accept()

    def show(self):
        """从隐藏状态到显示状态"""
        if self.isVisible():
            return
        pos_config = Config.CommonConfig.PositionConfig
        self.setGeometry(pos_config.pos_x, pos_config.pos_y, pos_config.width, pos_config.height)
        super(LyricsWindowInterface, self).show()

    def hide(self):
        """从显示状态到隐藏状态"""
        self._renew_pos_config()
        return super(LyricsWindowInterface, self).hide()

    def close(self):
        """结束程序"""
        self._renew_pos_config()
        Config.save_config()
        return super(LyricsWindowInterface, self).close()

    def _set_timer_status_signal_event(self, flag):
        if flag:
            self.timer.start()
        else:
            self.timer.stop()

    def _renew_pos_config(self):
        """同步配置文件 关于窗口的位置 以至下次打开在原来位置"""
        if Config.CommonConfig.is_save_position:
            Config.CommonConfig.PositionConfig.pos_x = self.pos().x()
            Config.CommonConfig.PositionConfig.pos_y = self.pos().y()
            Config.CommonConfig.PositionConfig.width = self.width()
            Config.CommonConfig.PositionConfig.height = self.height()

    def _update_index_timer_event(self):
        """更新timer状态"""
        self._time_count_in += 1
        self._time_count_out += 1
        if self._is_locked:
            if self._time_count_in * self._time_step >= 500:
                self.lock_button.setHidden(True)
                self.calibrate_button.setHidden(True)
            elif self._time_count_out * self._time_step >= 1000:
                self.lock_button.setHidden(False)
                self.calibrate_button.setHidden(False)

    def _update_pos_index(self, pos: QPoint):
        """
        更新鼠标关于窗口的位置区间 以供判断 拉伸状况 同步到 x_index 以及 y_index
         x_index--> 0           1              2
      y_index 0   左上拉|        上拉伸         |右上拉
         |       ------------------------------------
         v            |                      |
              1  左拉伸|        拖动           |右拉伸
                      |                      |
                 ------------------------------------
              2  左下拉|        下拉伸         |右下拉
        """
        # index  n/a  0   1                  2                n/a
        x_list = (-10, 10, self.width() - 10, self.width() + 10)
        y_list = (-10, 10, self.height() - 10, self.height() + 10)

        x = pos.x()
        y = pos.y()

        for i in range(3):
            if x_list[i] < x:
                self.x_index = i

        for i in range(3):
            if y_list[i] < y:
                self.y_index = i

    def _lock_event(self):
        """上锁按钮事件"""
        if self._is_locked:
            self._is_locked = False
            self.lock_button.setIcon(QtGui.QIcon(u":/pic/images/lock.png"))
            self.set_transparent(False)
        else:
            self._is_locked = True
            self.lock_button.setIcon(QtGui.QIcon(u":/pic/images/lockopen.png"))
            self.set_transparent(True)
            self.lock_button.setHidden(False)
            self.calibrate_button.setHidden(False)

    @staticmethod
    def get_emit_func(signal):
        """返回对应信号触发函数，lambda函数因引用问题不使用"""

        def emit_func(_):
            signal.emit()

        return emit_func
