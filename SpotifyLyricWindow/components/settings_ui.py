"""Settings presentation only; the page classes retain all configuration/actions.

These hand-written layouts replace the generated settings forms, not the lyrics
overlay. Existing control names and value ordering are deliberately preserved.
"""
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QCheckBox, QRadioButton, QComboBox,
    QLineEdit, QDoubleSpinBox, QPlainTextEdit, QListWidget, QListWidgetItem,
    QStackedWidget, QScrollArea, QSplitter, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy, QAbstractItemView,
)


ASSET_PATH = Path(__file__).resolve().parents[1] / 'resource' / 'ui' / 'settings'


def label(text, role='body', parent=None):
    widget = QLabel(text, parent)
    widget.setProperty('role', role)
    widget.setWordWrap(True)
    widget.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    return widget


def control(owner, name, widget):
    widget.setObjectName(name)
    setattr(owner, name, widget)
    return widget


def button(owner, name, text, role='secondary'):
    widget = control(owner, name, QPushButton(text))
    widget.setProperty('role', role)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    return widget


def horizontal(*widgets):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)
    for widget in widgets:
        layout.addWidget(widget)
    return container


def page_layout(page):
    page.setProperty('settingsPage', True)
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)
    return layout


def section(layout, title):
    layout.addWidget(label(title, 'section'))
    card = QFrame()
    card.setProperty('settingCard', True)
    rows = QVBoxLayout(card)
    rows.setContentsMargins(20, 4, 20, 4)
    rows.setSpacing(0)
    layout.addWidget(card)
    return rows


def row(layout, title, widget, description='', stacked=False):
    frame = QFrame()
    frame.setProperty('settingRow', True)
    contents = QVBoxLayout(frame) if stacked else QHBoxLayout(frame)
    contents.setContentsMargins(0, 16, 0, 16)
    contents.setSpacing(12)
    text = QWidget()
    texts = QVBoxLayout(text)
    texts.setContentsMargins(0, 0, 0, 0)
    texts.setSpacing(4)
    heading = label(title)
    heading.setBuddy(widget)
    texts.addWidget(heading)
    if description:
        texts.addWidget(label(description, 'muted'))
    if stacked:
        contents.addWidget(text)
        contents.addWidget(widget)
    else:
        contents.addWidget(text, 1)
        contents.addWidget(widget, 0, Qt.AlignmentFlag.AlignVCenter)
    layout.addWidget(frame)
    return frame


def combo(owner, name, items=()):
    widget = control(owner, name, QComboBox())
    widget.addItems(items)
    widget.setMinimumWidth(200)
    widget.setMaximumWidth(280)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return widget


def scroll_page(page):
    scroll = QScrollArea()
    scroll.setObjectName('settingsScroll')
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(page)
    return scroll


class Ui_SettingsWindow:
    def setupUi(self, window):
        tr = window.tr
        window.setObjectName('SettingsWindow')
        window.setWindowTitle(tr('设置 · Spotify Lyrics'))
        window.setWindowIcon(QIcon(':/pic/images/LyricsIcon.png'))
        window.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont))
        window.resize(1080, 780)
        window.setMinimumSize(860, 580)
        root = QHBoxLayout(window)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName('settingsSidebar')
        sidebar.setFixedWidth(208)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 28, 16, 20)
        side.setSpacing(8)
        brand = horizontal(label('♪', 'brandMark'), label('Spotify Lyrics', 'brand'))
        side.addWidget(brand)
        side.addSpacing(24)
        side.addWidget(label(tr('偏好设置'), 'eyebrow'))
        self.page_listWidget = QListWidget()
        self.page_listWidget.setObjectName('settingsNavigation')
        self.page_listWidget.setIconSize(QSize(18, 18))
        self.page_listWidget.setSpacing(4)
        self.page_listWidget.setFrameShape(QFrame.Shape.NoFrame)
        self.page_listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.page_listWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for text, icon in [(tr('常规'), 'general'), (tr('快捷键'), 'keyboard'),
                           (tr('歌词外观'), 'appearance'), (tr('歌词管理'), 'library')]:
            item = QListWidgetItem(QIcon(str(ASSET_PATH / f'{icon}.svg')), text)
            item.setSizeHint(QSize(168, 44))
            self.page_listWidget.addItem(item)
        side.addWidget(self.page_listWidget, 1)
        side.addWidget(label(tr('让歌词，陪伴每一次聆听。'), 'muted'))
        root.addWidget(sidebar)
        body = QWidget()
        body.setObjectName('settingsBody')
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(32, 28, 28, 20)
        body_layout.setSpacing(12)
        eyebrow = label(tr('个性化你的桌面歌词'), 'eyebrow')
        eyebrow.setMinimumHeight(16)
        body_layout.addWidget(eyebrow)
        self.page_title = label('', 'pageTitle')
        self.page_description = label('', 'muted')
        self.page_title.setMinimumHeight(36)
        self.page_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.page_description.setMinimumHeight(20)
        self.page_description.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        body_layout.addWidget(self.page_title)
        body_layout.addWidget(self.page_description)
        body_layout.addSpacing(12)
        self.page_stackedWidget = QStackedWidget()
        self.page_stackedWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body_layout.addWidget(self.page_stackedWidget, 1)
        body_layout.addSpacing(4)
        body_layout.addWidget(label(tr('外观设置即时生效 · 路径变更需重启 · 关闭窗口保存配置'), 'footer'))
        root.addWidget(body, 1)


