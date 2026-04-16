# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from tulip import kodi
from .constants import ART_ID


def theme():

    from xbmcaddon import Addon
    icon_theme = Addon().getSetting('theme')

    if icon_theme == '0':
        return 'alivegr', '+alivegr.png'
    elif icon_theme == '1':
        return 'twilight', '+twilight.png'
    elif icon_theme == '2':
        return 'gemini', '+gemini.png'


def iconname(name):

    base, plus = theme()

    icon = kodi.addonmedia(
        addonid=ART_ID, theme=base, path=name + plus
    )

    return icon
