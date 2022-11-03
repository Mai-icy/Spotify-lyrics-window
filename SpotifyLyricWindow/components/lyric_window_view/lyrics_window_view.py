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
    def __init__(self, parent=None):
        super(LyricsWindowView, self).__init__(parent)
        self.setupUi(self)
        self._init_main_window()  # 主窗口初始化设置
        self.installEventFilter(self)  # 初始化事件过滤器
        self._init_drag()
        self.set_button_hide(True)
        self.set_mouse_track()
        self.set_default_window_shadow()
        self._init_font()
        self._init_roll()
        self._is_play = False
        self._is_locked = False
        self.lock_button.clicked.connect(self.pause_button_clicked)
        

        self.set_text(1, "开发阶段", 0)
        self.set_text(2, "各功能还在陆续更新", 0)

    # 字体初始化设置
    def _init_font(self):
        self.font = QtGui.QFont()
        self.font.setFamily("微软雅黑")
        self.font.setPixelSize(int((self.height() - 30) / 2.7))
        self.text1_scrollarea.set_font(self.font)
        self.text2_scrollarea.set_font(self.font)

    # 主窗口初始化设置
    def _init_main_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.text1_scrollarea = TextScrollArea(self.lyrics_frame1)
        self.lyrics_gridLayout1.addWidget(self.text1_scrollarea)

        self.text2_scrollarea = TextScrollArea(self.lyrics_frame2)
        self.lyrics_gridLayout2.addWidget(self.text2_scrollarea)

        self.text1_scrollarea.set_label_stylesheet("color:rgb(86, 152, 195)")
        self.text2_scrollarea.set_label_stylesheet("color:rgb(86, 152, 195)")

    # 设置默认阴影
    def set_default_window_shadow(self):
        effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        # 偏移
        effect_shadow.setOffset(0, 0)
        # 阴影半径
        effect_shadow.setBlurRadius(10)
        # 阴影颜色
        effect_shadow.setColor(QtCore.Qt.gray)
        self.background_frame.setGraphicsEffect(effect_shadow)

    # 设置鼠标跟踪
    def set_mouse_track(self):
        self.setMouseTracking(True)
        self.background_frame.setMouseTracking(True)
        self.lyrics_frame1.setMouseTracking(True)
        self.lyrics_frame2.setMouseTracking(True)
        self.text1_scrollarea.set_mouse_track()
        self.text2_scrollarea.set_mouse_track()
        self.buttons_frame.setMouseTracking(True)

    # 定义鼠标移入事件,显示按钮,设置半透明背景
    def enterEvent(self, event):
        if not self._is_locked:
            self.set_transparent(False)
            event.accept()

    # 定义鼠标移出事件,隐藏按钮,设置背景透明
    def leaveEvent(self, event):
        self._time_count_out = 0
        if not self._is_locked:
            self.set_transparent(True)
            event.accept()

    # 设置窗口透明
    def set_transparent(self, flag):
        self.set_button_hide(flag)
        if flag:
            self.setStyleSheet("*\n"
                    "{\n"
                    "border:none;\n"
                    "}")
        else:
            self.setStyleSheet("*\n"
                    "{\n"
                    "border:none;\n"
                    "}"
                    "#background_frame\n"
                    "{\n"
                    "    background-color: rgba(0,0,0,0.2);\n"
                    "}")

    # 隐藏按钮
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

    # 初始化扳机
    def _init_drag(self):
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

    # 鼠标释放后，扳机复位
    def mouseReleaseEvent(self, QMouseEvent):

        self._init_drag()

    # 重写鼠标点击的事件
    def mousePressEvent(self, event):
        if not self._is_locked:
            if event.button() == Qt.LeftButton:
                self._clicked = True
                self.move_DragPosition = event.globalPos() - self.pos()
                event.accept()

    # 重写鼠标移动的事件
    def mouseMoveEvent(self, QMouseEvent):
        self._time_count_in = 0
        pos = QMouseEvent.pos() # QMouseEvent.pos()获取相对位置
        width = self.width()
        height = self.height()

        if not self._drag:
            # 右下
            if width - 10 <= pos.x() <= width + 10 and height - 10 <= pos.y() <= height + 10:
                self.set_all_cursor(Qt.SizeFDiagCursor)
                if self._clicked and not self._is_move:                
                    self._drag = True
                    self._drag_right_down = True
            # 左上
            elif -10 <= pos.x() <= 10 and -10 <= pos.y() <= 10:
                self.set_all_cursor(Qt.SizeFDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_left_up = True
            # 下
            elif 10 <= pos.x() <= width - 10 and height - 10 <= pos.y() <= height + 10:
                self.set_all_cursor(Qt.SizeVerCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_down = True
            # 上
            elif 10 <= pos.x() <= width - 10 and -10 <= pos.y() <= 10:
                self.set_all_cursor(Qt.SizeVerCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_up = True
            # 右
            elif width - 10 <= pos.x() <= width + 10 and 10 <= pos.y() <= height - 10:
                self.set_all_cursor(Qt.SizeHorCursor)
                if self._clicked and not self._is_move:                
                    self._drag = True
                    self._drag_right = True
            # 左
            elif -10 <= pos.x() <= 10 and 10 <= pos.y() <= height - 10:
                self.set_all_cursor(Qt.SizeHorCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_left = True
            # 左下
            elif -10 <= pos.x() <= 10 and height - 10 <= pos.y() <= height + 10:
                self.set_all_cursor(Qt.SizeBDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_left_down = True
            # 右上
            elif width -10 <= pos.x() <= width + 10 and -10 <= pos.y() <= 10:
                self.set_all_cursor(Qt.SizeBDiagCursor)
                if self._clicked and not self._is_move:
                    self._drag = True
                    self._drag_right_up = True
            # 中间
            #elif 10 <= pos.x() <= width - 10 and 10 <= pos.y() <= height - 10:
            else:
                if self._is_locked:
                    self.set_all_cursor(Qt.ArrowCursor)
                else:
                    self.set_all_cursor(Qt.SizeAllCursor)
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
        self.text1_scrollarea.resize_label(self.get_text_width(self.text1_scrollarea.text))
        self.text2_scrollarea.resize_label(self.get_text_width(self.text2_scrollarea.text))

        QMouseEvent.accept()

    # 设置光标
    def set_all_cursor(self, cursor):
        #self.setCursor(cursor)
        #self.background_frame.setCursor(cursor)
        self.buttons_frame.setCursor(cursor)
        self.text1_scrollarea.setCursor(cursor)
        self.text2_scrollarea.setCursor(cursor)

    # region 歌词滚动
    # 歌词滚动设置初始化
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
        self.timer.timeout.connect(self.update_index)
        self.timer.start()

    # 计算文本的总宽度
    def get_text_width(self, text):
        song_font_metrics = QFontMetrics(self.font)
        return song_font_metrics.width(text)

    # 设置歌词文本
    def set_text(self, rows, text, roll_time):
        width = self.get_text_width(text)
        self.roll_time = roll_time
        if rows == 1:
            self.text1_scrollarea.set_text(text, width)
        if rows == 2:
            self.text2_scrollarea.set_text(text, width)

        def get_move_step(width_t):
            if not roll_time:
                return 0
            return ceil(2 * (self.time_step * (width_t - self.width())) / (roll_time * self.roll_time_rate))

        if self.text1_scrollarea.text_width > self.text2_scrollarea.text_width:
            self.move_step = get_move_step(self.text1_scrollarea.text_width)
        else:
            self.move_step = get_move_step(self.text2_scrollarea.text_width)
        self.begin_index = (0.5 * (1 - self.roll_time_rate) * self.roll_time) // self.time_step

    def update_index(self):
        self.text1_scrollarea.update_index(self.begin_index, self.move_step)
        self.text2_scrollarea.update_index(self.begin_index, self.move_step)
        self._time_count_in += 1
        self._time_count_out += 1
        if self._is_locked:
            if self._time_count_in * self.time_step >= 500:
                self.lock_button.setHidden(True)
                self.calibrate_button.setHidden(True)
            elif self._time_count_out * self.time_step >= 1000:
                self.lock_button.setHidden(False)
                self.calibrate_button.setHidden(False)


    # endregion

    # 设置播放状态
    def set_play(self, flag):
        if flag:
            if not self._is_play:
                self._is_play = True
                self.pause_button.setIcon(QtGui.QIcon(u":/pic/images/pause.png"))
                if not self.timer.isActive():
                    self.timer.start()
        else:
            if self._is_play:
                self._is_play = False
                self.pause_button.setIcon(QtGui.QIcon(u":/pic/images/continue.png"))
                if self.timer.isActive():
                    self.timer.stop()

    # 锁定歌词窗口
    def pause_button_clicked(self):
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

    # 关闭歌词窗口
    def on_close_button_clicked(self):
        self.close()

    def show(self) -> None:
        self.setGeometry(500, 900, self.width(), self.height())
        super(LyricsWindowView, self).show()