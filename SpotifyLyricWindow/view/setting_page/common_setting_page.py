#!/usr/bin/python
# -*- coding:utf-8 -*-
import weakref

from requests.exceptions import ProxyError
from PyQt6.QtWidgets import *

from common.api.user_api import SpotifyUserAuth
from common.config import Config
from common.lyric import LyricFileManage
from common.path import LRC_PATH, TEMP_PATH, ORI_LRC_PATH, ORI_TEMP_PATH
from common.temp_manage import TempFileManage
from components.raw_ui import Ui_CommonPage


class CommonPage(QWidget, Ui_CommonPage):
    def __init__(self, parent=None, lyric_window=None, setting_window=None):
        super(CommonPage, self).__init__(parent)
        self.lyric_window = lyric_window
        self.setting_window = setting_window
        self.setupUi(self)
        self._init_common()
        self._init_label()
        self._init_line_edit()

        self._init_signal()

    def _init_common(self):
        self.auth = SpotifyUserAuth()
        self.lyrics_file_manage_ = weakref.ref(LyricFileManage())
        self.temp_file_manage_ = weakref.ref(TempFileManage())

    def _init_label(self):
        """初始化标签属性"""
        self.register_label.setOpenExternalLinks(True)
        self.register_label.setText('<a href="https://developer.spotify.com/dashboard/">注册client</a>')

        self.cache_tip_label.setText("")
        self.lyrics_tip_label.setText("")

    def _init_line_edit(self):
        """初始化lineEdit"""
        self.secret_lineEdit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)

        self.cache_path_lineEdit.setReadOnly(True)
        self.lyrics_path_lineEdit.setReadOnly(True)

    def _init_signal(self):
        """初始化信号"""
        self.cache_path_button.clicked.connect(self._cache_path_press_event)
        self.lyrics_path_button.clicked.connect(self._lyrics_path_press_event)

        self.cache_path_lineEdit.textChanged.connect(self._cache_path_text_event)
        self.lyrics_path_lineEdit.textChanged.connect(self._lyrics_path_text_event)

        self.clear_cache_button.clicked.connect(self.temp_file_manage.clean_all_temp)
        self.global_offset_doubleSpinBox.valueChanged.connect(self.set_api_offset_event)
        self.confirm_button.clicked.connect(self.confirm_client_event)
        self.default_button.clicked.connect(self.set_default_event)

        self.quit_on_close_checkBox.stateChanged.connect(self._quit_on_close_event)
        self.save_position_checkBox.stateChanged.connect(self._save_position_event)

    def load_config(self):
        """载入配置文件"""
        common_config = Config.CommonConfig

        client_id = common_config.ClientConfig.client_id
        client_secret = common_config.ClientConfig.client_secret
        temp_path = str(TEMP_PATH)
        lyrics_path = str(LRC_PATH)
        is_save_position = common_config.is_save_position
        is_quit_on_close = common_config.is_quit_on_close

        api_offset = self.lyrics_file_manage.get_offset_file("api_offset")

        self.save_position_checkBox.setChecked(is_save_position)
        self.quit_on_close_checkBox.setChecked(is_quit_on_close)

        self.id_lineEdit.setText(client_id)
        self.secret_lineEdit.setText(client_secret)
        self.cache_path_lineEdit.setText(temp_path)
        self.lyrics_path_lineEdit.setText(lyrics_path)
        self.global_offset_doubleSpinBox.setValue(api_offset)

        self.cache_tip_label.setText("")
        self.lyrics_tip_label.setText("")

    def confirm_client_event(self):
        """确认输入的client事件"""
        Config.CommonConfig.ClientConfig.client_id = self.id_lineEdit.text()
        Config.CommonConfig.ClientConfig.client_secret = self.secret_lineEdit.text()
        try:
            self.auth.load_client_config()
        except NotImplementedError as e:
            self.lyric_window.error_msg_show_signal.emit(e)
            return
        except ProxyError:
            error = ProxyError("代理错误 请在配置文件检查代理并重启")
            self.lyric_window.error_msg_show_signal.emit(error)
            return
        self.lyric_window.text_show_signal.emit(1, "成功设置client配置！", 0)
        self.lyric_window.text_show_signal.emit(2, "♪(^∇^*)", 0)
        self.lyric_window.delay_calibration()

    def set_default_event(self):
        """设置初始化按钮事件"""
        default_dict = Config.get_default_dict()["CommonConfig"]

        is_save_position = default_dict["is_save_position"]
        is_quit_on_close = default_dict["is_quit_on_close"]
        api_offset = default_dict["api_offset"]

        self.save_position_checkBox.setChecked(is_save_position)
        self.quit_on_close_checkBox.setChecked(is_quit_on_close)
        self.cache_path_lineEdit.setText(str(ORI_TEMP_PATH))
        self.lyrics_path_lineEdit.setText(str(ORI_LRC_PATH))
        self.global_offset_doubleSpinBox.setValue(api_offset)

        Config.CommonConfig.PathConfig.lyrics_file_path = ""
        Config.CommonConfig.PathConfig.temp_file_path = ""

    def set_path_event(self, line_edit: QLineEdit):
        """设置路径事件"""
        self.setting_window.mask_.show()
        file_path = QFileDialog.getExistingDirectory(self, "选择一个目录", "./", QFileDialog.ShowDirsOnly)
        self.setting_window.mask_.hide()
        if not file_path:
            return
        else:
            line_edit.setText(file_path)

        if line_edit is self.lyrics_path_lineEdit:
            Config.CommonConfig.PathConfig.lyrics_file_path = file_path
        else:
            Config.CommonConfig.PathConfig.temp_file_path = file_path

    def set_check_box_event(self, check_box: QCheckBox):
        """设置勾选框事件"""
        flag = check_box.isChecked()
        if check_box is self.save_position_checkBox:
            Config.CommonConfig.is_save_position = flag
        else:
            Config.CommonConfig.is_quit_on_close = flag

    def set_api_offset_event(self):
        """修改全局偏移事件"""
        new_val = self.global_offset_doubleSpinBox.value()
        self.lyrics_file_manage.set_offset_file("api_offset", new_val * 1000)

    def _cache_path_press_event(self):
        self.set_path_event(self.cache_path_lineEdit)

    def _lyrics_path_press_event(self):
        self.set_path_event(self.lyrics_path_lineEdit)

    def _lyrics_path_text_event(self):
        self.path_change_tip_event(self.lyrics_tip_label)

    def _cache_path_text_event(self):
        self.path_change_tip_event(self.cache_tip_label)

    def _quit_on_close_event(self):
        self.set_check_box_event(self.quit_on_close_checkBox)

    def _save_position_event(self):
        self.set_check_box_event(self.save_position_checkBox)

    @staticmethod
    def path_change_tip_event(tip_label: QLabel):
        """修改路径事件"""
        tip_label.setText("路径修改将在重启后生效")

    @property
    def lyrics_file_manage(self):
        return self.lyrics_file_manage_()

    @property
    def temp_file_manage(self):
        return self.temp_file_manage_()

