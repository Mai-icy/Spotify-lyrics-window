#!/usr/bin/python
# -*- coding:utf-8 -*-
import weakref

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from components.raw_ui.LyricsManagePage import Ui_LyricsManage
from components.work_thread import thread_drive
from components.dialog.lyrics_download_dialog import LyricsDownloadDialog

from common.lyric.lyric_type import TransType, LrcFile
from common.lyric.lyric_manage import LyricFileManage
from common.temp_manage import TempFileManage
from common.api import SpotifyApi
from common.config import Config


class FileListWidgetItem(QListWidgetItem):
    def __init__(self, parent=None, *, track_id, no_lyric=False):
        super(FileListWidgetItem, self).__init__(parent)
        self.track_id = track_id
        self.no_lyric = no_lyric

        self.set_no_lyric(no_lyric)

    def set_no_lyric(self, flag: bool):
        if flag:
            self.setBackground(QColor(177, 177, 177))
        else:
            self.setBackground(Qt.white)
        self.no_lyric = flag


class LyricsManagePage(QWidget, Ui_LyricsManage):
    set_plain_text_signal = pyqtSignal(str)

    def __init__(self, parent=None, *, setting_window=None):
        super(LyricsManagePage, self).__init__(parent)
        self.setupUi(self)
        self.setting_window = setting_window

        self._init_components()
        self._init_common()
        self._init_dialog()
        self._init_signal()

    def _init_components(self):
        self.trans_text_list = ["无翻译", "音译", "中文翻译"]

        self.image_label.setScaledContents(True)
        self.show_comboBox.clear()
        self.show_comboBox.addItems(self.trans_text_list)

        self.lyrics_plainTextEdit.setReadOnly(True)

        self._set_modify_mode(False)

    def _init_common(self):
        self.current_lrc = LrcFile()

        self.lyrics_file_manage_ = weakref.ref(LyricFileManage())
        self.temp_file_manage = TempFileManage()
        self.spotify_api = SpotifyApi()

        self.lyrics_file_items = []

    def _init_signal(self):
        self.filter_lineEdit.textChanged.connect(self.filter_file_item_event)
        self.lyrics_listWidget.itemClicked.connect(self.click_file_item_event)

        self.download_button.clicked.connect(self.download_lyric_dialog_show_event)
        self.download_dialog.download_lrc_signal.connect(self.download_lyric_dialog_done_event)
        self.download_dialog.finished.connect(self.download_lyric_dialog_done_event)

        self.cancel_button.clicked.connect(self.cancel_modify_text_event)
        self.confirm_button.clicked.connect(self.confirm_modify_text_event)
        self.modify_button.clicked.connect(self.modify_lyric_text_event)
        self.export_button.clicked.connect(self.export_lyric_event)

        self.set_plain_text_signal.connect(self.set_plain_text)
        self.show_comboBox.currentIndexChanged.connect(self.lyric_show_trans_event)

    def _init_dialog(self):
        self.download_dialog = LyricsDownloadDialog(self)

    def filter_file_item_event(self):
        filter_text = self.filter_lineEdit.text()

        if not filter_text:
            for item in self.lyrics_file_items:
                if item.isHidden():
                    item.setHidden(False)
            return

        res = self.lyrics_listWidget.findItems(filter_text, Qt.MatchWrap | Qt.MatchContains)

        count_ = self.lyrics_listWidget.count()
        for i in range(count_):
            p_item = self.lyrics_listWidget.item(i)
            if p_item not in res:
                if not p_item.isHidden():
                    p_item.setHidden(True)
            else:
                if p_item.isHidden():
                    p_item.setHidden(False)

    @thread_drive()
    def click_file_item_event(self, item: FileListWidgetItem):
        track_id = item.track_id
        track_title = item.text()

        image = self.temp_file_manage.get_temp_image(track_id)
        title, singer = track_title.split(" - ")[:2]  # todo
        self.songname_label.setText(title)
        self.singer_label.setText(singer)

        if self.lyrics_file_manage.is_lyric_exist(track_id):
            self.current_lrc = self.lyrics_file_manage.read_lyric_file(track_id)
        else:  # 无歌词
            self.current_lrc = LrcFile()
        self.lyric_show_trans_event()

        if not image.getvalue():
            self.image_label.clear()
            self.image_label.setText("正在获取封面")

            song_data = self.spotify_api.search_song_info(track_id, download_pic=True)
            image = song_data.picBuffer
            self.temp_file_manage.save_temp_image(track_id, image)

        if self.lyrics_listWidget.currentItem() == item:
            pix = QPixmap()
            pix.loadFromData(image.read())
            self.image_label.setPixmap(pix)

    @property
    def lyrics_file_manage(self):
        return self.lyrics_file_manage_()

    def load_lyrics_file(self):
        tracks_id_data = self.lyrics_file_manage.get_tracks_id_data()
        not_found_data = self.lyrics_file_manage.get_not_found_data()

        self.lyrics_listWidget.clear()
        self.lyrics_file_items.clear()

        for track_id in not_found_data:
            item = FileListWidgetItem(track_id=track_id, no_lyric=True)
            item.setText(not_found_data[track_id]["track_title"])

            self.lyrics_listWidget.addItem(item)
            self.lyrics_file_items.append(item)

        for track_id in tracks_id_data:
            item = FileListWidgetItem(track_id=track_id)
            item.setText(tracks_id_data[track_id])

            self.lyrics_listWidget.addItem(item)
            self.lyrics_file_items.append(item)

    def download_lyric_dialog_show_event(self):
        self.setting_window.mask_.show()
        self.download_dialog.show()

        item = self.lyrics_listWidget.currentItem()
        if item:
            self.download_dialog.search_lineEdit.setText(item.text())
            self.download_dialog.search_event()

    def download_lyric_dialog_done_event(self, lrc=None):
        if not lrc:
            self.setting_window.mask_.hide()
            return

        item = self.lyrics_listWidget.currentItem()
        track_id = item.track_id

        self.current_lrc = lrc
        self.lyric_show_trans_event()
        self.lyrics_file_manage.save_lyric_file(track_id, lrc)

        item.set_no_lyric(False)

    def export_lyric_event(self):
        lrc_text = self.lyrics_plainTextEdit.toPlainText()
        if not lrc_text or lrc_text == "无歌词":
            return

        self.setting_window.mask_.show()
        file_path = QFileDialog.getSaveFileName(self, "save file", "", "Lyric (*.lrc);;Text files (*.txt)")
        self.setting_window.mask_.hide()
        if not file_path:
            return

        lrc = LrcFile()
        lrc.load_content(lrc_text, TransType.NON)
        lrc.save_to_lrc(file_path[0], TransType.NON)

    def modify_lyric_text_event(self):
        self.ori_plain_text = self.lyrics_plainTextEdit.toPlainText()
        self._set_modify_mode(True)

    def confirm_modify_text_event(self):
        self._set_modify_mode(False)

        new_lyric_text = self.lyrics_plainTextEdit.toPlainText()
        trans_type = TransType(self.show_comboBox.currentIndex())
        LrcFile.load_content(self.current_lrc, new_lyric_text, trans_type)
        try:
            pass
        except Exception as e:
            print(e)
            self.set_plain_text_signal.emit(self.ori_plain_text)

        track_id = self.lyrics_listWidget.currentItem().track_id
        self.lyrics_file_manage.save_lyric_file(track_id, self.current_lrc)

    def cancel_modify_text_event(self):
        self._set_modify_mode(False)

        self.set_plain_text_signal.emit(self.ori_plain_text)

    def _set_modify_mode(self, flag: bool):
        self.confirm_button.setVisible(flag)
        self.cancel_button.setVisible(flag)
        self.show_comboBox.setEnabled(not flag)
        self.lyrics_plainTextEdit.setReadOnly(not flag)

    def lyric_show_trans_event(self, index_=None):
        if not index_:
            index_ = self.show_comboBox.currentIndex()
        trans_type = TransType(index_)
        if self.current_lrc.empty(trans_type):
            self.set_plain_text_signal.emit("无歌词")
        else:
            self.set_plain_text_signal.emit(self.current_lrc.get_content(trans_type))

    def set_plain_text(self, text):
        self.lyrics_plainTextEdit.setPlainText(text)


