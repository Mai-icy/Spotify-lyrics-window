#!/usr/bin/python
# -*- coding:utf-8 -*-
import io

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from components.raw_ui import Ui_LyricsDownloadDialog
from components.dialog import WarningDialog
from components.work_thread import thread_drive
from common.api.lyric_api import CloudMusicWebApi, KugouApi, SpotifyApi
from common.api.exceptions import NoneResultError, NetworkError, UserError
from common.temp_manage import TempFileManage


class LyricsDownloadDialog(QDialog, Ui_LyricsDownloadDialog):
    download_lrc_signal = pyqtSignal(object)

    _load_data_signal = pyqtSignal(list)
    _load_detail_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(LyricsDownloadDialog, self).__init__(parent)
        self.setupUi(self)
        self._init_table_widget()
        self._init_signal()
        self._init_api()
        self._init_label()
        self.temp_file_manage = TempFileManage()

        self.warning_dialog = WarningDialog(self)

    def _init_label(self):
        """初始化标签"""
        self.image_label.setScaledContents(True)
        self.songname_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.singer_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def _init_signal(self):
        """初始化信号"""
        # 表格信号连接
        self.search_tableWidget.itemClicked.connect(self.result_click_event)
        self.search_tableWidget.itemDoubleClicked.connect(self.download_event)
        # 按钮信号连接
        self.search_button.clicked.connect(self.search_event)
        self.download_button.clicked.connect(self.download_event)
        self.cancel_button.clicked.connect(self.close)
        # 设置文本信号连接（为了便于线程设置文本不出现未响应）
        self._load_detail_signal.connect(self._set_detail_label)
        self._load_data_signal.connect(self._load_result_table_widget)

    def _init_api(self):
        """初始化使用的歌词api"""
        self.kugou_api = KugouApi()
        self.cloud_api = CloudMusicWebApi()
        self.spotify_api = SpotifyApi()

    def _init_table_widget(self):
        """初始化表格属性"""
        self.search_tableWidget.horizontalHeader().setVisible(True)
        self.search_tableWidget.horizontalHeader().setHighlightSections(True)
        self.search_tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.search_tableWidget.horizontalHeader().setStretchLastSection(False)

        self.search_tableWidget.verticalHeader().setVisible(False)
        self.search_tableWidget.setShowGrid(False)

        # 设置表头的默认对齐方式
        self.search_tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # 设置垂直表头的固定大小
        self.search_tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.search_tableWidget.verticalHeader().setDefaultSectionSize(47)
        self.search_tableWidget.horizontalHeader().setMinimumHeight(30)  # 表头高度

        # 设置选择模式和行为
        self.search_tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.search_tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.search_tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 设置列数
        self.search_tableWidget.setColumnCount(5)

        # 设置表头列宽自动拉伸
        self.search_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 设置指定列宽固定
        self.search_tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.search_tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        # self.setColumnWidth(0, 380)  # 设置指定列宽
        self.search_tableWidget.setColumnWidth(2, 55)
        self.search_tableWidget.setColumnWidth(3, 55)

        self.setAcceptDrops(True)
        self.search_tableWidget.setAcceptDrops(True)  # 允许文件拖入

        column_text_list = [self.tr('曲名'), self.tr('歌手'), self.tr('时长'), self.tr('来源'), self.tr('id')]
        for column in range(5):
            item = QTableWidgetItem()
            item.setText(column_text_list[column])
            self.search_tableWidget.setHorizontalHeaderItem(column, item)
        self.search_tableWidget.hideColumn(4)

    @thread_drive()
    def search_event(self, *_):
        """搜索事件"""
        self.search_tableWidget.clearContents()

        self.image_label.setPixmap(QPixmap())
        self._load_detail_signal.emit((self.tr("正在搜索相关歌词，请稍后"), ""))

        keyword = self.search_lineEdit.text()

        network_error = False

        try:
            res_spotify = self.spotify_api.search_song_id(keyword)
        except NoneResultError:
            res_spotify = []
        except NetworkError:
            res_spotify = []
            self._load_detail_signal.emit((self.tr("连接到spotify网络错误"), ""))
            network_error = True

        try:
            res_kugou = self.kugou_api.search_song_id(keyword)
        except NoneResultError:
            res_kugou = []
        except NetworkError:
            res_kugou = []
            self._load_detail_signal.emit((self.tr("连接到kugou网络错误"), ""))
            network_error = True

        try:
            res_cloud = self.cloud_api.search_song_id(keyword)
        except NoneResultError:
            res_cloud = []
        except NetworkError:
            res_cloud = []
            self._load_detail_signal.emit((self.tr("连接到网易云网络错误"), ""))
            network_error = True

        # 交叉合并搜索结果，在前的优先级高
        res_list = []
        for i in range(len(res_kugou) + len(res_cloud) + len(res_spotify)):
            if res_kugou:
                data = res_kugou.pop(0)
                new_data = (data.songName, data.singer, data.duration, "kugou", data.idOrMd5)
                res_list.append(new_data)
            if res_cloud:
                data = res_cloud.pop(0)
                new_data = (data.songName, data.singer, data.duration, "cloud", data.idOrMd5)
                res_list.append(new_data)
            if res_spotify:
                data = res_spotify.pop(0)
                new_data = (data.songName, data.singer, data.duration, "spotify", data.idOrMd5)
                res_list.append(new_data)

        if not res_list and not network_error:
            self._load_detail_signal.emit((self.tr("搜索词无结果"), ""))
            return

        self.search_tableWidget.setRowCount(len(res_list))
        self._load_data_signal.emit(res_list)
        self._load_detail_signal.emit((self.tr("请在上方选择"), ""))

    @thread_drive()
    def result_click_event(self, item):
        """点击搜索结果事件"""
        self.search_tableWidget.setEnabled(False)
        title = self.search_tableWidget.item(item.row(), 0).text()
        singer = self.search_tableWidget.item(item.row(), 1).text()
        api = self.search_tableWidget.item(item.row(), 3).text()
        track_id = self.search_tableWidget.item(item.row(), 4).text()
        if api == "kugou":
            data_api = self.kugou_api
        elif api == "spotify":
            data_api = self.spotify_api
        else:
            data_api = self.cloud_api

        image = self.temp_file_manage.get_temp_image(track_id)
        self._load_detail_signal.emit((title, singer))

        if not image.getvalue():
            self.image_label.clear()
            # self.image_label.setText("正在获取封面") 引发崩溃
            try:
                song_data = data_api.search_song_info(track_id, download_pic=True, pic_size=64)
            except NetworkError:
                self._load_detail_signal.emit((self.tr("网络错误，获取失败"), ""))
                self.search_tableWidget.setEnabled(True)
                return
            image = song_data.picBuffer
            if image:
                self.temp_file_manage.save_temp_image(track_id, image)
            else:
                image = io.BytesIO()

        item = self.search_tableWidget.currentItem()

        if item and item.row() == item.row():
            pix = QPixmap()
            if image.getvalue():
                pix.loadFromData(image.read())
                self.image_label.setPixmap(pix)
            else:
                # self.image_label.setText("无图片")
                ...
        self.search_tableWidget.setEnabled(True)

    def download_event(self, item=None):
        """下载歌词事件"""
        if not item:
            item = self.search_tableWidget.currentItem()

        if not item:
            return
        self.search_tableWidget.setEnabled(False)

        track_id_or_md5 = self.search_tableWidget.item(item.row(), 4).text()
        api = self.search_tableWidget.item(item.row(), 3).text()
        if api == "kugou":
            data_api = self.kugou_api
        elif api == "spotify":
            data_api = self.spotify_api
        else:
            data_api = self.cloud_api
        try:
            lrc = data_api.fetch_song_lyric(track_id_or_md5)
        except (NetworkError, NoneResultError, UserError) as e:
            self.warning_dialog.show()
            self.warning_dialog.set_text(str(e))
            self.search_tableWidget.setEnabled(True)
            return
        self.search_tableWidget.setEnabled(True)
        self.download_lrc_signal.emit(lrc)
        self.close()

    def _set_detail_label(self, texts):
        """设置文本，利于非主线程控制"""
        self.songname_label.setText(texts[0])
        self.singer_label.setText(texts[1])

    def _load_result_table_widget(self, result_data):
        """设置搜索结果到表格，利于非主线程控制"""
        for outer_index, outer_data in enumerate(result_data):
            for inner_index, inner_data in enumerate(outer_data):
                item = QTableWidgetItem()
                item.setText(inner_data)
                self.search_tableWidget.setItem(outer_index, inner_index, item)