class Ui_CommonPage:
    def setupUi(self, page):
        tr = page.tr
        layout = page_layout(page)
        group = section(layout, tr('窗口行为'))
        row(group, tr('记住窗口位置'), control(self, 'save_position_checkBox', QCheckBox(tr('启用'))),
            tr('下次启动时恢复歌词窗口的位置。'))
        row(group, tr('关闭时退出程序'), control(self, 'quit_on_close_checkBox', QCheckBox(tr('启用'))),
            tr('关闭歌词窗口时退出，而不是隐藏到托盘。'))
        group = section(layout, tr('播放同步'))
        offset = control(self, 'global_offset_doubleSpinBox', QDoubleSpinBox())
        offset.setRange(-30, 30)
        offset.setSingleStep(.5)
        offset.setSuffix(tr(' 秒'))
        offset.setFixedWidth(150)
        row(group, tr('全局歌词偏移'), offset, tr('统一调整歌词时间，正值使歌词提前显示。'))
        group = section(layout, tr('存储与缓存'))
        for prefix, title in [('lyrics', tr('歌词保存位置')), ('cache', tr('缓存位置'))]:
            path = control(self, f'{prefix}_path_lineEdit', QLineEdit())
            path.setMinimumWidth(0)
            choose = button(self, f'{prefix}_path_button', tr('选择目录'))
            value = horizontal(path, choose)
            value.layout().setStretch(0, 1)
            row(group, title, value, stacked=True)
            tip = control(self, f'{prefix}_tip_label', label('', 'notice'))
            group.addWidget(tip)
        row(group, tr('清理缓存'), button(self, 'clear_cache_button', tr('清理缓存')),
            tr('清除临时文件，保留已下载的歌词。'))
        group = section(layout, tr('Spotify 连接'))
        for name, title in [('id_lineEdit', 'Client ID'), ('secret_lineEdit', 'Client Secret')]:
            field = control(self, name, QLineEdit())
            field.setPlaceholderText(tr('填写 Spotify 应用凭据'))
            row(group, title, field, stacked=True)
        links = QWidget()
        links_layout = QHBoxLayout(links)
        links_layout.setContentsMargins(0, 12, 0, 16)
        self.register_label = control(self, 'register_label', QLabel())
        links_layout.addWidget(self.register_label)
        links_layout.addStretch()
        links_layout.addWidget(button(self, 'confirm_button', tr('应用连接配置'), 'primary'))
        group.addWidget(links)
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(button(self, 'default_button', tr('恢复常规默认设置')))
        layout.addLayout(footer)
        layout.addStretch()


class Ui_LyricsSettingsPage:
    def setupUi(self, page):
        tr = page.tr
        layout = page_layout(page)
        group = section(layout, tr('显示方式'))
        row(group, tr('歌词方向'), combo(self, 'display_mode_comboBox', [tr('横排歌词'), tr('竖排歌词')]),
            tr('选择适合桌面布局的阅读方向。'))
        row(group, tr('始终置顶'), control(self, 'enable_front_checkBox', QCheckBox(tr('启用'))),
            tr('让歌词显示在其他应用窗口上方。'))
        group = section(layout, tr('字体与翻译'))
        row(group, tr('歌词字体'), combo(self, 'font_comboBox'))
        row(group, tr('译文字体'), combo(self, 'translation_font_comboBox'))
        options = horizontal(
            control(self, 'non_trans_radioButton', QRadioButton(tr('不显示'))),
            control(self, 'trans_radioButton', QRadioButton(tr('中文'))),
            control(self, 'romaji_radioButton', QRadioButton(tr('罗马音'))))
        row(group, tr('歌词翻译'), options)
        group = section(layout, tr('颜色'))
        row(group, tr('配色方案'), combo(self, 'color_comboBox'), tr('使用预设配色，或自定义歌词与阴影颜色。'))
        colors = []
        for prefix, title in [('lyrics', tr('歌词颜色')), ('shadow', tr('阴影颜色'))]:
            swatch = control(self, f'{prefix}_color_label', QLabel())
            swatch.setFixedSize(24, 24)
            swatch.setAccessibleName(title)
            colors.append(horizontal(swatch, button(self, f'{prefix}_color_button', title)))
        row(group, tr('自定义颜色'), horizontal(*colors))
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(button(self, 'lyrics_default_button', tr('恢复外观默认设置')))
        layout.addLayout(footer)
        layout.addStretch()
        for widget in (self.color_comboBox, self.font_comboBox, self.translation_font_comboBox):
            widget.setCurrentIndex(-1)


