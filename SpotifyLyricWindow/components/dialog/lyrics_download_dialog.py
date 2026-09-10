#!/usr/bin/python
# -*- coding:utf-8 -*-
from functools import partial
from itertools import zip_longest

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from components.raw_ui import Ui_LyricsDownloadDialog
from components.dialog import WarningDialog
from components.work_thread import thread_manager
from common.api.lyric_api import CloudMusicWebApi, KugouApi, SpotifyApi
from common.api.exceptions import NoneResultError, NetworkError, UserError
from common.temp_manage import TempFileManage
from common.logger import get_logger


logger = get_logger(__name__)


class _DownloadTask(QThread):
    """Only plain data/API calls cross into this thread, never dialog widgets."""
    result_ready = pyqtSignal(int, object, object)

    def __init__(self, request_id, work):
        super().__init__()
        self.request_id = request_id
        self.work = work

    def run(self):
        try:
            result = self.work()
        except Exception as exc:
            logger.exception("Lyrics download dialog request failed")
            self.result_ready.emit(self.request_id, None, str(exc))
        else:
            self.result_ready.emit(self.request_id, result, None)


class LyricsDownloadDialog(QDialog, Ui_LyricsDownloadDialog):
    download_lrc_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(LyricsDownloadDialog, self).__init__(parent)
        self._request_id = 0
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

    def search_event(self, *_):
        """在主线程读取输入和更新界面，只将网络查询交给后台。"""
        keyword = self.search_lineEdit.text()
        self.search_tableWidget.setRowCount(0)
        self.image_label.clear()
        self._set_detail_label((self.tr("正在搜索相关歌词，请稍后"), ""))
        self._set_controls_enabled(False)
        self.warning_dialog.hide()
        apis = {"spotify": self.spotify_api, "kugou": self.kugou_api, "cloud": self.cloud_api}
        self._start_request(partial(self._search_sources, keyword, apis), self._search_done)

    @staticmethod
    def _search_sources(keyword, apis):
        results, errors = {}, []
        for name, api in apis.items():
            try:
                results[name] = api.search_song_id(keyword)
            except NoneResultError:
                results[name] = []
            except (NetworkError, UserError) as exc:
                results[name] = []
                errors.append(f"{name}: {exc}")
        rows = []
        sources = ("kugou", "cloud", "spotify")
        for group in zip_longest(*(results[name] for name in sources)):
            for name, data in zip(sources, group):
                if data is not None:
                    rows.append((data.songName, data.singer, data.duration, name, data.idOrMd5))
        return rows, errors

    @pyqtSlot(int, object, object)
    def _search_done(self, request_id, result, error):
        if request_id != self._request_id:
            return
        self._set_controls_enabled(True)
        if error is not None:
            self._set_detail_label((self.tr("搜索失败"), error))
            return
        rows, errors = result
        self._load_result_table_widget(rows)
        self.download_button.setEnabled(bool(rows))
        message = self.tr("请在上方选择") if rows else self.tr("搜索词无结果")
        self._set_detail_label((message, "; ".join(errors)))

    def result_click_event(self, item):
        """主线程快照选中行，旧封面请求不能覆盖新选择。"""
        row = item.row()
        title = self.search_tableWidget.item(row, 0).text()
        singer = self.search_tableWidget.item(row, 1).text()
        source = self.search_tableWidget.item(row, 3).text()
        track_id = self.search_tableWidget.item(row, 4).text()
        self._set_detail_label((title, singer))
        self.image_label.clear()
        self._request_id += 1
        try:
            image = self.temp_file_manage.get_temp_image(track_id)
        except OSError:
            logger.exception("Cannot read cover cache")
            image = None
        if image and image.getvalue():
            self._show_image(image.getvalue())
            return
        self._start_request(partial(self._fetch_cover, self._source_api(source), track_id), self._cover_done)

    @staticmethod
    def _fetch_cover(api, track_id):
        data = api.search_song_info(track_id, download_pic=True, pic_size=64)
        return track_id, data.picBuffer

    @pyqtSlot(int, object, object)
    def _cover_done(self, request_id, result, error):
        if request_id != self._request_id:
            return
        if error is not None:
            self.image_label.setText(self.tr("封面获取失败"))
            return
        track_id, image = result
        if image and image.getvalue():
            try:
                self.temp_file_manage.save_temp_image(track_id, image)
            except OSError:
                logger.exception("Cannot save cover cache")
            self._show_image(image.getvalue())

    def _show_image(self, data):
        pix = QPixmap()
        pix.loadFromData(data)
        self.image_label.setPixmap(pix)

    def _source_api(self, source):
        return {"kugou": self.kugou_api, "spotify": self.spotify_api, "cloud": self.cloud_api}[source]

    def download_event(self, item=None):
        """下载歌词事件"""
        if item is None or isinstance(item, bool):
            item = self.search_tableWidget.currentItem()

        if not item:
            return
        track_id_or_md5 = self.search_tableWidget.item(item.row(), 4).text()
        api = self.search_tableWidget.item(item.row(), 3).text()
        self._set_controls_enabled(False)
        self.warning_dialog.hide()
        self._start_request(partial(self._source_api(api).fetch_song_lyric, track_id_or_md5), self._download_done)

    @pyqtSlot(int, object, object)
    def _download_done(self, request_id, lrc, error):
        if request_id != self._request_id:
            return
        self._set_controls_enabled(True)
        if error is not None:
            self.warning_dialog.set_text(error)
            self.warning_dialog.show()
            return
        self.download_lrc_signal.emit(lrc)
        self.close()

    def _start_request(self, work, callback):
        self._request_id += 1
        task = _DownloadTask(self._request_id, work)
        task.result_ready.connect(callback, Qt.ConnectionType.QueuedConnection)
        thread_manager.add_thread(task)
        task.start()

    def _set_controls_enabled(self, enabled):
        self.search_tableWidget.setEnabled(enabled)
        self.search_button.setEnabled(enabled)
        self.search_lineEdit.setEnabled(enabled)
        self.download_button.setEnabled(enabled and self.search_tableWidget.rowCount() > 0)

    def hideEvent(self, event):
        # Closing settings may hide/delete this dialog while a request is in
        # flight. Queued QObject slots auto-disconnect on deletion; a reusable
        # hidden dialog additionally invalidates results from its old session.
        self._request_id += 1
        super().hideEvent(event)

    def showEvent(self, event):
        self._set_controls_enabled(True)
        super().showEvent(event)

    def _set_detail_label(self, texts):
        """设置文本，利于非主线程控制"""
        self.songname_label.setText(texts[0])
        self.singer_label.setText(texts[1])

    def _load_result_table_widget(self, result_data):
        """设置搜索结果到表格，利于非主线程控制"""
        self.search_tableWidget.setRowCount(len(result_data))
        for outer_index, outer_data in enumerate(result_data):
            for inner_index, inner_data in enumerate(outer_data):
                item = QTableWidgetItem()
                item.setText(str(inner_data))
                self.search_tableWidget.setItem(outer_index, inner_index, item)
