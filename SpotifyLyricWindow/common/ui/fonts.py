"""Resolve unavailable Windows font preferences when running on macOS."""
import sys

from PyQt6.QtGui import QFontDatabase


def resolve_font_family(family: str) -> str:
    if sys.platform != "darwin":
        return family
    available = QFontDatabase.families()
    if family in available:
        return family
    if "PingFang SC" in available:
        return "PingFang SC"
    return QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
