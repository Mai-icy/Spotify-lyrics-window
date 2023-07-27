# coding:utf-8
import os
import sys

from PyQt5.QtCore import Qt, QLocale, QTranslator, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout

from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import isDarkTheme, FluentTranslator
from view.setting_window.setting_window_interface import SettingInterface
from common.config import cfg, Language


class SettingWindowView(FramelessWindow):
    lyric_color_changed = pyqtSignal(QColor)
    shadow_color_changed = pyqtSignal(QColor)
    lyric_font_changed = pyqtSignal(QFont)
    display_mode_changed = pyqtSignal()
    show_lyric_manager_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitleBar(StandardTitleBar(self))

        self.hBoxLayout = QHBoxLayout(self)
        self.settingInterface = SettingInterface(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.settingInterface)

        self.setWindowIcon(QIcon("resource/logo.png"))
        self.setWindowTitle(self.tr("Setting"))

        self.resize(1080, 784)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.titleBar.raise_()

        self.setQss()
        cfg.themeChanged.connect(self.setQss)

        self._init_signal()

    def _init_signal(self):
        self.settingInterface.lyric_color_changed.connect(self.lyric_color_changed)
        self.settingInterface.shadow_color_changed.connect(self.shadow_color_changed)
        self.settingInterface.lyric_font_changed.connect(self.lyric_font_changed)
        self.settingInterface.display_mode_changed.connect(self.display_mode_changed)
        self.settingInterface.show_lyric_manager_signal.connect(self.show_lyric_manager_signal)

    def setQss(self):
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == '__main__':
    # enable dpi scale
    if cfg.get(cfg.dpi_scale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", "resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    # create main window
    w = SettingWindowView()
    w.show()

    app.exec_()
