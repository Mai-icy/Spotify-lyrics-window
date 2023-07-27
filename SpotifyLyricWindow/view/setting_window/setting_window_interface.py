# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, ColorSettingCard,
                            setTheme, isDarkTheme)

from components.hotkey_setting_card import HotkeySettingCard
from common.image.extend_icon import ExtendFluentIcon as EFI
from common.config import cfg, HELP_URL


class SettingInterface(ScrollArea):
    """ Setting interface """
    lyric_color_changed = pyqtSignal(QColor)
    shadow_color_changed = pyqtSignal(QColor)
    lyric_font_changed = pyqtSignal(QFont)
    display_mode_changed = pyqtSignal()
    show_lyric_manager_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scroll_widget = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widget)

        # setting label
        self.setting_label = QLabel(self.tr("Settings"), self)

        # Account
        self.account_group = SettingCardGroup(
            self.tr("Account"), self.scroll_widget)

        self.account_login_card = PushSettingCard(
            self.tr("login"),
            EFI.PERSON,
            self.tr("API Account"),
            parent=self.account_group
        )

        self.login_help_card = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr('Get some help with login API account'),
            self.account_group
        )

        # File on this PC
        self.file_on_this_pc_group = SettingCardGroup(
            self.tr("File on this PC"), self.scroll_widget)

        self.lyric_folder_card = PushSettingCard(
            self.tr('Choose folder'),
            FIF.DOWNLOAD,
            self.tr("Lyric download directory"),
            cfg.get(cfg.lyric_folders),
            self.file_on_this_pc_group
        )

        self.temp_folder_card = PushSettingCard(
            self.tr('Choose folder'),
            EFI.FOLDER,
            self.tr("Temp download directory"),
            cfg.get(cfg.temp_folder),
            self.file_on_this_pc_group
        )

        # personalization
        self.lyric_personal_group = SettingCardGroup(self.tr('Personalization'), self.scroll_widget)

        self.enable_always_front_card = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Always front"),
            self.tr("Keep the lyrics window always at the forefront"),
            configItem=cfg.enable_always_front,
            parent=self.lyric_personal_group
        )
        self.translate_mode_card = OptionsSettingCard(
            cfg.trans_mode,
            EFI.TRANSLATE,
            self.tr('Translate Language'),
            self.tr("Change the translation language of your lyric"),
            texts=[
                self.tr('None'), self.tr('Romaji'),
                self.tr('Chinese')
            ],
            parent=self.lyric_personal_group
        )
        self.display_mode_card = OptionsSettingCard(
            cfg.display_mode,
            EFI.WINDOWSAPPS,
            self.tr('Display mode'),
            self.tr("Change the lyric display mode, vertical or horizontal"),
            texts=[
                self.tr('Vertical'), self.tr('Horizontal'),
            ],
            parent=self.lyric_personal_group
        )
        self.lyric_color_card = ColorSettingCard(
            cfg.lyric_color,
            FIF.PALETTE,
            self.tr('Lyric color'),
            self.tr('Change the color of you lyric'),
            self.lyric_personal_group
        )
        self.shadow_color_card = ColorSettingCard(
            cfg.shadow_color,
            EFI.PEN,
            self.tr('Shadow color'),
            self.tr('Change the color of you lyric'),
            self.lyric_personal_group
        )
        self.desk_lyric_font_card = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Lyric font'),
            parent=self.lyric_personal_group
        )

        self.interface_group = SettingCardGroup(self.tr('Main Panel'), self.scroll_widget)

        self.language_card = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for setting UI'),
            texts=['简体中文', 'English', self.tr('Use system setting')],
            parent=self.interface_group
        )
        self.minimize_to_tray_card = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('the lyric will continue to run in the background'),
            configItem=cfg.minimize_to_tray,
            parent=self.interface_group
        )
        self.zoom_card = OptionsSettingCard(
            cfg.dpi_scale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.interface_group
        )
        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            EFI.LIGHTBULB,
            self.tr('Application theme'),
            self.tr("Change the appearance of your setting window"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.interface_group
        )

        self.tools_group = SettingCardGroup(self.tr('Tools'), self.scroll_widget)
        self.lyric_manage_card = PushSettingCard(
            self.tr("open"),
            FIF.MUSIC,
            self.tr('Lyric manager'),
            parent=self.tools_group
        )

        self.hotkeys_group = SettingCardGroup(self.tr('Hotkeys'), self.scroll_widget)

        self.enable_hotkey_card = SwitchSettingCard(
            EFI.KEYBOARD,
            self.tr('Hotkeys'),
            configItem=cfg.enable_hotkeys,
            parent=self.hotkeys_group
        )
        self.pause_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Pause/Resume",
            "Pause or continue the song",
            cfg.pause_hotkey,
            self.hotkeys_group
            )
        self.last_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Last song",
            "Start playing the previous song",
            cfg.last_song_hotkey,
            self.hotkeys_group
            )
        self.next_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Next song",
            "Start playing the next song",
            cfg.next_song_hotkey,
            self.hotkeys_group
            )
        self.lock_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Lock",
            "Lock the lyrics window so that it cannot be dragged",
            cfg.lock_hotkey,
            self.hotkeys_group
            )
        self.calibration_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Calibration",
            "Calibrate the lyrics using the time obtained by the api",
            cfg.calibrate_hotkey,
            self.hotkeys_group
            )
        self.trans_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Switch translation",
            "Toggle the translation mode of lyrics",
            cfg.translate_hotkey,
            self.hotkeys_group
            )
        self.show_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Show",
            "Show the lyrics window",
            cfg.show_window_hotkey,
            self.hotkeys_group
        )
        self.close_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Close",
            "Close the lyrics window",
            cfg.close_window_hotkey,
            self.hotkeys_group
        )
        self.tool_hotkey_card = HotkeySettingCard(
            EFI.KEYBOARD,
            "Open Tool",
            "Open the Lyrics manager",
            cfg.open_tool_hotkey,
            self.hotkeys_group
        )
        self._init_widget()

    def _init_widget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.set_qss_event()

        # initialize layout
        self._init_layout()
        self._init_signal()

        self.set_hotkey_lineEdit_enable(cfg.get(cfg.enable_hotkeys))

    def _init_layout(self):
        self.setting_label.move(60, 63)

        # add cards to group
        self.account_group.addSettingCard(self.account_login_card)
        self.account_group.addSettingCard(self.login_help_card)

        self.file_on_this_pc_group.addSettingCard(self.lyric_folder_card)
        self.file_on_this_pc_group.addSettingCard(self.temp_folder_card)

        self.lyric_personal_group.addSettingCard(self.enable_always_front_card)
        self.lyric_personal_group.addSettingCard(self.display_mode_card)
        self.lyric_personal_group.addSettingCard(self.translate_mode_card)
        self.lyric_personal_group.addSettingCard(self.lyric_color_card)
        self.lyric_personal_group.addSettingCard(self.shadow_color_card)
        self.lyric_personal_group.addSettingCard(self.desk_lyric_font_card)

        self.interface_group.addSettingCard(self.language_card)
        self.interface_group.addSettingCard(self.minimize_to_tray_card)
        self.interface_group.addSettingCard(self.zoom_card)
        self.interface_group.addSettingCard(self.theme_card)
        self.hotkeys_group.addSettingCard(self.enable_hotkey_card)
        self.hotkeys_group.addSettingCard(self.pause_hotkey_card)
        self.hotkeys_group.addSettingCard(self.last_hotkey_card)
        self.hotkeys_group.addSettingCard(self.next_hotkey_card)
        self.hotkeys_group.addSettingCard(self.lock_hotkey_card)
        self.hotkeys_group.addSettingCard(self.lock_hotkey_card)
        self.hotkeys_group.addSettingCard(self.calibration_hotkey_card)
        self.hotkeys_group.addSettingCard(self.trans_hotkey_card)
        self.hotkeys_group.addSettingCard(self.show_hotkey_card)
        self.hotkeys_group.addSettingCard(self.close_hotkey_card)
        self.hotkeys_group.addSettingCard(self.tool_hotkey_card)

        self.tools_group.addSettingCard(self.lyric_manage_card)

        # add setting card group to layout
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)
        self.expand_layout.addWidget(self.account_group)
        self.expand_layout.addWidget(self.file_on_this_pc_group)
        self.expand_layout.addWidget(self.lyric_personal_group)
        self.expand_layout.addWidget(self.interface_group)
        self.expand_layout.addWidget(self.hotkeys_group)
        self.expand_layout.addWidget(self.tools_group)

    def _init_signal(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.show_restart_tooltip_event)
        cfg.themeChanged.connect(self.theme_changed_event)

        self.lyric_folder_card.clicked.connect(self.lyric_folder_card_clicked_event)
        self.temp_folder_card.clicked.connect(self.temp_folder_card_clicked_event)
        self.lyric_color_card.colorChanged.connect(self.lyric_color_changed)
        self.shadow_color_card.colorChanged.connect(self.shadow_color_changed)
        self.display_mode_card.optionChanged.connect(self.display_mode_changed)
        self.desk_lyric_font_card.clicked.connect(self.lyric_font_card_clicked_event)
        self.lyric_manage_card.clicked.connect(self.show_lyric_manager_signal)
        self.enable_hotkey_card.checkedChanged.connect(self.set_hotkey_lineEdit_enable)

    def set_qss_event(self):
        """ set style sheet """
        self.scroll_widget.setObjectName('scrollWidget')
        self.setting_label.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def set_hotkey_lineEdit_enable(self, flag: bool):
        hotkeys_cards = [self.trans_hotkey_card, self.show_hotkey_card, self.close_hotkey_card,
                         self.tool_hotkey_card, self.next_hotkey_card, self.lock_hotkey_card,
                         self.last_hotkey_card, self.calibration_hotkey_card, self.pause_hotkey_card]
        for card in hotkeys_cards:
            card.setEnabled(flag)

    def show_restart_tooltip_event(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def lyric_font_card_clicked_event(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            cfg.lyric_font, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.lyric_font = font
            self.lyric_font_changed.emit(font)

    def lyric_folder_card_clicked_event(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.lyric_folders) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def temp_folder_card_clicked_event(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.temp_folder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def theme_changed_event(self, theme: Theme):
        """ theme changed slot """
        setTheme(theme)

        # chang the theme of setting interface
        self.set_qss_event()