class Ui_HotkeysPage:
    def setupUi(self, page):
        tr = page.tr
        layout = page_layout(page)
        group = section(layout, tr('全局快捷键'))
        row(group, tr('启用快捷键'), control(self, 'enable_hotkeys_checkBox', QCheckBox(tr('启用'))),
            tr('在其他应用中也能控制桌面歌词。'))
        layout.addWidget(label(tr('点击右侧输入框，再按下组合键。重复的组合键会从原操作中移除。'), 'muted'))
        group = section(layout, tr('按键绑定'))
        columns = QWidget()
        grid = QGridLayout(columns)
        grid.setContentsMargins(0, 16, 0, 16)
        grid.setHorizontalSpacing(24)
        self.hotkeyslineedit_frame = QWidget()
        self.HotkeysLineEditFrameVerticalLayout = QVBoxLayout(self.hotkeyslineedit_frame)
        self.HotkeysLineEditFrameVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.HotkeysLineEditFrameVerticalLayout.setSpacing(12)
        labels = QWidget()
        names = QVBoxLayout(labels)
        names.setContentsMargins(0, 0, 0, 0)
        names.setSpacing(12)
        for title in [tr('暂停 / 继续'), tr('上一首'), tr('下一首'), tr('锁定歌词窗口'),
                      tr('校准进度'), tr('切换翻译'), tr('显示歌词窗口'), tr('关闭歌词窗口')]:
            item = label(title)
            item.setFixedHeight(32)
            names.addWidget(item)
        grid.addWidget(labels, 0, 0)
        grid.addWidget(self.hotkeyslineedit_frame, 0, 1)
        grid.setColumnStretch(0, 1)
        group.addWidget(columns)
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(button(self, 'hotkeys_default_button', tr('恢复快捷键默认设置')))
        layout.addLayout(footer)
        layout.addStretch()


class Ui_LyricsManage:
    def setupUi(self, page):
        tr = page.tr
        layout = page_layout(page)
        toolbar = QHBoxLayout()
        toolbar.addWidget(button(self, 'download_button', tr('下载歌词'), 'primary'))
        toolbar.addStretch()
        toolbar.addWidget(button(self, 'export_button', tr('导出')))
        toolbar.addWidget(button(self, 'modify_button', tr('编辑歌词')))
        toolbar.addWidget(button(self, 'delete_button', tr('删除'), 'danger'))
        layout.addLayout(toolbar)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        library = QWidget()
        library.setMinimumWidth(180)
        left = QVBoxLayout(library)
        left.setContentsMargins(0, 0, 8, 0)
        left.setSpacing(12)
        search = control(self, 'filter_lineEdit', QLineEdit())
        search.setPlaceholderText(tr('搜索本地歌词…'))
        search.setClearButtonEnabled(True)
        left.addWidget(search)
        left.addWidget(control(self, 'lyrics_listWidget', QListWidget()), 1)
        splitter.addWidget(library)
        editor = QWidget()
        right = QVBoxLayout(editor)
        right.setContentsMargins(8, 0, 0, 0)
        right.setSpacing(12)
        options = QHBoxLayout()
        modes = combo(self, 'show_comboBox', [tr('原文'), tr('罗马音'), tr('中文翻译')])
        modes.setMinimumWidth(100)
        options.addWidget(modes, 1)
        options.addWidget(label(tr('偏移')))
        offset = control(self, 'offset_doubleSpinBox', QDoubleSpinBox())
        offset.setRange(-1000, 1000)
        offset.setSingleStep(.5)
        offset.setSuffix(tr(' 秒'))
        offset.setFixedWidth(110)
        options.addWidget(offset)
        right.addLayout(options)
        text = control(self, 'lyrics_plainTextEdit', QPlainTextEdit())
        text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        text.setPlaceholderText(tr('选择一首歌曲，查看或编辑歌词。'))
        right.addWidget(text, 1)
        self.textbuttons_frame = QWidget()
        actions = QHBoxLayout(self.textbuttons_frame)
        actions.setContentsMargins(0, 0, 0, 0)
        actions.addStretch()
        actions.addWidget(button(self, 'cancel_button', tr('取消编辑')))
        actions.addWidget(button(self, 'confirm_button', tr('保存歌词'), 'primary'))
        right.addWidget(self.textbuttons_frame)
        splitter.addWidget(editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([240, 480])
        layout.addWidget(splitter, 1)
        music = QFrame()
        music.setProperty('settingCard', True)
        info = QHBoxLayout(music)
        info.setContentsMargins(16, 12, 16, 12)
        cover = control(self, 'image_label', QLabel())
        cover.setFixedSize(64, 64)
        cover.setObjectName('settingsCover')
        info.addWidget(cover)
        texts = QVBoxLayout()
        texts.addWidget(control(self, 'songname_label', label('', 'section')))
        texts.addWidget(control(self, 'singer_label', label('', 'muted')))
        info.addLayout(texts, 1)
        layout.addWidget(music)
