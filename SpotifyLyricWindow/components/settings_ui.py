"""Settings presentation only; the page classes retain all configuration/actions.

These hand-written layouts replace the generated settings forms, not the lyrics
overlay. Existing control names and value ordering are deliberately preserved.
"""
from pathlib import Path

from common.ui.i18n import LANGUAGES

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFontDatabase, QFontMetrics, QIcon, QPainter, QPalette
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QCheckBox, QRadioButton, QComboBox,
    QLineEdit, QDoubleSpinBox, QPlainTextEdit, QListWidget, QListWidgetItem,
    QStackedWidget, QScrollArea, QSplitter, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem, QStyle,
)


ASSET_PATH = Path(__file__).resolve().parents[1] / 'resource' / 'ui' / 'settings'
MISSING_LYRICS_ROLE = Qt.ItemDataRole.UserRole + 1


class LyricsStatusDelegate(QStyledItemDelegate):
    """Decorate missing lyrics without changing titles used by search/export."""

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        # Let the viewport set the width so long titles elide instead of scroll.
        size.setWidth(0)
        if index.data(MISSING_LYRICS_ROLE):
            size.setHeight(max(size.height(), option.fontMetrics.height() * 2 + 24))
        return size

    def paint(self, painter, option, index):
        if not index.data(MISSING_LYRICS_ROLE):
            return super().paint(painter, option, index)
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        hovered = bool(opt.state & QStyle.StateFlag.State_MouseOver)
        dark = opt.palette.color(QPalette.ColorRole.Base).lightness() < 128
        background = '#d5e8de' if selected else ('#faedd8' if hovered else '#fff5e6')
        if dark:
            background = '#264f78' if selected else ('#40392d' if hovered else '#332e25')
        rect = opt.rect.adjusted(0, 2, 0, -2)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(background))
        painter.drawRoundedRect(rect, 4, 4)
        if opt.state & QStyle.StateFlag.State_HasFocus:
            painter.setPen(QColor('#007fd4' if dark else '#398765'))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 4, 4)
        title = rect.adjusted(6, 6, -6, 0)
        title.setHeight(opt.fontMetrics.height())
        painter.setFont(opt.font)
        title_color = ('#e4effa' if selected else '#ead7b4') if dark else ('#183c32' if selected else '#58482f')
        painter.setPen(QColor(title_color))
        painter.drawText(title, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         opt.fontMetrics.elidedText(opt.text, Qt.TextElideMode.ElideRight, title.width()))
        font = opt.font
        font.setPixelSize(11)
        font.setBold(False)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        status = self.tr('无歌词')
        badge = rect.adjusted(6, 0, 0, 0)
        badge.setTop(title.bottom() + 5)
        badge.setSize(QSize(metrics.horizontalAdvance(status) + 12, metrics.height() + 4))
        painter.setPen(Qt.PenStyle.NoPen)
        badge_color = ('#305d84' if selected else '#51422a') if dark else ('#bddbca' if selected else '#f7e5c5')
        painter.setBrush(QColor(badge_color))
        painter.drawRoundedRect(badge, 4, 4)
        badge_text = ('#c7e1f5' if selected else '#edc885') if dark else ('#236347' if selected else '#896027')
        painter.setPen(QColor(badge_text))
        painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, status)
        painter.restore()


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
        body_layout.addWidget(label(tr('外观设置即时生效 · 语言和路径变更需重启 · 关闭窗口保存配置'), 'footer'))
        root.addWidget(body, 1)


class Ui_CommonPage:
    def setupUi(self, page):
        tr = page.tr
        layout = page_layout(page)
        group = section(layout, tr('界面'))
        themes = combo(self, 'theme_comboBox')
        themes.addItem(tr('浅色'), 'light')
        themes.addItem(tr('深色'), 'dark')
        row(group, tr('界面主题'), themes, tr('仅调整设置界面，不改变桌面歌词配色。'))
        languages = combo(self, 'language_comboBox')
        for code, name in LANGUAGES:
            languages.addItem(name, code)
        row(group, tr('语言 / Language'), languages, tr('重启程序后生效，不改变歌词内容或翻译模式。'))
        group = section(layout, tr('窗口行为'))
        row(group, tr('记住窗口位置'), control(self, 'save_position_checkBox', QCheckBox(tr('启用'))),
            tr('下次启动时恢复歌词窗口的位置。'))
        row(group, tr('关闭时退出程序'), control(self, 'quit_on_close_checkBox', QCheckBox(tr('启用'))),
            tr('关闭歌词窗口时退出，而不是隐藏到托盘。'))
        group = section(layout, tr('播放同步'))
        row(group, tr('自动切歌同步修正'),
            control(self, 'auto_track_sync_checkBox', QCheckBox(tr('启用'))),
            tr('自动切歌后等待约 0.7 秒，将歌曲和歌词重新定位到开头。关闭后可能出现歌词时间偏差。'))
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
        files = control(self, 'lyrics_listWidget', QListWidget())
        files.setItemDelegate(LyricsStatusDelegate(files))
        left.addWidget(files, 1)
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
