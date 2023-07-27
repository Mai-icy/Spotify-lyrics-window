#!/usr/bin/env python
# -*- coding:utf-8 -*-

from qfluentwidgets.common.icon import FluentIconBase, getIconColor
from qfluentwidgets.common.config import Theme
from enum import Enum


class ExtendFluentIcon(FluentIconBase, Enum):
    FOLDER = "Folder"
    KEYBOARD = "Keyboard"
    LIGHTBULB = "LightBulb"
    PEN = "Pen"
    PERSON = "Person"
    TRANSLATE = "Translate"
    WINDOWSAPPS = "WindowApps"

    def path(self, theme=Theme.AUTO):
        return f':/images/svg/{self.value}_{getIconColor(theme)}.svg'



