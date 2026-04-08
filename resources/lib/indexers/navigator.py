# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import json

from tulip import kodi, directory
from tulip.utils import convert_to_bool
from tulip.utils import iteritems
from tulip.log import log
from ..modules.themes import iconname
from ..modules.utils import read_from_file, reset_idx as reset
from ..modules.constants import PLAYBACK_HISTORY


class Indexer:

    def __init__(self):

        self.list = []
        self.menu = []

    def root(self):

        log("Opening up")

        self.list = [
            {
                'title': kodi.i18n(30001),
                'action': 'live_tv',
                'icon': iconname('monitor'),
                'show_item': kodi.setting('show_live') == 'true',
                'isFolder': 'False' if kodi.setting('live_tv_mode') == '1' else 'True', 'isPlayable': 'False'
            }
            # ,
            # {
            #     'title': kodi.i18n(30001),
            #     'action': 'live_m3u',
            #     'icon': iconname('monitor'),
            #     'show_item': kodi.setting('show_live') == 'false' and kodi.setting('show_m3u') == 'true',
            #     'isFolder': 'False' if kodi.setting('live_tv_mode') == '1' else 'True', 'isPlayable': 'False'
            # }
            # ,
            # {
            #     'title': kodi.i18n(30036),
            #     'action': 'pvr_client',
            #     'icon': iconname('guide'),
            #     'show_item': kodi.setting('show_pvr') == 'true'
            # }
            # ,
            # {
            #     'title': kodi.i18n(30008),
            #     'action': 'networks',
            #     'icon': iconname('networks'),
            #     'show_item': kodi.setting('show_networks') == 'true'
            # }
            # ,
            # {
            #     'title': kodi.i18n(30123),
            #     'action': 'news',
            #     'icon': iconname('news'),
            #     'show_item': kodi.setting('show_news') == 'true'
            # }
            ,
            {
                'title': kodi.i18n(30031),
                'action': 'movies',
                'icon': iconname('movies'),
                'show_item': kodi.setting('show_movies') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30083),
                'action': 'short_films',
                'icon': iconname('short'),
                'show_item': kodi.setting('show_short_films') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30030),
                'action': 'series',
                'icon': iconname('series'),
                'show_item': kodi.setting('show_series') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30063),
                'action': 'shows',
                'icon': iconname('shows'),
                'show_item': kodi.setting('show_shows') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30068),
                'action': 'theater',
                'icon': iconname('theater'),
                'show_item': kodi.setting('show_theater') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30079),
                'action': 'listing',
                'url': 'https://greek-movies.com/movies.php?g=6&y=&l=&p=',
                'icon': iconname('documentaries'),
                'show_item': kodi.setting('show_docs') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            # {
            #     'title': kodi.i18n(30094),
            #     'action': 'gm_sports',
            #     'icon': iconname('sports'),
            #     'show_item': kodi.setting('show_sports') == 'true',
            #     'isFolder': 'True', 'isPlayable': 'False'
            # }
            # ,
            {
                'title': kodi.i18n(30032),
                'action': 'kids',
                'icon': iconname('kids'),
                'show_item': kodi.setting('show_kids') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            # ,
            # {
            #     'title': kodi.i18n(30002),
            #     'action': 'radio',
            #     'icon': iconname('radios'),
            #     'show_item': kodi.setting('show_radio') == 'true'
            # }
            ,
            {
                'title': kodi.i18n(30125),
                'action': 'music',
                'icon': iconname('music'),
                'show_item': kodi.setting('show_music') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30095).partition(' ')[0],
                'action': 'search_index',
                'icon': iconname('search'),
                'show_item': kodi.setting('show_search') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30012),
                'action': 'playback_history',
                'icon': iconname('history'),
                'show_item': kodi.setting('show_history') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30055),
                'action': 'bookmarks',
                'icon': iconname('bookmarks'),
                'show_item': kodi.setting('show_bookmarks') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30137),
                'action': 'settings',
                'icon': iconname('settings'),
                'show_item': kodi.setting('show_settings') == 'true',
                'isFolder': 'True', 'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30288),
                'action': 'quit',
                'icon': iconname('quit'),
                'show_item': kodi.setting('show_quit') == 'true',
                'isFolder': 'False', 'isPlayable': 'False'
            }
        ]

        self.list = [item for item in self.list if convert_to_bool(item['show_item'])]

        refresh = {'title': 30054, 'query': {'action': 'refresh'}}
        cache_clear = {'title': 30056, 'query': {'action': 'cache_clear'}}
        reset_idx = {'title': 30134, 'query': {'action': 'reset_idx', 'query': 'force'}}
        settings = {'title': 30011, 'query': {'action': 'openSettings'}}
        go_to_audio = {'title': 30321, 'query': {'action': 'activate_other_addon', 'url': 'plugin.video.alivegr', 'query': 'audio'}}
        tools = {'title': 30137, 'query': {'action': 'tools_menu'}}
        ii_cm = {'title': 30255, 'query': {'action': 'call_info'}}

        for item in self.list:

            item.update({'cm': [ii_cm, refresh, cache_clear, reset_idx, settings, go_to_audio, tools]})

        directory.builder(self.list)

    def playback_history(self):

        lines = read_from_file(PLAYBACK_HISTORY)

        if not lines:

            self.list = [{'title': 30110, 'action':  None, 'icon': iconname('empty')}]
            directory.builder(self.list)

        else:

            self.list = [json.loads(line) for line in lines]

            for i in self.list:
                bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
                bookmark['bookmark'] = i['url']
                bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
                remove_from_history_cm = {'title': 30485, 'query': {'action': 'delete_from_history', 'query': json.dumps(i)}}
                clear_history_cm = {'title': 30471, 'query': {'action': 'clear_playback_history'}}
                i.update({'cm': [bookmark_cm, remove_from_history_cm, clear_history_cm]})

            directory.builder(self.list)

    def generic(self, query, content='videos'):

        self.list = json.loads(query)

        directory.builder(self.list, content=content)
