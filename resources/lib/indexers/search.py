# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import json

from urllib.parse import quote, quote_plus
from tulip import directory, kodi, cleantitle
from . import vod
from . import live
from ..modules.themes import iconname
from ..modules.utils import add_to_file, read_from_file
from ..modules.constants import QUERY_MAP, SEARCH_HISTORY, GM_SEARCH


class Indexer:

    def __init__(self):

        self.list = []; self.data = []

    def wrapper(self, str_input, category):

        post = 'searchcategory={0}&searchtext={1}'.format(category, quote(str_input.encode('utf-8')))

        if category == 'person':
            self.list = vod.Indexer().persons_index(GM_SEARCH, post=post)
        else:
            self.list = vod.Indexer().listing(GM_SEARCH, post=post, get_listing=True)

        return self.list

    def search_index(self):

        add_to_search_history_cm = {'title': 30486, 'query': {'action': 'add_to_search_history'}}
        refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}

        self.list = [
            {
                'title': kodi.i18n(30016),
                'action': 'search',
                'icon': iconname('search'),
                'isFolder': 'False', 'isPlayable': 'False',
                'cm': [add_to_search_history_cm, refresh_cm]
            }
        ]

        history = read_from_file(SEARCH_HISTORY)

        if history:

            search_history = [
                {
                    'title': i.split(',')[1] + ' (' + kodi.i18n(QUERY_MAP.get(i.split(',')[0])) + ')',
                    'action': 'search', 'query': i,
                    'cm': [
                        add_to_search_history_cm,
                        {'title': 30485, 'query': {'action': 'delete_from_history', 'query': i}},
                        {'title': 30494, 'query': {'action': 'change_search_term', 'query': i}},
                        refresh_cm
                    ]
                } for i in history
            ]

            for i in search_history:
                if i['query'].split(',')[0] == 'Live TV Channel':
                    i.update({'image': iconname('monitor'), 'isFolder': 'True'})
                elif i['query'].split(',')[0] == 'TV Serie':
                    i.update({'image': iconname('series'), 'isFolder': 'True'})
                elif i['query'].split(',')[0] == 'TV Show':
                    i.update({'image': iconname('shows'), 'isFolder': 'True'})
                elif i['query'].split(',')[0] == 'Movie':
                    i.update({'image': iconname('movies'), 'isFolder': 'True'})
                elif i['query'].split(',')[0] == 'Theater':
                    i.update({'image': iconname('theater'), 'isFolder': 'True'})
                elif i['query'].split(',')[0] == 'Cartoon':
                    i.update({'image': iconname('kids'), 'isFolder': 'True'})
                elif i['query'].split(',')[0] == 'Person':
                    i.update({'image': iconname('user'), 'isFolder': 'True'})

            self.list.extend(search_history)

        directory.builder(self.list)

    def search(self, action, query=None):

        if query is not None:
            choice = list(QUERY_MAP.keys()).index(query.split(',')[0])
            str_input = query.split(',')[1]
        else:
            choice = None
            str_input = None

        if choice is None:

            choices = [
                kodi.i18n(30096), kodi.i18n(30031), kodi.i18n(30030), kodi.i18n(30063), kodi.i18n(30068),
                kodi.i18n(30097), kodi.i18n(30101)
            ]

            choice = kodi.selectDialog(heading=kodi.i18n(30095), list=choices)

        if choice == 0:

            if str_input is None:

                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30096)
                )

                if not str_input:
                    return

            add_to_file(SEARCH_HISTORY, u"Live TV Channel,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = live.Indexer().live_tv(query=str_input.lower())

            if query:
                directory.builder(self.list)
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        elif choice == 1:

            if str_input is None:

                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30031)
                )

                str_input = cleantitle.strip_accents(str_input)

            if not str_input:
                return

            add_to_file(SEARCH_HISTORY, u"Movie,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = self.wrapper(str_input, 'movies')

            if query:
                directory.builder(self.list, content='movies')
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        elif choice == 2:

            if str_input is None:

                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30030)
                )

                if not str_input:

                    return

                str_input = cleantitle.strip_accents(str_input)

            add_to_file(SEARCH_HISTORY, u"TV Serie,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = self.wrapper(str_input, 'series')

            if query is not None:
                directory.builder(self.list, content='tvshows')
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        elif choice == 3:

            if not str_input:

                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30063)
                )

                if not str_input:

                    return

                str_input = cleantitle.strip_accents(str_input)

            add_to_file(SEARCH_HISTORY, u"TV Show,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = self.wrapper(str_input, 'shows')

            if query is not None:
                directory.builder(self.list, content='tvshows')
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        elif choice == 4:

            if str_input is None:

                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30068)
                )

                if not str_input:

                    return

                try:
                    str_input = cleantitle.strip_accents(str_input.decode('utf-8'))
                except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
                    str_input = cleantitle.strip_accents(str_input)

            add_to_file(SEARCH_HISTORY, u"Theater,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = self.wrapper(str_input, 'theater')

            if query is not None:
                directory.builder(self.list, content='movies')
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        elif choice == 5:

            if str_input is None:
                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30097)
                )

                if not str_input:

                    return

                str_input = cleantitle.strip_accents(str_input)

            add_to_file(SEARCH_HISTORY, u"Cartoon,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = self.wrapper(str_input, 'animation')

            if query is not None:
                directory.builder(self.list, content='tvshows')
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        elif choice == 6:

            if str_input is None:

                str_input = kodi.dialog.input(
                    heading=kodi.i18n(30095).partition(' ')[0] + kodi.i18n(30100) + kodi.i18n(30101)
                )

                if not str_input:

                    return

                str_input = cleantitle.strip_accents(str_input)

            add_to_file(SEARCH_HISTORY, u"Person,{0}".format(str_input))

            if action == 'add_to_search_history':
                kodi.refresh()
                return

            self.list = self.wrapper(str_input, 'person')

            if query is not None:
                directory.builder(self.list)
            else:
                directory.run_builtin(action='generic_index', query=quote_plus(json.dumps(self.list)))

        else:

            kodi.close_all()
