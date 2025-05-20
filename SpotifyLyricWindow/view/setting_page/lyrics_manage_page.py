#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
import weakref

import requests
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from common.api.lyric_api import SpotifyApi
from common.lyric.lyric_manage import LyricFileManage
from common.typing import TransType, LrcFile
from common.temp_manage import TempFileManage
from components.dialog.lyrics_download_dialog import LyricsDownloadDialog
from components.work_thread import thread_drive
from components.raw_ui import Ui_LyricsManage


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
            self.setBackground(Qt.GlobalColor.white)
        self.no_lyric = flag


class LyricsManagePage(QWidget, Ui_LyricsManage):
    set_plain_text_signal = pyqtSignal(str)
    set_detail_label_signal = pyqtSignal(tuple)

    def __init__(self, parent=None, *, setting_window=None):
        super(LyricsManagePage, self).__init__(parent)
        self.setupUi(self)
        self.setting_window = setting_window
        self.current_lrc = LrcFile()

        self._init_common()
        self._init_label()
        self._init_dialog()
        self._init_list_widget()
        self._init_signal()

        self._set_modify_mode(False)

    def _init_common(self):
        self.lyrics_file_manage_ = weakref.ref(LyricFileManage())
        self.temp_file_manage_ = weakref.ref(TempFileManage())
        self.spotify_api = SpotifyApi()

        self.lyrics_file_items = []

    def _init_label(self):
        """初始化标签"""
        self.image_label.setScaledContents(True)
        self.songname_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.singer_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def _init_dialog(self):
        """初始化对话框"""
        self.download_dialog = LyricsDownloadDialog(self)

    def _init_signal(self):
        """初始化信号"""
        self.filter_lineEdit.textChanged.connect(self.filter_file_item_event)
        self.lyrics_listWidget.itemClicked.connect(self.click_file_item_event)
        self.offset_doubleSpinBox.valueChanged.connect(self.set_spin_box_offset_event)
        self.show_comboBox.currentIndexChanged.connect(self.lyric_show_trans_event)
        # 下载信号连接
        self.download_button.clicked.connect(self.download_lyric_dialog_show_event)
        self.download_dialog.download_lrc_signal.connect(self.download_lyric_dialog_done_event)
        self.download_dialog.finished.connect(self.download_lyric_dialog_done_event)
        # 按钮信号连接
        self.cancel_button.clicked.connect(self.cancel_modify_text_event)
        self.confirm_button.clicked.connect(self.confirm_modify_text_event)
        self.modify_button.clicked.connect(self.modify_lyric_text_event)
        self.export_button.clicked.connect(self.export_lyric_event)
        self.delete_button.clicked.connect(self.delete_lyric_event)
        # 设置文本信号连接（为了便于线程设置文本不出现未响应）
        self.set_plain_text_signal.connect(self._set_plain_text_event)
        self.set_detail_label_signal.connect(self._set_detail_label_event)

    def _init_list_widget(self):
        """初始化歌词文件列 添加右键菜单栏"""
        self.lyrics_listWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lyrics_listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.lyrics_listWidget.customContextMenuRequested.connect(self.menu_show_event)

    def load_lyrics_file(self):
        """导入已有的歌词文件，显示在左边"""
        self.filter_lineEdit.clear()
        self.lyrics_plainTextEdit.clear()

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
            if track_id in not_found_data:
                continue

            item = FileListWidgetItem(track_id=track_id)
            item.setText(tracks_id_data[track_id])

            self.lyrics_listWidget.addItem(item)
            self.lyrics_file_items.append(item)

    def filter_file_item_event(self):
        """筛选，随着输入框的输入同步"""
        filter_text = self.filter_lineEdit.text()

        if not filter_text:
            for item in self.lyrics_file_items:
                if item.isHidden():
                    item.setHidden(False)
            return

        res = self.lyrics_listWidget.findItems(filter_text, Qt.MatchFlag.MatchWrap | Qt.MatchFlag.MatchContains)

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
        """选中项事件 显示其详细信息 以及 已有歌词"""
        track_id = item.track_id
        track_title = item.text()

        image = self.temp_file_manage.get_temp_image(track_id)
        offset = self.lyrics_file_manage.get_offset_file(track_id)
        # 显示歌词歌手以及歌名
        title_list = track_title.split(" - ")
        title = title_list[0]
        singer = ", ".join(title_list[1:])
        self.set_detail_label_signal.emit((title, singer))
        # 显示歌词设置的偏移
        self.offset_doubleSpinBox.setValue(offset)
        # 显示已有歌词
        if self.lyrics_file_manage.is_lyric_exist(track_id):
            self.current_lrc = self.lyrics_file_manage.read_lyric_file(track_id)
        else:  # 无歌词
            self.current_lrc = LrcFile()
        self.lyric_show_trans_event()
        # 下载歌曲专辑封面
        if not image.getvalue():
            self.image_label.clear()
            self.image_label.setText(self.tr("正在获取封面"))
            try:
                song_data = self.spotify_api.search_song_info(track_id, download_pic=True, pic_size=64)
            except requests.RequestException:
                return
            image = song_data.picBuffer
            self.temp_file_manage.save_temp_image(track_id, image)
        # 显示歌曲专辑封面
        if self.lyrics_listWidget.currentItem() == item:
            pix = QPixmap()
            pix.loadFromData(image.read())
            self.image_label.setPixmap(pix)

    def set_spin_box_offset_event(self):
        """设置偏移事件"""
        item = self.lyrics_listWidget.currentItem()
        if not item:
            return

        offset = self.offset_doubleSpinBox.value()
        self.lyrics_file_manage.set_offset_file(item.track_id, offset * 1000)

    def download_lyric_dialog_show_event(self):
        """下载对话框打开事件"""
        self.setting_window.mask_.show()
        self.download_dialog.show()

        item = self.lyrics_listWidget.currentItem()
        if item:
            self.download_dialog.search_lineEdit.setText(item.text())
            self.download_dialog.search_event()

    def download_lyric_dialog_done_event(self, lrc: LrcFile = None):
        """下载歌词窗口关闭事件，直接关闭 以及 下载后自动关闭"""
        if not lrc:  # 直接关闭窗口不下载
            self.setting_window.mask_.hide()
            return

        item = self.lyrics_listWidget.currentItem()
        track_id = item.track_id

        self.current_lrc = lrc
        self.lyric_show_trans_event()
        self.lyrics_file_manage.save_lyric_file(track_id, lrc)

        item.set_no_lyric(False)

    def export_lyric_event(self):
        """导出歌词事件"""
        lrc_text = self.lyrics_plainTextEdit.toPlainText()  # todo 处理略微不合适
        if not lrc_text or lrc_text == self.tr("无歌词"):
            return
        item = self.lyrics_listWidget.currentItem()
        title = item.text()

        file_name = re.sub(r'[\\/:*?"<>|]', '-', title)
        self.setting_window.mask_.show()

        file_path = QFileDialog.getSaveFileName(self, self.tr("保存文件"), file_name, "Lyric (*.lrc);;Text files (*.txt)")
        self.setting_window.mask_.hide()
        if not file_path[0]:
            return

        lrc = LrcFile()
        lrc.load_content(lrc_text, TransType.NON)
        lrc.save_to_lrc(file_path[0], TransType.NON)

    def delete_lyric_event(self):
        """删除当前歌词事件"""
        item = self.lyrics_listWidget.currentItem()
        if not item:
            return
        if not self.lyrics_file_manage.is_lyric_exist(item.track_id):
            return
        title = item.text()
        self.lyrics_file_manage.set_not_found(item.track_id, title)
        item.set_no_lyric(True)

        self.current_lrc = LrcFile()
        self.lyric_show_trans_event()

    def modify_lyric_text_event(self):
        """进入歌词修改模式事件"""
        # 保存原有的歌词 用于回撤
        self.ori_plain_text = self.lyrics_plainTextEdit.toPlainText()
        self._set_modify_mode(True)

    def confirm_modify_text_event(self):
        """确认修改事件"""
        self._set_modify_mode(False)

        new_lyric_text = self.lyrics_plainTextEdit.toPlainText()  # todo 处理略微不合适
        if new_lyric_text == self.tr("无歌词"):
            return

        trans_type = TransType(self.show_comboBox.currentIndex())
        try:
            LrcFile.load_content(self.current_lrc, new_lyric_text, trans_type)
        except Exception as e:
            print(e)
            self.set_plain_text_signal.emit(self.ori_plain_text)

        track_id = self.lyrics_listWidget.currentItem().track_id
        self.lyrics_file_manage.save_lyric_file(track_id, self.current_lrc)

    def cancel_modify_text_event(self):
        """取消修改事件"""
        self._set_modify_mode(False)

        self.set_plain_text_signal.emit(self.ori_plain_text)

    def lyric_show_trans_event(self, index_: int = None):
        """下拉框选择翻译类型事件 根据下拉框变化需要显示的歌词翻译"""
        if not index_:
            index_ = self.show_comboBox.currentIndex()
        trans_type = TransType(index_)
        if self.current_lrc.empty(trans_type):
            self.set_plain_text_signal.emit(self.tr("无歌词"))
        else:
            self.set_plain_text_signal.emit(self.current_lrc.get_content(trans_type))

    def menu_show_event(self, position):
        """item右键菜单栏事件"""
        if not self.lyrics_listWidget.itemAt(position):
            return
        list_widget_menu = QMenu()
        del_item_action = QAction(self.tr("删除歌词"), self)
        list_widget_menu.addAction(del_item_action)
        del_item_action.triggered.connect(self.menu_delete_item)

        list_widget_menu.exec(self.lyrics_listWidget.mapToGlobal(position))

    def menu_delete_item(self):
        """删除歌词文件项事件"""
        item = self.lyrics_listWidget.takeItem(self.lyrics_listWidget.currentRow())
        self.lyrics_file_items.remove(item)
        self.lyrics_file_manage.delete_lyric_file(item.track_id)

    def _set_plain_text_event(self, text: str):
        """设置文本，利于非主线程控制"""
        self.lyrics_plainTextEdit.setPlainText(text)

    def _set_detail_label_event(self, texts: tuple):
        """设置文本，利于非主线程控制"""
        self.songname_label.setText(texts[0])
        self.singer_label.setText(texts[1])

    def _set_modify_mode(self, flag: bool):
        """设置是否进入修改模式"""
        self.textbuttons_frame.setVisible(flag)
        self.confirm_button.setVisible(flag)
        self.cancel_button.setVisible(flag)

        self.export_button.setEnabled(not flag)
        self.download_button.setEnabled(not flag)
        self.show_comboBox.setEnabled(not flag)
        self.lyrics_listWidget.setEnabled(not flag)
        self.lyrics_plainTextEdit.setReadOnly(not flag)

    @property
    def lyrics_file_manage(self):
        return self.lyrics_file_manage_()

    @property
    def temp_file_manage(self):
        return self.temp_file_manage_()
