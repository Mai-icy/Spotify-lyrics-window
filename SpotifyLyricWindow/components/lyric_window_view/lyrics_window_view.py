#!/usr/bin/python
# -*- coding:utf-8 -*-
from math import ceil
from system_hotkey import SystemHotkey

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from common.config import Config
from components.lyric_window_view.raw_ui.LyricsWindow import Ui_LyricsWindow
from components.lyric_window_view.text_scroll_area import TextScrollArea
from components.lyric_window_view.lyric_tray_icon import LyricsTrayIcon


class LyricsWindowView(QWidget, Ui_LyricsWindow):
    set_timer_status_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(LyricsWindowView, self).__init__(parent)
        self.setupUi(self)
        self.installEventFilter(self)  # 初始化事件过滤器
        self.tray_icon = LyricsTrayIcon(self)

        # 界面相关
        self._init_window_shadow()
        self._init_main_window()
        self._init_font()

        # 功能效果相关
        self._init_window_lock_flag()
        self._init_window_drag_flag()
        self._init_mouse_track()
        self._init_roll()
        self._init_hotkey()

        self.set_button_hide(True)

    def _init_window_shadow(self):
        self.effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(0, 0)  # 偏移
        self.effect_shadow.setBlurRadius(10)  # 阴影半径
        # self.effect_shadow.setColor(QtCore.Qt.gray)  # 阴影颜色
        self.background_frame.setGraphicsEffect(self.effect_shadow)

    def _init_main_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.above_scrollArea = TextScrollArea(self.lyrics_frame1)
        self.lyrics_gridLayout1.addWidget(self.above_scrollArea)

        self.below_scrollArea = TextScrollArea(self.lyrics_frame2)
        self.lyrics_gridLayout2.addWidget(self.below_scrollArea)

        if Config.LyricConfig.rgb_style:
            self.set_rgb_style(Config.LyricConfig.rgb_style)
        else:
            self.set_lyrics_rgb(Config.LyricConfig.lyric_color)
            self.set_shadow_rgb(Config.LyricConfig.shadow_color)

    def _init_font(self):
        family = Config.LyricConfig.font_family
        height = Config.CommonConfig.height

        self.font = QtGui.QFont()
        self.font.setFamily(family)
        self.font.setPixelSize(int((height - 30) / 3))
        self.above_scrollArea.set_font(self.font)
        self.below_scrollArea.set_font(self.font)

    def _init_window_drag_flag(self):
        self._clicked = False

        self.x_index = self.y_index = -1
        self._drag_cursor = [
            (Qt.SizeFDiagCursor, Qt.SizeVerCursor, Qt.SizeBDiagCursor),
            (Qt.SizeHorCursor,   Qt.SizeAllCursor, Qt.SizeHorCursor),
            (Qt.SizeBDiagCursor, Qt.SizeVerCursor, Qt.SizeFDiagCursor)
        ]

        self.move_DragPosition = 0
        self.pos_x_list = []

    def _init_mouse_track(self):
        self.setMouseTracking(True)
        self.background_frame.setMouseTracking(True)
        self.lyrics_frame1.setMouseTracking(True)
        self.lyrics_frame2.setMouseTracking(True)
        self.above_scrollArea.set_mouse_track()
        self.below_scrollArea.set_mouse_track()
        self.buttons_frame.setMouseTracking(True)

    def _init_signal(self):
        self.close_button.clicked.connect(self.hide)
        self.lock_button.clicked.connect(self.lock_event)
        self.set_timer_status_signal.connect(lambda flag: self.timer.start() if flag else self.timer.stop())

    def _init_window_lock_flag(self):
        self._is_locked = False
        self._time_count_out = 0
        self._time_count_in = 0

    def _init_roll(self):
        self._time_step = 20  # 刷新时间间隔
        self._move_step = 1  # 步长
        self._roll_time = 0
        self._roll_time_rate = 0.7
        self._begin_index = 0

        self._time_count_in = 0
        self._time_count_out = 0

        self.timer = QTimer()
        self.timer.setInterval(self._time_step)
        self.timer.timeout.connect(self.update_index_timer_event)
        self.timer.start()

    def _init_hotkey(self):
        self.hotkey = SystemHotkey()

        self.signal_dic = {
            "calibrate_button": self.calibrate_button.clicked,
            "lock_button": self.lock_button.clicked,
            "close_button": self.close_button.clicked,
            "translate_button": self.translate_button.clicked
        }

        if Config.HotkeyConfig.is_enable:
            for key in self.signal_dic.keys():
                hotkeys = getattr(Config.HotkeyConfig, key)
                if hotkeys:
                    self.hotkey.register(hotkeys,
                                         callback=self.get_emit_func(self.signal_dic[key]))

    def set_signal_hotkey(self, signal_key, hotkeys: tuple):
        old_hotkey = getattr(Config.HotkeyConfig, signal_key)
        setattr(Config.HotkeyConfig, signal_key, hotkeys)
        if old_hotkey:
            self.hotkey.unregister(old_hotkey)

        if hotkeys:
            self.hotkey.register(hotkeys, callback=self.get_emit_func(self.signal_dic[signal_key]))

    def set_lyrics_rgb(self, rgb: tuple):
        stylesheet = f"color:rgb{rgb}"
        self.above_scrollArea.set_label_stylesheet(stylesheet)
        self.below_scrollArea.set_label_stylesheet(stylesheet)

        Config.LyricConfig.lyric_color = rgb

    def set_shadow_rgb(self, rgb: tuple):
        color = QColor(*rgb)
        self.effect_shadow.setColor(color)

        Config.LyricConfig.shadow_color = rgb

    def set_rgb_style(self, color: str):
        style_dict = {
            # color   lyrics_color    shadow_color
            "blue": ((86, 152, 195), (190, 190, 190)),
            "red": ((255, 77, 109), (150, 150, 150)),
            "violet": ((153, 111, 214), (150, 150, 150)),
            "green": ((152, 201, 163), (190, 190, 190)),
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
        self.font.setFamily(family)
        self.above_scrollArea.set_font(self.font)
        self.below_scrollArea.set_font(self.font)

    def set_font_size(self, size: int, *, resize_window: bool = False):
        self.font.setPixelSize(size)
        self.above_scrollArea.set_font(self.font)
        self.below_scrollArea.set_font(self.font)
        if resize_window:
            height = int(size * 3 + 30)
            self.resize(self.width(), height)

    def set_button_hide(self, flag: bool):
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
        self.set_button_hide(flag)
        style_hide_sheet = "*{border:none;}"
        style_show_sheet = "*{border:none;}#background_frame{background-color: rgba(0,0,0,0.2);}"

        now_sheet = style_hide_sheet if flag else style_show_sheet
        self.setStyleSheet(now_sheet)

    def set_cursor_icon(self, cursor: QCursor):
        # 设置光标图标
        # self.setCursor(cursor)
        # self.background_frame.setCursor(cursor)
        self.buttons_frame.setCursor(cursor)
        self.above_scrollArea.setCursor(cursor)
        self.below_scrollArea.setCursor(cursor)

    def set_pause_button_icon(self, flag: bool):
        if flag:
            self.pause_button.setIcon(QtGui.QIcon(u":/pic/images/pause.png"))
        else:
            self.pause_button.setIcon(QtGui.QIcon(u":/pic/images/continue.png"))

    def set_rolling(self, flag: bool):
        if (flag and not self.timer.isActive()) or (not flag and self.timer.isActive()):
            self.set_timer_status_signal.emit(flag)

    def set_lyrics_text(self, rows: int, text: str, *, roll_time: int = 0):
        width = self._get_text_width(text)
        self._roll_time = roll_time

        if rows == 1:
            self.above_scrollArea.set_text(text, width)
            self.update()
        if rows == 2:
            self.below_scrollArea.set_text(text, width)

        max_width = max(self.above_scrollArea.text_width, self.below_scrollArea.text_width)
        self._move_step = ceil(2 * (self._time_step * (max_width - self.width()))
                               / (roll_time * self._roll_time_rate)) if roll_time else 0
        self._begin_index = (0.5 * (1 - self._roll_time_rate) * self._roll_time) // self._time_step

    def _get_text_width(self, text):
        # 计算文本的总宽度
        song_font_metrics = QFontMetrics(self.font)
        return song_font_metrics.width(text)

    def enterEvent(self, event):
        # 定义鼠标移入事件,显示按钮,设置半透明背景
        if not self._is_locked:
            self.set_transparent(False)
            event.accept()

    def leaveEvent(self, event):
        # 定义鼠标移出事件,隐藏按钮,设置背景透明
        self._time_count_out = 0
        if not self._is_locked:
            self.set_transparent(True)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # 鼠标释放后，扳机复位
        self._init_window_drag_flag()

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if not self._is_locked:
            if event.button() == Qt.LeftButton:
                self._clicked = True
                self.move_DragPosition = event.globalPos() - self.pos()
                event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        # 重写鼠标移动的事件
        self._time_count_in = 0
        pos = event.pos()  # QMouseEvent.pos()获取相对位置
        width = self.width()
        height = self.height()

        if not self._clicked:
            x = pos.x()
            y = pos.y()

            #  index     0    1           2
            x_list = (-10, 10, width - 10,  width + 10)
            y_list = (-10, 10, height - 10, height + 10)

            for i in range(3):
                if x_list[i] < x:
                    self.x_index = i

            for i in range(3):
                if y_list[i] < y:
                    self.y_index = i

            if self.y_index == self.x_index == 1 and self._is_locked:
                self.set_cursor_icon(Qt.ArrowCursor)
            if not self._is_locked:
                self.set_cursor_icon(self._drag_cursor[self.y_index][self.x_index])

        if self._clicked:
            # 右下
            if self.y_index == self.x_index == 2:
                self.resize(pos.x(), pos.y())
            # 左上
            elif self.y_index == self.x_index == 0:
                if not ((self.height() == self.minimumHeight() and pos.y() > 0)
                        or (self.height() == self.maximumHeight() and pos.y() < 0)):
                    self.setGeometry(
                        self.geometry().x(),
                        self.geometry().y() + pos.y(),
                        self.width(),
                        self.height() - pos.y())
                if not (self.width() == self.minimumWidth() and pos.x() > 0):
                    self.setGeometry(
                        self.geometry().x() + pos.x(),
                        self.geometry().y(),
                        self.width() - pos.x(),
                        self.height())
            # 下
            elif self.x_index == 1 and self.y_index == 2:
                self.resize(self.width(), pos.y())
            # 上
            elif self.x_index == 1 and self.y_index == 0:
                if not ((self.height() == self.minimumHeight() and pos.y() > 0)
                        or (self.height() == self.maximumHeight() and pos.y() < 0)):
                    self.setGeometry(
                        self.geometry().x(),
                        self.geometry().y() + pos.y(),
                        self.width(),
                        self.height() - pos.y())
            # 右
            elif self.x_index == 2 and self.y_index == 1:
                self.resize(pos.x(), self.height())
            # 左
            elif self.x_index == 0 and self.y_index == 1:
                if not (self.width() == self.minimumWidth() and pos.x() > 0):
                    self.setGeometry(
                        self.geometry().x() + pos.x(),
                        self.geometry().y(),
                        self.width() - pos.x(),
                        self.height())
            # 左下
            elif self.x_index == 0 and self.y_index == 2:
                if not (self.width() == self.minimumWidth() and pos.x() > 0):
                    self.setGeometry(
                        self.geometry().x() + pos.x(),
                        self.geometry().y(),
                        self.width() - pos.x(),
                        pos.y())
            # 右上
            elif self.x_index == 2 and self.y_index == 0:
                if not ((self.height() == self.minimumHeight() and pos.y() > 0)
                        or (self.height() == self.maximumHeight() and pos.y() < 0)):
                    self.setGeometry(
                        self.geometry().x(),
                        self.geometry().y() + pos.y(),
                        pos.x(),
                        self.height() - pos.y())
            else:
                if self.move_DragPosition:
                    self.move(event.globalPos() - self.move_DragPosition)

            # 更改字体大小
            self.set_font_size(int((self.height() - 30) / 3))

        # 判断缩放后是否开启滚动并更改文本label大小
        self.above_scrollArea.resize_label(self._get_text_width(self.above_scrollArea.text))
        self.below_scrollArea.resize_label(self._get_text_width(self.below_scrollArea.text))

        event.accept()

    def show(self):
        pos_config = Config.CommonConfig
        self.setGeometry(pos_config.pos_x, pos_config.pos_y, pos_config.width, pos_config.height)
        self.tray_icon.show()
        super(LyricsWindowView, self).show()

    def hide(self):
        self.renew_pos_config()
        return super(LyricsWindowView, self).hide()

    def close(self):
        self.renew_pos_config()
        Config.save_config()
        return super(LyricsWindowView, self).close()

    def renew_pos_config(self):
        Config.CommonConfig.pos_x = self.pos().x()
        Config.CommonConfig.pos_y = self.pos().y()
        Config.CommonConfig.width = self.width()
        Config.CommonConfig.height = self.height()

    def update_index_timer_event(self):
        self.above_scrollArea.update_index(self._begin_index, self._move_step)
        self.below_scrollArea.update_index(self._begin_index, self._move_step)
        self._time_count_in += 1
        self._time_count_out += 1
        if self._is_locked:
            if self._time_count_in * self._time_step >= 500:
                self.lock_button.setHidden(True)
                self.calibrate_button.setHidden(True)
            elif self._time_count_out * self._time_step >= 1000:
                self.lock_button.setHidden(False)
                self.calibrate_button.setHidden(False)

    def lock_event(self):
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
        def emit_func(_):
            signal.emit()

        return emit_func
