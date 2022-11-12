#!/usr/bin/python
# -*- coding:utf-8 -*-
from math import ceil

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.lyric_window_view.raw_ui.LyricsWindow import Ui_LyricsWindow
from components.lyric_window_view.text_scroll_area import TextScrollArea


class LyricsWindowView(QWidget, Ui_LyricsWindow):
    set_timer_status_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(LyricsWindowView, self).__init__(parent)
        self.setupUi(self)
        self.installEventFilter(self)  # 初始化事件过滤器

        # 界面相关
        self._init_window_shadow()
        self._init_main_window()
        self._init_font()

        # 功能效果相关
        self._init_window_lock_flag()
        self._init_window_drag_flag()
        self._init_mouse_track()
        self._init_roll()

        self.set_button_hide(True)

    def _init_window_shadow(self):
        effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        effect_shadow.setOffset(0, 0)  # 偏移
        effect_shadow.setBlurRadius(10)  # 阴影半径
        effect_shadow.setColor(QtCore.Qt.gray)  # 阴影颜色
        self.background_frame.setGraphicsEffect(effect_shadow)

    def _init_main_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.above_scrollArea = TextScrollArea(self.lyrics_frame1)
        self.lyrics_gridLayout1.addWidget(self.above_scrollArea)

        self.below_scrollArea = TextScrollArea(self.lyrics_frame2)
        self.lyrics_gridLayout2.addWidget(self.below_scrollArea)

        self.set_label_rgb()

    def _init_font(self):
        self.font = QtGui.QFont()
        self.font.setFamily("微软雅黑")
        self.font.setPixelSize(int((self.height() - 30) / 2.7))
        self.above_scrollArea.set_font(self.font)
        self.below_scrollArea.set_font(self.font)

    def _init_window_drag_flag(self):
        self._clicked = False
        self._drag = False
        self._drag_left = False
        self._drag_up = False
        self._drag_right = False
        self._drag_down = False
        self._drag_left_up = False
        self._drag_left_down = False
        self._drag_right_up = False
        self._drag_right_down = False
        self._is_move = False

    def _init_mouse_track(self):
        self.setMouseTracking(True)
        self.background_frame.setMouseTracking(True)
        self.lyrics_frame1.setMouseTracking(True)
        self.lyrics_frame2.setMouseTracking(True)
        self.above_scrollArea.set_mouse_track()
        self.below_scrollArea.set_mouse_track()
        self.buttons_frame.setMouseTracking(True)

    def _init_signal(self):
        self.close_button.clicked.connect(self.close)
        self.lock_button.clicked.connect(self.lock_event)
        self.set_timer_status_signal.connect(lambda flag: self.timer.start() if flag else self.timer.stop())

    def _init_window_lock_flag(self):
        self._is_locked = False
        self._time_count_out = 0
        self._time_count_in = 0

    def _init_roll(self):
        self.time_step = 20  # 刷新时间间隔
        self.move_step = 1  # 步长
        self.roll_time = 0
        self.roll_time_rate = 0.7
        self.begin_index = 0

        self._time_count_in = 0
        self._time_count_out = 0

        self.timer = QTimer()
        self.timer.setInterval(self.time_step)
        self.timer.timeout.connect(self.update_index_timer_event)
        self.timer.start()

    def set_label_rgb(self, r=86, g=152, b=195):
        stylesheet = f"color:rgb({r}, {g}, {b})"
        self.above_scrollArea.set_label_stylesheet(stylesheet)
        self.below_scrollArea.set_label_stylesheet(stylesheet)

    def set_transparent(self, flag):
        self.set_button_hide(flag)
        style_hide_sheet = "*{border:none;}"
        style_show_sheet = "*{border:none;}#background_frame{background-color: rgba(0,0,0,0.2);}"

        now_sheet = style_hide_sheet if flag else style_show_sheet
        self.setStyleSheet(now_sheet)

    def set_button_hide(self, flag):
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

    def set_cursor_icon(self, cursor):
        # 设置光标图标
        # self.setCursor(cursor)
        # self.background_frame.setCursor(cursor)
        self.buttons_frame.setCursor(cursor)
        self.above_scrollArea.setCursor(cursor)
        self.below_scrollArea.setCursor(cursor)

    def set_pause_button_icon(self, flag):
        if flag:
            self.pause_button.setIcon(QtGui.QIcon(u":/pic/images/pause.png"))
        else:
            self.pause_button.setIcon(QtGui.QIcon(u":/pic/images/continue.png"))

    def set_rolling(self, flag):
        if (flag and not self.timer.isActive()) or (not flag and self.timer.isActive()):
            self.set_timer_status_signal.emit(flag)

    def set_text(self, rows, text, roll_time):
        width = self._get_text_width(text)
        self.roll_time = roll_time
        if rows == 1:
            self.above_scrollArea.set_text(text, width)
        if rows == 2:
            self.below_scrollArea.set_text(text, width)

        def get_move_step(width_t):
            if not roll_time:
                return 0
            return ceil(2 * (self.time_step * (width_t - self.width())) / (roll_time * self.roll_time_rate))

        if self.above_scrollArea.text_width > self.below_scrollArea.text_width:
            self.move_step = get_move_step(self.above_scrollArea.text_width)
        else:
            self.move_step = get_move_step(self.below_scrollArea.text_width)
        self.begin_index = (0.5 * (1 - self.roll_time_rate) * self.roll_time) // self.time_step

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

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，扳机复位
        self._init_window_drag_flag()

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if not self._is_locked:
            if event.button() == Qt.LeftButton:
                self._clicked = True
                self.move_DragPosition = event.globalPos() - self.pos()
                event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 重写鼠标移动的事件
        self._time_count_in = 0
        pos = QMouseEvent.pos()  # QMouseEvent.pos()获取相对位置
        width = self.width()
        height = self.height()

        if not self._drag:
            # 右下
            if width - 10 <= pos.x() <= width + 10 and height - 10 <= pos.y() <= height + 10:
                self.set_cursor_icon(Qt.SizeFDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_right_down = True
            # 左上
            elif -10 <= pos.x() <= 10 and -10 <= pos.y() <= 10:
                self.set_cursor_icon(Qt.SizeFDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_left_up = True
            # 下
            elif 10 <= pos.x() <= width - 10 and height - 10 <= pos.y() <= height + 10:
                self.set_cursor_icon(Qt.SizeVerCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_down = True
            # 上
            elif 10 <= pos.x() <= width - 10 and -10 <= pos.y() <= 10:
                self.set_cursor_icon(Qt.SizeVerCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_up = True
            # 右
            elif width - 10 <= pos.x() <= width + 10 and 10 <= pos.y() <= height - 10:
                self.set_cursor_icon(Qt.SizeHorCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_right = True
            # 左
            elif -10 <= pos.x() <= 10 and 10 <= pos.y() <= height - 10:
                self.set_cursor_icon(Qt.SizeHorCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_left = True
            # 左下
            elif -10 <= pos.x() <= 10 and height - 10 <= pos.y() <= height + 10:
                self.set_cursor_icon(Qt.SizeBDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_left_down = True
            # 右上
            elif width - 10 <= pos.x() <= width + 10 and -10 <= pos.y() <= 10:
                self.set_cursor_icon(Qt.SizeBDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_right_up = True
            # 中间
            else:  # 10 <= pos.x() <= width - 10 and 10 <= pos.y() <= height - 10:
                if self._is_locked:
                    self.set_cursor_icon(Qt.ArrowCursor)
                else:
                    self.set_cursor_icon(Qt.SizeAllCursor)
                if self._clicked and not self._drag:
                    self._is_move = True
                    self.move(QMouseEvent.globalPos() - self.move_DragPosition)

        if not self._is_move:
            # 右下
            if self._drag_right_down:
                self.resize(pos.x(), pos.y())
            # 左上
            elif self._drag_left_up:
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
            elif self._drag_down:
                self.resize(self.width(), pos.y())
            # 上
            elif self._drag_up:
                if not ((self.height() == self.minimumHeight() and pos.y() > 0)
                        or (self.height() == self.maximumHeight() and pos.y() < 0)):
                    self.setGeometry(
                        self.geometry().x(),
                        self.geometry().y() + pos.y(),
                        self.width(),
                        self.height() - pos.y())
            # 右
            elif self._drag_right:
                self.resize(pos.x(), self.height())
            # 左
            elif self._drag_left:
                if not (self.width() == self.minimumWidth() and pos.x() > 0):
                    self.setGeometry(
                        self.geometry().x() + pos.x(),
                        self.geometry().y(),
                        self.width() - pos.x(),
                        self.height())
            # 左下
            elif self._drag_left_down:
                if not (self.width() == self.minimumWidth() and pos.x() > 0):
                    self.setGeometry(
                        self.geometry().x() + pos.x(),
                        self.geometry().y(),
                        self.width() - pos.x(),
                        pos.y())
            # 右上
            elif self._drag_right_up:
                if not ((self.height() == self.minimumHeight() and pos.y() > 0)
                        or (self.height() == self.maximumHeight() and pos.y() < 0)):
                    self.setGeometry(
                        self.geometry().x(),
                        self.geometry().y() + pos.y(),
                        pos.x(),
                        self.height() - pos.y())

        # 更改字体大小
        self._init_font()

        # 判断缩放后是否开启滚动并更改文本label大小
        self.above_scrollArea.resize_label(self._get_text_width(self.above_scrollArea.text))
        self.below_scrollArea.resize_label(self._get_text_width(self.below_scrollArea.text))

        QMouseEvent.accept()

    def show(self) -> None:
        self.setGeometry(500, 900, self.width(), self.height())
        super(LyricsWindowView, self).show()

    def update_index_timer_event(self):
        self.above_scrollArea.update_index(self.begin_index, self.move_step)
        self.below_scrollArea.update_index(self.begin_index, self.move_step)
        self._time_count_in += 1
        self._time_count_out += 1
        if self._is_locked:
            if self._time_count_in * self.time_step >= 500:
                self.lock_button.setHidden(True)
                self.calibrate_button.setHidden(True)
            elif self._time_count_out * self.time_step >= 1000:
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
