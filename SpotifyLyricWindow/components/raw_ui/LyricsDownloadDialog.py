# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LyricsDownloadDialog(object):
    def setupUi(self, LyricsDownloadDialog):
        LyricsDownloadDialog.setObjectName("LyricsDownloadDialog")
        LyricsDownloadDialog.resize(337, 473)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        LyricsDownloadDialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/images/LyricsIcon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LyricsDownloadDialog.setWindowIcon(icon)
        LyricsDownloadDialog.setSizeGripEnabled(True)
        LyricsDownloadDialog.setModal(True)
        self.lyricsdownload_gridLayout = QtWidgets.QGridLayout(LyricsDownloadDialog)
        self.lyricsdownload_gridLayout.setObjectName("lyricsdownload_gridLayout")
        self.buttons_frame = QtWidgets.QFrame(LyricsDownloadDialog)
        self.buttons_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttons_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttons_frame.setObjectName("buttons_frame")
        self.buttons_horizontalLayout = QtWidgets.QHBoxLayout(self.buttons_frame)
        self.buttons_horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.buttons_horizontalLayout.setSpacing(10)
        self.buttons_horizontalLayout.setObjectName("buttons_horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(163, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_horizontalLayout.addItem(spacerItem)
        self.download_button = QtWidgets.QPushButton(self.buttons_frame)
        self.download_button.setMinimumSize(QtCore.QSize(80, 32))
        self.download_button.setMaximumSize(QtCore.QSize(80, 32))
        self.download_button.setObjectName("download_button")
        self.buttons_horizontalLayout.addWidget(self.download_button)
        self.cancel_button = QtWidgets.QPushButton(self.buttons_frame)
        self.cancel_button.setMinimumSize(QtCore.QSize(80, 32))
        self.cancel_button.setMaximumSize(QtCore.QSize(80, 32))
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_horizontalLayout.addWidget(self.cancel_button)
        self.lyricsdownload_gridLayout.addWidget(self.buttons_frame, 3, 0, 1, 2)
        self.search_button = QtWidgets.QPushButton(LyricsDownloadDialog)
        self.search_button.setMinimumSize(QtCore.QSize(0, 32))
        self.search_button.setMaximumSize(QtCore.QSize(80, 32))
        self.search_button.setObjectName("search_button")
        self.lyricsdownload_gridLayout.addWidget(self.search_button, 0, 1, 1, 1)
        self.search_lineEdit = QtWidgets.QLineEdit(LyricsDownloadDialog)
        self.search_lineEdit.setMinimumSize(QtCore.QSize(0, 32))
        self.search_lineEdit.setMaximumSize(QtCore.QSize(16777215, 32))
        self.search_lineEdit.setObjectName("search_lineEdit")
        self.lyricsdownload_gridLayout.addWidget(self.search_lineEdit, 0, 0, 1, 1)
        self.music_frame = QtWidgets.QFrame(LyricsDownloadDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.music_frame.sizePolicy().hasHeightForWidth())
        self.music_frame.setSizePolicy(sizePolicy)
        self.music_frame.setMinimumSize(QtCore.QSize(0, 64))
        self.music_frame.setMaximumSize(QtCore.QSize(16777215, 64))
        self.music_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.music_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.music_frame.setObjectName("music_frame")
        self.music_gridLayout = QtWidgets.QGridLayout(self.music_frame)
        self.music_gridLayout.setContentsMargins(0, 0, 0, 0)
        self.music_gridLayout.setHorizontalSpacing(10)
        self.music_gridLayout.setVerticalSpacing(0)
        self.music_gridLayout.setObjectName("music_gridLayout")
        self.singer_label = QtWidgets.QLabel(self.music_frame)
        self.singer_label.setMinimumSize(QtCore.QSize(0, 32))
        self.singer_label.setMaximumSize(QtCore.QSize(16777215, 32))
        self.singer_label.setText("")
        self.singer_label.setObjectName("singer_label")
        self.music_gridLayout.addWidget(self.singer_label, 1, 1, 1, 1)
        self.image_label = QtWidgets.QLabel(self.music_frame)
        self.image_label.setMinimumSize(QtCore.QSize(64, 64))
        self.image_label.setMaximumSize(QtCore.QSize(64, 64))
        self.image_label.setText("")
        self.image_label.setObjectName("image_label")
        self.music_gridLayout.addWidget(self.image_label, 0, 0, 2, 1)
        self.songname_label = QtWidgets.QLabel(self.music_frame)
        self.songname_label.setMinimumSize(QtCore.QSize(0, 32))
        self.songname_label.setMaximumSize(QtCore.QSize(16777215, 32))
        self.songname_label.setText("")
        self.songname_label.setObjectName("songname_label")
        self.music_gridLayout.addWidget(self.songname_label, 0, 1, 1, 1)
        self.lyricsdownload_gridLayout.addWidget(self.music_frame, 2, 0, 1, 2)
        self.search_tableWidget = QtWidgets.QTableWidget(LyricsDownloadDialog)
        self.search_tableWidget.setObjectName("musics_tableWidget")
        self.search_tableWidget.setColumnCount(0)
        self.search_tableWidget.setRowCount(0)
        self.lyricsdownload_gridLayout.addWidget(self.search_tableWidget, 1, 0, 1, 2)

        self.retranslateUi(LyricsDownloadDialog)
        QtCore.QMetaObject.connectSlotsByName(LyricsDownloadDialog)

    def retranslateUi(self, LyricsDownloadDialog):
        _translate = QtCore.QCoreApplication.translate
        LyricsDownloadDialog.setWindowTitle(_translate("LyricsDownloadDialog", "下载歌词"))
        self.download_button.setText(_translate("LyricsDownloadDialog", "下载"))
        self.cancel_button.setText(_translate("LyricsDownloadDialog", "取消"))
        self.search_button.setText(_translate("LyricsDownloadDialog", "搜索"))
