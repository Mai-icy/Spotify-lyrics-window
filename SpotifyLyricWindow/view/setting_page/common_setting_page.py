#!/usr/bin/python
# -*- coding:utf-8 -*-
import weakref
from urllib.parse import urlsplit

from requests.exceptions import ProxyError
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import *

from common.api.user_api import SpotifyUserAuth
from common.config import Config
from common.ui.i18n import supported_language
from common.lyric import LyricFileManage
from common.path import LRC_PATH, TEMP_PATH, ORI_LRC_PATH, ORI_TEMP_PATH
from common.temp_manage import TempFileManage
from components.settings_ui import Ui_CommonPage


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
        self.register_label.setText(f'<a href="https://developer.spotify.com/dashboard/">{self.tr("注册client")}</a>')

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

        self.clear_cache_button.clicked.connect(self._clear_cache_event)
        self.global_offset_doubleSpinBox.valueChanged.connect(self.set_api_offset_event)
        self.confirm_button.clicked.connect(self.confirm_client_event)
        self.default_button.clicked.connect(self.set_default_event)

        self.quit_on_close_checkBox.stateChanged.connect(self._quit_on_close_event)
        self.save_position_checkBox.stateChanged.connect(self._save_position_event)
        self.auto_track_sync_checkBox.toggled.connect(self._auto_track_sync_event)
        self.language_comboBox.currentIndexChanged.connect(self._language_event)
        self.theme_comboBox.currentIndexChanged.connect(self._theme_event)
        self.proxy_button.clicked.connect(self._proxy_event)
        for name in ('spotify', 'cloudmusic', 'kugou'):
            getattr(self, f'{name}_proxy_lineEdit').textEdited.connect(self.proxy_tip_label.clear)

    def load_config(self):
        """载入配置文件"""
        common_config = Config.CommonConfig
        self.theme_comboBox.setCurrentIndex(max(0, self.theme_comboBox.findData(common_config.settings_theme)))
        self.language_comboBox.setCurrentIndex(
            self.language_comboBox.findData(supported_language(common_config.language)))

        client_id = common_config.ClientConfig.client_id
        client_secret = common_config.ClientConfig.client_secret
        temp_path = str(TEMP_PATH)
        lyrics_path = str(LRC_PATH)
        is_save_position = common_config.is_save_position
        is_quit_on_close = common_config.is_quit_on_close

        api_offset = self.lyrics_file_manage.get_offset_file("api_offset")

        self.save_position_checkBox.setChecked(is_save_position)
        self.quit_on_close_checkBox.setChecked(is_quit_on_close)
        self.auto_track_sync_checkBox.setChecked(common_config.is_auto_track_sync)

        self.id_lineEdit.setText(client_id)
        self.secret_lineEdit.setText(client_secret)
        for name in ('spotify', 'cloudmusic', 'kugou'):
            getattr(self, f'{name}_proxy_lineEdit').setText(getattr(common_config.ClientConfig, f'{name}_proxy_ip'))
        self.proxy_tip_label.clear()
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
            error = ProxyError(self.tr("代理错误，请在常规设置中检查并应用代理设置。"))
            self.lyric_window.error_msg_show_signal.emit(error)
            return
        self.lyric_window.text_show_signal.emit(1, self.tr("成功设置client配置！"), 0)
        self.lyric_window.text_show_signal.emit(2, self.tr("♪(^∇^*)"), 0)
        self.lyric_window.delay_calibration()

    def set_default_event(self):
        """设置初始化按钮事件"""
        default_dict = Config.get_default_dict()["CommonConfig"]
        self.theme_comboBox.setCurrentIndex(self.theme_comboBox.findData(default_dict['settings_theme']))
        self.language_comboBox.setCurrentIndex(
            self.language_comboBox.findData(default_dict['language']))

        is_save_position = default_dict["is_save_position"]
        is_quit_on_close = default_dict["is_quit_on_close"]
        api_offset = default_dict["api_offset"]

        self.save_position_checkBox.setChecked(is_save_position)
        self.quit_on_close_checkBox.setChecked(is_quit_on_close)
        self.auto_track_sync_checkBox.setChecked(default_dict["is_auto_track_sync"])
        self.cache_path_lineEdit.setText(str(ORI_TEMP_PATH))
        self.lyrics_path_lineEdit.setText(str(ORI_LRC_PATH))
        self.global_offset_doubleSpinBox.setValue(api_offset)

        Config.CommonConfig.PathConfig.lyrics_file_path = ""
        Config.CommonConfig.PathConfig.temp_file_path = ""
        for name in ('spotify', 'cloudmusic', 'kugou'):
            getattr(self, f'{name}_proxy_lineEdit').setText(default_dict['ClientConfig'][f'{name}_proxy_ip'])
        self._proxy_event()

    def _proxy_event(self):
        """先校验全部地址，再更新代理，避免使用输入到一半的地址。"""
        proxies = {}
        for name in ('spotify', 'cloudmusic', 'kugou'):
            field = getattr(self, f'{name}_proxy_lineEdit')
            address = field.text().strip()
            if address:
                try:
                    url = urlsplit(address)
                    if (url.scheme not in ('http', 'https') or not url.hostname
                            or any(char.isspace() for char in address)
                            or url.port == 0 or url.path not in ('', '/') or url.query or url.fragment):
                        raise ValueError
                except ValueError:
                    self.proxy_tip_label.setText(self.tr('代理地址无效，请填写完整的 HTTP/HTTPS 地址，例如 http://127.0.0.1:7890。'))
                    field.setFocus()
                    return
            proxies[name] = address
        for name, address in proxies.items():
            setattr(Config.CommonConfig.ClientConfig, f'{name}_proxy_ip', address)
            getattr(self, f'{name}_proxy_lineEdit').setText(address)
        self.auth.load_proxy_config()
        self.proxy_tip_label.setText(self.tr('代理设置已应用，对后续请求生效；关闭设置窗口后保存。'))

    @pyqtSlot()
    def _clear_cache_event(self):
        """隔离 clicked(bool) 参数，并在页面内处理清理失败。"""
        try:
            before, after = self.temp_file_manage.clean_all_temp()
        except OSError:
            self.clear_cache_tip_label.setText(self.tr('缓存清理未完成，请检查缓存目录的访问权限后重试。'))
            self._refresh_cache_size()
        else:
            self.cache_size_label.setText(self.tr('当前缓存：{}').format(self._format_cache_size(after)))
            cleared = self._format_cache_size(max(0, before - after))
            self.clear_cache_tip_label.setText(self.tr('已清理 {} 缓存，已下载的歌词不受影响。').format(cleared))

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_cache_size()

    def _refresh_cache_size(self):
        try:
            size = self.temp_file_manage.get_cache_size()
        except OSError:
            self.cache_size_label.setText(self.tr('当前缓存：无法读取'))
        else:
            self.cache_size_label.setText(self.tr('当前缓存：{}').format(self._format_cache_size(size)))

    @staticmethod
    def _format_cache_size(size):
        if size < 1024:
            return f'{size} B'
        for unit in ('KiB', 'MiB', 'GiB', 'TiB'):
            size /= 1024
            if size < 1024 or unit == 'TiB':
                return f'{size:.1f} {unit}'

    def set_path_event(self, line_edit: QLineEdit):
        """设置路径事件"""
        self.setting_window.mask_.show()
        file_path = QFileDialog.getExistingDirectory(self, self.tr("选择一个目录"), "./", QFileDialog.Option.ShowDirsOnly)
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

    def _auto_track_sync_event(self, enabled: bool):
        Config.CommonConfig.is_auto_track_sync = enabled

    def _language_event(self):
        Config.CommonConfig.language = self.language_comboBox.currentData()

    def _theme_event(self):
        Config.CommonConfig.settings_theme = self.theme_comboBox.currentData()
        if self.setting_window is not None:
            self.setting_window._init_style_sheet()

    def path_change_tip_event(self, tip_label: QLabel):
        """修改路径事件"""
        tip_label.setText(self.tr("路径修改将在重启后生效"))

    @property
    def lyrics_file_manage(self):
        return self.lyrics_file_manage_()

    @property
    def temp_file_manage(self):
        return self.temp_file_manage_()
