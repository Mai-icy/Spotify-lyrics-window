# Form implementation generated from reading ui file 'E:\code\git-code\Spotify-lyrics-window\SpotifyLyricWindow\resource\ui\ui_file\LyricsSettingsPage.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LyricsSettingsPage(object):
    def setupUi(self, LyricsSettingsPage):
        LyricsSettingsPage.setObjectName("LyricsSettingsPage")
        LyricsSettingsPage.resize(875, 604)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        LyricsSettingsPage.setFont(font)
        self.lyricssettingspage_gridLayout = QtWidgets.QGridLayout(LyricsSettingsPage)
        self.lyricssettingspage_gridLayout.setContentsMargins(50, 40, 50, 40)
        self.lyricssettingspage_gridLayout.setSpacing(0)
        self.lyricssettingspage_gridLayout.setObjectName("lyricssettingspage_gridLayout")
        self.change_color_frame = QtWidgets.QFrame(parent=LyricsSettingsPage)
        self.change_color_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.change_color_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.change_color_frame.setObjectName("change_color_frame")
        self.changecolor_gridLayout = QtWidgets.QGridLayout(self.change_color_frame)
        self.changecolor_gridLayout.setObjectName("changecolor_gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.changecolor_gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.color_label = QtWidgets.QLabel(parent=self.change_color_frame)
        self.color_label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.color_label.setObjectName("color_label")
        self.changecolor_gridLayout.addWidget(self.color_label, 0, 0, 1, 2)
        self.lyrics_default_button = QtWidgets.QPushButton(parent=self.change_color_frame)
        self.lyrics_default_button.setMinimumSize(QtCore.QSize(100, 32))
        self.lyrics_default_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lyrics_default_button.setObjectName("lyrics_default_button")
        self.changecolor_gridLayout.addWidget(self.lyrics_default_button, 1, 4, 1, 1)
        self.shadow_color_frame = QtWidgets.QFrame(parent=self.change_color_frame)
        self.shadow_color_frame.setMaximumSize(QtCore.QSize(132, 32))
        self.shadow_color_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.shadow_color_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.shadow_color_frame.setObjectName("shadow_color_frame")
        self.shadowcolor_horizontalLayout = QtWidgets.QHBoxLayout(self.shadow_color_frame)
        self.shadowcolor_horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.shadowcolor_horizontalLayout.setSpacing(0)
        self.shadowcolor_horizontalLayout.setObjectName("shadowcolor_horizontalLayout")
        self.shadow_color_label = QtWidgets.QLabel(parent=self.shadow_color_frame)
        self.shadow_color_label.setMinimumSize(QtCore.QSize(32, 32))
        self.shadow_color_label.setMaximumSize(QtCore.QSize(32, 32))
        self.shadow_color_label.setText("")
        self.shadow_color_label.setObjectName("shadow_color_label")
        self.shadowcolor_horizontalLayout.addWidget(self.shadow_color_label)
        self.shadow_color_button = QtWidgets.QPushButton(parent=self.shadow_color_frame)
        self.shadow_color_button.setMinimumSize(QtCore.QSize(100, 32))
        self.shadow_color_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.shadow_color_button.setObjectName("shadow_color_button")
        self.shadowcolor_horizontalLayout.addWidget(self.shadow_color_button)
        self.changecolor_gridLayout.addWidget(self.shadow_color_frame, 1, 2, 1, 1)
        self.lyrics_color_frame = QtWidgets.QFrame(parent=self.change_color_frame)
        self.lyrics_color_frame.setMaximumSize(QtCore.QSize(132, 32))
        self.lyrics_color_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.lyrics_color_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.lyrics_color_frame.setObjectName("lyrics_color_frame")
        self.lyricscolor_horizontalLayout = QtWidgets.QHBoxLayout(self.lyrics_color_frame)
        self.lyricscolor_horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.lyricscolor_horizontalLayout.setSpacing(0)
        self.lyricscolor_horizontalLayout.setObjectName("lyricscolor_horizontalLayout")
        self.lyrics_color_label = QtWidgets.QLabel(parent=self.lyrics_color_frame)
        self.lyrics_color_label.setMinimumSize(QtCore.QSize(32, 32))
        self.lyrics_color_label.setMaximumSize(QtCore.QSize(32, 32))
        self.lyrics_color_label.setText("")
        self.lyrics_color_label.setObjectName("lyrics_color_label")
        self.lyricscolor_horizontalLayout.addWidget(self.lyrics_color_label)
        self.lyrics_color_button = QtWidgets.QPushButton(parent=self.lyrics_color_frame)
        self.lyrics_color_button.setMinimumSize(QtCore.QSize(100, 32))
        self.lyrics_color_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lyrics_color_button.setObjectName("lyrics_color_button")
        self.lyricscolor_horizontalLayout.addWidget(self.lyrics_color_button)
        self.changecolor_gridLayout.addWidget(self.lyrics_color_frame, 1, 1, 1, 1)
        self.color_comboBox = QtWidgets.QComboBox(parent=self.change_color_frame)
        self.color_comboBox.setMinimumSize(QtCore.QSize(100, 32))
        self.color_comboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.color_comboBox.setObjectName("color_comboBox")
        self.changecolor_gridLayout.addWidget(self.color_comboBox, 1, 0, 1, 1)
        self.lyricssettingspage_gridLayout.addWidget(self.change_color_frame, 6, 0, 1, 1)
        self.lyrics_trans_frame = QtWidgets.QFrame(parent=LyricsSettingsPage)
        self.lyrics_trans_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.lyrics_trans_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.lyrics_trans_frame.setObjectName("lyrics_trans_frame")
        self.lyricstrans_verticalLayout = QtWidgets.QVBoxLayout(self.lyrics_trans_frame)
        self.lyricstrans_verticalLayout.setObjectName("lyricstrans_verticalLayout")
        self.lyrics_trans_label = QtWidgets.QLabel(parent=self.lyrics_trans_frame)
        self.lyrics_trans_label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.lyrics_trans_label.setObjectName("lyrics_trans_label")
        self.lyricstrans_verticalLayout.addWidget(self.lyrics_trans_label)
        self.non_trans_radioButton = QtWidgets.QRadioButton(parent=self.lyrics_trans_frame)
        self.non_trans_radioButton.setObjectName("non_trans_radioButton")
        self.lyricstrans_verticalLayout.addWidget(self.non_trans_radioButton)
        self.trans_radioButton = QtWidgets.QRadioButton(parent=self.lyrics_trans_frame)
        self.trans_radioButton.setObjectName("trans_radioButton")
        self.lyricstrans_verticalLayout.addWidget(self.trans_radioButton)
        self.romaji_radioButton = QtWidgets.QRadioButton(parent=self.lyrics_trans_frame)
        self.romaji_radioButton.setObjectName("romaji_radioButton")
        self.lyricstrans_verticalLayout.addWidget(self.romaji_radioButton)
        self.lyricssettingspage_gridLayout.addWidget(self.lyrics_trans_frame, 0, 0, 1, 1)
        self.font_frame = QtWidgets.QFrame(parent=LyricsSettingsPage)
        self.font_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.font_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.font_frame.setObjectName("font_frame")
        self.font_verticalLayout = QtWidgets.QVBoxLayout(self.font_frame)
        self.font_verticalLayout.setObjectName("font_verticalLayout")
        self.font_label = QtWidgets.QLabel(parent=self.font_frame)
        self.font_label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.font_label.setObjectName("font_label")
        self.font_verticalLayout.addWidget(self.font_label)
        self.font_comboBox = QtWidgets.QComboBox(parent=self.font_frame)
        self.font_comboBox.setMinimumSize(QtCore.QSize(0, 32))
        self.font_comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.font_comboBox.setObjectName("font_comboBox")
        self.font_verticalLayout.addWidget(self.font_comboBox)
        self.lyricssettingspage_gridLayout.addWidget(self.font_frame, 4, 0, 1, 1)
        self.always_front_frame = QtWidgets.QFrame(parent=LyricsSettingsPage)
        self.always_front_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.always_front_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.always_front_frame.setObjectName("always_front_frame")
        self.alwaysfront_verticalLayout = QtWidgets.QVBoxLayout(self.always_front_frame)
        self.alwaysfront_verticalLayout.setObjectName("alwaysfront_verticalLayout")
        self.always_front_label = QtWidgets.QLabel(parent=self.always_front_frame)
        self.always_front_label.setMaximumSize(QtCore.QSize(16777215, 20))
        self.always_front_label.setObjectName("always_front_label")
        self.alwaysfront_verticalLayout.addWidget(self.always_front_label)
        self.enable_front_checkBox = QtWidgets.QCheckBox(parent=self.always_front_frame)
        self.enable_front_checkBox.setObjectName("enable_front_checkBox")
        self.alwaysfront_verticalLayout.addWidget(self.enable_front_checkBox)
        self.lyricssettingspage_gridLayout.addWidget(self.always_front_frame, 2, 0, 1, 1)
        self.display_mode_frame = QtWidgets.QFrame(parent=LyricsSettingsPage)
        self.display_mode_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.display_mode_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.display_mode_frame.setObjectName("display_mode_frame")
        self.display_mode_verticalLayout = QtWidgets.QVBoxLayout(self.display_mode_frame)
        self.display_mode_verticalLayout.setObjectName("display_mode_verticalLayout")
        self.display_mode_label = QtWidgets.QLabel(parent=self.display_mode_frame)
        self.display_mode_label.setObjectName("display_mode_label")
        self.display_mode_verticalLayout.addWidget(self.display_mode_label)
        self.display_mode_comboBox = QtWidgets.QComboBox(parent=self.display_mode_frame)
        self.display_mode_comboBox.setMinimumSize(QtCore.QSize(0, 32))
        self.display_mode_comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.display_mode_comboBox.setObjectName("display_mode_comboBox")
        self.display_mode_comboBox.addItem("")
        self.display_mode_comboBox.addItem("")
        self.display_mode_verticalLayout.addWidget(self.display_mode_comboBox)
        self.lyricssettingspage_gridLayout.addWidget(self.display_mode_frame, 3, 0, 1, 1)

        self.retranslateUi(LyricsSettingsPage)
        self.color_comboBox.setCurrentIndex(-1)
        self.font_comboBox.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(LyricsSettingsPage)

    def retranslateUi(self, LyricsSettingsPage):
        _translate = QtCore.QCoreApplication.translate
        LyricsSettingsPage.setWindowTitle(_translate("LyricsSettingsPage", "LyricsSettingsPage"))
        self.color_label.setText(_translate("LyricsSettingsPage", "更改歌词颜色:"))
        self.lyrics_default_button.setText(_translate("LyricsSettingsPage", "恢复默认"))
        self.shadow_color_button.setText(_translate("LyricsSettingsPage", "阴影"))
        self.lyrics_color_button.setText(_translate("LyricsSettingsPage", "歌词"))
        self.lyrics_trans_label.setText(_translate("LyricsSettingsPage", "歌词翻译:"))
        self.non_trans_radioButton.setText(_translate("LyricsSettingsPage", "不显示翻译"))
        self.trans_radioButton.setText(_translate("LyricsSettingsPage", "显示中文翻译"))
        self.romaji_radioButton.setText(_translate("LyricsSettingsPage", "显示罗马音译"))
        self.font_label.setText(_translate("LyricsSettingsPage", "字体:"))
        self.always_front_label.setText(_translate("LyricsSettingsPage", "总在最前:"))
        self.enable_front_checkBox.setText(_translate("LyricsSettingsPage", "启用总在最前"))
        self.display_mode_label.setText(_translate("LyricsSettingsPage", "显示模式:"))
        self.display_mode_comboBox.setItemText(0, _translate("LyricsSettingsPage", "横排歌词"))
        self.display_mode_comboBox.setItemText(1, _translate("LyricsSettingsPage", "竖排歌词"))
