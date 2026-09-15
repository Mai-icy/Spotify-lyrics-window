#!/usr/bin/python
# -*- coding:utf-8 -*-
import math
import unicodedata
from bisect import bisect_right
from functools import lru_cache

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from common.ui.vertical_orientation_data import ORIENTATION_RANGES


# Unicode 竖排规范：https://www.unicode.org/reports/tr50/
# 暂未接入字体的竖排字形替换，按规范回退：U/Tu 正立，R/Tr 顺时针旋转 90°。
_STARTS = tuple(start for start, _, _ in ORIENTATION_RANGES)


def _vertical_orientation(character):
    point = ord(character)
    index = bisect_right(_STARTS, point) - 1
    if index >= 0 and point <= ORIENTATION_RANGES[index][1]:
        return ORIENTATION_RANGES[index][2]
    return 'R'


def _graphemes(text):
    """按字素簇分组，保留重音、变体选择符和组合 Emoji。"""
    finder = QTextBoundaryFinder(QTextBoundaryFinder.BoundaryType.Grapheme, text)
    # Qt 返回 UTF-16 偏移，不能直接作为 Python 字符串下标。
    encoded = text.encode('utf-16-le', errors='surrogatepass')
    start = 0
    while (end := finder.toNextBoundary()) != -1:
        yield encoded[start * 2:end * 2].decode('utf-16-le', errors='surrogatepass')
        start = end


@lru_cache(maxsize=256)
def _vertical_runs(text):
    """返回 (文本, 是否旋转)，连续旋转文本合并，正立文本按字素簇分组。"""
    runs = []
    sideways = []
    for cluster in _graphemes(text):
        # UAX #50 §3.2.1：方向取决于字素簇首字符；包含包围组合标记
        # （Me，例如键帽 Emoji）时，整个字素簇保持正立。
        rotate = (_vertical_orientation(cluster[0]) in ('R', 'Tr')
                  and not any(unicodedata.category(ch) == 'Me' for ch in cluster))
        if rotate:
            sideways.append(cluster)
        else:
            if sideways:
                runs.append((''.join(sideways), True))
                sideways.clear()
            runs.append((cluster, False))
    if sideways:
        runs.append((''.join(sideways), True))
    return tuple(runs)


class VerticalLabel(QLabel):
    def __init__(self, parent=None):
        super(VerticalLabel, self).__init__(parent)
        self.text_height = 0
        self._layout_key = None
        self._layouts = []

    def _ensure_layout(self):
        """缓存排版结果，绘制和滚动高度使用同一组尺寸。"""
        font = self.font()
        key = (self.text(), font, self.logicalDpiX(), self.logicalDpiY())
        if key == self._layout_key:
            return
        metrics = QFontMetricsF(font, self)
        layouts = []
        text_height = 0
        # UAX #50: https://www.unicode.org/reports/tr50/
        # 按完整旋转文本或正立字素簇排版，包含回退字体的实际尺寸。
        for text, rotate in _vertical_runs(self.text()):
            layout = QTextLayout(text, font, self)
            option = QTextOption()
            option.setWrapMode(QTextOption.WrapMode.NoWrap)
            option.setFlags(QTextOption.Flag.IncludeTrailingSpaces)
            layout.setTextOption(option)
            layout.setCacheEnabled(True)
            layout.beginLayout()
            line = layout.createLine()
            line.setLineWidth(1e9)
            layout.endLayout()
            width, height = line.horizontalAdvance(), line.height()
            advance = width if rotate else max(metrics.height(), height)
            layouts.append((layout, rotate, width, height, advance))
            text_height += advance
        self._layouts = layouts
        # 保留原有的末尾一格补偿，维持滚动行为。
        self.text_height = math.ceil(text_height + metrics.height())
        self._layout_key = key

    def paintEvent(self, event: QPaintEvent) -> None:
        self._ensure_layout()
        painter = QPainter(self)
        painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))
        y = 0
        for layout, rotate, width, height, advance in self._layouts:
            painter.save()
            if rotate:
                painter.translate((self.width() + height) / 2, y)
                painter.rotate(90)
                layout.draw(painter, QPointF(0, 0))
            else:
                layout.draw(painter, QPointF((self.width() - width) / 2,
                                            y + (advance - height) / 2))
            painter.restore()
            y += advance

    def getTextSize(self):
        """获取当前歌词高度；滚动参数可能在重绘之前读取。"""
        self._ensure_layout()
        return self.text_height
