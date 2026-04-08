# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from tulip import kodi, directory
from ..modules.themes import iconname
from .vod import GM_BASE

class Indexer:

    def __init__(self):

        self.list = []
        self.data = []

    def kids(self):

        self.list = [
            {
                'title': kodi.i18n(30078),
                'action': 'kids_live',
                'icon': iconname('kids_live'),
                'isFolder': 'True'
            }
            ,
            {
                'title': kodi.i18n(30073),
                'action': 'listing',
                'url': ''.join([GM_BASE, 'movies.php?g=8&y=&l=&p=']),
                'icon': iconname('cartoon_movies'),
                'isFolder': 'True'
            }
            ,
            {
                'title': kodi.i18n(30092),
                'action': 'listing',
                'url': ''.join([GM_BASE, 'shortfilm.php?g=8&y=&l=&p=']),
                'icon': iconname('cartoon_short'),
                'isFolder': 'True'
            }
            ,
            {
                'title': kodi.i18n(30072),
                'action': 'cartoon_series',
                'icon': iconname('cartoon_series'),
                'isFolder': 'True'
            }
        ]

        directory.builder(self.list)
