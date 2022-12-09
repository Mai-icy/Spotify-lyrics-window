#!/usr/bin/python
# -*- coding:utf-8 -*-
import io

import requests
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsDownloadDialog import Ui_LyricsDownloadDialog
from components.work_thread import thread_drive
from common.api.lyric_api import CloudMusicWebApi, KugouApi
from common.temp_manage import TempFileManage
from common.api.api_error import NoneResultError


class LyricsDownloadDialog(QDialog, Ui_LyricsDownloadDialog):
    download_lrc_signal = pyqtSignal(object)

    _load_data_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(LyricsDownloadDialog, self).__init__(parent)
        self.setupUi(self)
        self._init_table_widget()
        self._init_signal()
        self._init_api()
        self._init_label()
        self.temp_file_manage = TempFileManage()

    def _init_label(self):
        self.image_label.setScaledContents(True)
        self.songname_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.singer_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def _init_signal(self):
        self.search_tableWidget.itemClicked.connect(self.result_click_event)
        self.search_button.clicked.connect(self.search_event)

        self.download_button.clicked.connect(self.download_event)
        self.search_tableWidget.itemDoubleClicked.connect(self.download_event)
        self.cancel_button.clicked.connect(self.close)

        self._load_data_signal.connect(self._load_result_table_widget)

    def _init_api(self):
        self.kugou_api = KugouApi()
        self.cloud_api = CloudMusicWebApi()

    def _init_table_widget(self):
        self.search_tableWidget.horizontalHeader().setVisible(True)
        self.search_tableWidget.horizontalHeader().setHighlightSections(True)
        self.search_tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.search_tableWidget.horizontalHeader().setStretchLastSection(False)

        self.search_tableWidget.verticalHeader().setVisible(False)
        self.search_tableWidget.setShowGrid(False)

        self.search_tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        self.search_tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.search_tableWidget.verticalHeader().setDefaultSectionSize(47)
        self.search_tableWidget.horizontalHeader().setMinimumHeight(30)  # 表头高度

        self.search_tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.search_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.search_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # self.search_tableWidget.clear()
        self.search_tableWidget.setColumnCount(5)

        self.search_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.search_tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.search_tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        # self.setColumnWidth(0, 380)  # 设置指定列宽
        self.search_tableWidget.setColumnWidth(2, 55)
        self.search_tableWidget.setColumnWidth(3, 55)

        self.setAcceptDrops(True)
        self.search_tableWidget.setAcceptDrops(True)  # 允许文件拖入

        column_text_list = ['曲名', '歌手', '时长', '来源', 'id']
        for column in range(5):
            item = QTableWidgetItem()
            item.setText(column_text_list[column])
            self.search_tableWidget.setHorizontalHeaderItem(column, item)
        self.search_tableWidget.hideColumn(4)

    @thread_drive()
    def search_event(self, *_):
        self.search_tableWidget.clearContents()

        self.singer_label.setText("")
        self.songname_label.setText("正在搜索相关歌词，请稍后")

        keyword = self.search_lineEdit.text()

        try:
            res_kugou = self.kugou_api.search_song_id(keyword)
        except NoneResultError:
            res_kugou = []
        try:
            res_cloud = self.cloud_api.search_song_id(keyword)
        except NoneResultError:
            res_cloud = []

        res_list = []
        for i in range(len(res_kugou) + len(res_cloud)):
            if res_kugou:
                data = res_kugou.pop(0)
                new_data = (data.songName, data.singer, data.duration, "kugou", data.idOrMd5)
                res_list.append(new_data)
            if res_cloud:
                data = res_cloud.pop(0)
                new_data = (data.songName, data.singer, data.duration, "cloud", data.idOrMd5)
                res_list.append(new_data)

        if not res_list:
            self.songname_label.setText("搜索词无结果")
            return

        self.search_tableWidget.setRowCount(len(res_list))
        self._load_data_signal.emit(res_list)
        self.songname_label.setText("请在上方选择")

    def _load_result_table_widget(self, result_data):
        for outer_index, outer_data in enumerate(result_data):
            for inner_index, inner_data in enumerate(outer_data):
                item = QTableWidgetItem()
                item.setText(inner_data)
                self.search_tableWidget.setItem(outer_index, inner_index, item)

    @thread_drive()
    def result_click_event(self, item):
        title = self.search_tableWidget.item(item.row(), 0).text()
        singer = self.search_tableWidget.item(item.row(), 1).text()
        api = self.search_tableWidget.item(item.row(), 3).text()
        track_id = self.search_tableWidget.item(item.row(), 4).text()
        if api == "kugou":
            data_api = self.kugou_api
        else:
            data_api = self.cloud_api

        image = self.temp_file_manage.get_temp_image(track_id)
        self.songname_label.setText(title)
        self.singer_label.setText(singer)

        if not image.getvalue():
            self.image_label.clear()
            self.image_label.setText("正在获取封面")

            song_data = data_api.search_song_info(track_id, download_pic=True)
            image = song_data.picBuffer
            if image:
                self.temp_file_manage.save_temp_image(track_id, image)
            else:
                image = io.BytesIO()

        if self.search_tableWidget.currentItem().row() == item.row():
            pix = QPixmap()
            if image.getvalue():
                pix.loadFromData(image.read())
                self.image_label.setPixmap(pix)
            else:
                self.image_label.setText("无图片")

    def download_event(self, item=None):
        if not item:
            item = self.search_tableWidget.currentItem()

        if not item:
            return
        track_id_or_md5 = self.search_tableWidget.item(item.row(), 4).text()
        api = self.search_tableWidget.item(item.row(), 3).text()
        if api == "kugou":
            data_api = self.kugou_api
        else:
            data_api = self.cloud_api
        try:
            lrc = data_api.fetch_song_lyric(track_id_or_md5)
        except requests.RequestException as e:
            print(e)  # todo
            return
        self.download_lrc_signal.emit(lrc)
        self.close()








