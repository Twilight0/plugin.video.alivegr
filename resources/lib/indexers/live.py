# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import re
import json
from urllib.parse import urlencode
from datetime import datetime
from tulip import kodi, directory
from netclient import Net
from useragents import get_ua
from tulip.utils import py3_dec
from ..modules.utils import thgiliwt, pinned_from_file
from ..modules.themes import iconname
from ..modules.constants import LIVE_GROUPS, cache_method, cache_duration, M3U_LINK, PINNED


class Indexer:

    def __init__(self):

        # self.alivegr = 'QjNi5SZ2lGbvcXYy9Cdl5mLydWZ2lGbh9yL6MHc0RHa'
        self.alivegr = (
            'gbvNnaug2YfJ3ZvY2M0YWY5gzY3YTO3UGM5EzYiJjMmNzY4EDZ0YzNjFjZ3ITZhFzM2Q2L3FmcvYmY0IGN3YmZ2QDZ0EGN4EWMwQGOzcD'
            'ZxYGZ1EjYyUzYvADdodWasl2dU9SbvNmL05WZ052bjJXZzVnY1hGdpdmL0NXan9yL6MHc0RHa'
        )

    @staticmethod
    def switcher():

        def seq(group):
            kodi.setSetting('live_group', group)
            kodi.idle()
            kodi.sleep(100)

        groups = list(LIVE_GROUPS.values())
        translated = [kodi.i18n(i) for i in groups]
        choice = kodi.selectDialog(heading=kodi.i18n(30049), list=[kodi.i18n(30048)] + translated + [kodi.i18n(30282)])

        if choice != -1:
            seq(str(choice))
            kodi.refresh()

    @cache_method(cache_duration(480))
    def live(self):

        if kodi.setting('debug') == 'false':

            result = Net().http_GET(
                py3_dec(thgiliwt('==' + self.alivegr))
            ).content

            # result = Net().http_GET('https://pastebin.com/raw/YxxuQEtP').content

            # result = bourtsa(b64decode(result))

        else:

            if kodi.setting('local_remote') == '0':
                local = kodi.setting('live_local')
                with open(local, encoding='utf-8') as _json:
                    result = _json.read()
            elif kodi.setting('local_remote') == '1':
                result = Net().http_GET(kodi.setting('live_remote')).content
            else:
                result = Net().http_GET(thgiliwt('==' + self.alivegr)).content
                # result = bourtsa(b64decode(result))

        try:
            channels = json.loads(result)
        except json.decoder.JSONDecodeError:
            channels = json.loads(result.replace('\'', '"'))
        # channels = [i for i in channel_list['channels'] if i['enable']]
        updated = channels['updated']
        live_list = []

        for channel in channels['channels']:

            title = channel['name']
            image = channel['logo']
            group = channel['group']
            group = LIVE_GROUPS[group]
            url = channel['url']
            website = channel['website']
            info = channel['info']
            headers = channel.get('headers')
            if headers == 'random':
                headers = {'User-Agent': get_ua(), 'Referer': 'https://www.greektv.live/'}
            drm = channel.get('drm')
            if drm:
                if not isinstance(headers, dict):
                    headers = {}
                headers.update({'DRM': json.dumps(drm)})

            if len(info) == 5 and info[:5].isdigit():
                info = kodi.i18n(int(info))

            if ' - ' in info:
                if kodi.setting('lang_split') == '0':
                    if 'Greek' in kodi.infoLabel('System.Language'):
                        info = info.partition(' - ')[2]
                    elif 'English' in kodi.infoLabel('System.Language'):
                        info = info.partition(' - ')[0]
                    else:
                        info = info
                elif kodi.setting('lang_split') == '1':
                    info = info.partition(' - ')[0]
                elif kodi.setting('lang_split') == '2':
                    info = info.partition(' - ')[2]
                else:
                    info = info

            data = (
                {
                    'title': title, 'image': image, 'group': str(group),
                    'genre': kodi.i18n(group), 'plot': info, 'website': website
                }
            )

            if headers:
                data.update({'url': '|'.join([url[0], urlencode(headers)])})
            else:
                data.update({'url': url[0]})

            live_list.append(data)

        return live_list, updated

    def live_tv(self, query=None):

        live_data, updated = self.live()

        if kodi.setting('live_tv_mode') == '1' and kodi.setting('live_group') not in ['0', '0']:

            value = int(kodi.setting('live_group')) - 1

            group = str(list(LIVE_GROUPS.values())[value])

            live_data = [item for item in live_data if item['group'] == group]

        elif kodi.setting('show_live_switcher') == 'true':

            if kodi.setting('live_group') not in ['0', '10'] and query is None:

                value = int(kodi.setting('live_group')) - 1

                group = str(list(LIVE_GROUPS.values())[value])

                live_data = [item for item in live_data if item['group'] == group]

        elif not kodi.setting('live_tv_mode') == '1':

            if kodi.setting('live_group') not in ['0', '10'] and query is None:

                value = int(kodi.setting('live_group')) - 1

                group = str(list(LIVE_GROUPS.values())[value])

                live_data = [item for item in live_data if item['group'] == group]

        if kodi.setting('live_group') == '10' and query is None:

            live_data = [item for item in live_data if item['title'] in pinned_from_file(PINNED)]

        year = datetime.now().year

        for item in live_data:

            item.update(
                {
                    'action': 'play', 'isPlayable': 'True', 'year': year,
                    'duration': None
                }
            )

        for item in live_data:

            if kodi.setting('live_group') == '10':
                pin_cm = {'title': 30337, 'query': {'action': 'unpin', 'query': item['title']}}
            else:
                pin_cm = {'title': 30336, 'query': {'action': 'pin', 'query': item['title']}}

            menu = [pin_cm]

            group_changer = {'title': 30034, 'query': {'action': 'live_switcher'}}
            r_and_c_cm = {'title': 30082, 'query': {'action': 'refresh_and_clear'}}

            if kodi.setting('live_tv_mode') == '0':
                menu.insert(1, r_and_c_cm)

            if kodi.setting('show_live_switcher') == 'false':
                menu.insert(1, group_changer)

            if item['website'] != 'None':
                web_cm = {'title': 30316, 'query': {'action': 'open_link', 'url': item['website']}}
                menu.insert(2, web_cm)

            item.update({'cm': menu})

        if kodi.setting('show_live_switcher') == 'true' and kodi.setting('live_tv_mode') == '0':

            if kodi.setting('live_group') == '0':
                label = kodi.i18n(30048)
            elif kodi.setting('live_group') == '10':
                label = kodi.i18n(30282)
            else:
                value = int(kodi.setting('live_group')) - 1
                group = int(list(LIVE_GROUPS.values())[value])
                label = kodi.i18n(group)

            switch = {
                'title': label,
                'image': iconname('switcher'),
                'action': 'live_switcher',
                'plot': kodi.i18n(30034) + '[CR]' + kodi.i18n(30035) + updated,
                'isFolder': 'False', 'isPlayable': 'False'
            }

            live_data.insert(0, switch)

        if query:

            queried_list = [i for i in live_data if query in i['title'].lower()]

            return queried_list

        if kodi.setting('live_tv_mode') == '0':

            kodi.setsortmethod()
            kodi.setsortmethod('production_code')
            kodi.setsortmethod('title')
            kodi.setsortmethod('genre', mask='%C')

        directory.builder(live_data, content='videos', as_playlist=kodi.setting('live_tv_mode') == '1')

    @cache_method(cache_duration(480))
    def cached_live_m3u(self):

        result = Net().http_GET(
            M3U_LINK, headers={'User-Agent': 'AliveGR, version: ' + kodi.version()}
        ).content

        items = re.findall(r'#EXTINF:.+?\n.+?$', result, re.M)

        m3u_list = []

        for item in items:

            title = re.search(r',(.+)', item).group(1)
            try:
                image = re.search(r'tvg-logo="(.+)"', item).group(1)
            except AttributeError:
                image = kodi.addonInfo('icon')
            url = re.search(r'\n(.+)', item).group(1)

            data = {'title': title, 'image': image, 'url': url}

            m3u_list.append(data)

        return m3u_list

    def live_m3u(self):

        m3u_list = self.cached_live_m3u()

        for i in m3u_list:
            i.update({'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})

        directory.builder(m3u_list, content='videos', as_playlist=kodi.setting('live_tv_mode') == '1')

    def modular(self, group):

        if group == '30125':
            fanart = 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
        elif group == '30032':
            fanart = 'https://cdn.iview.abc.net.au/thumbs/i/ls/LS1604H001S005786f5937ded19.22034349_1280.jpg'
        else:
            fanart = kodi.addonInfo('fanart')

        channel_list, _ = self.live()
        modular_list = [item for item in channel_list if item['group'] == group]

        year = datetime.now().year

        for item in modular_list:
            pin_cm = {'title': 30336, 'query': {'action': 'pin'}}
            item.update(
                {'action': 'play', 'isFolder': 'False', 'isPlayable': 'True',
                 'cm': [pin_cm], 'year': year, 'duration': None, 'fanart': fanart
                 }
            )

        modular_list.sort(key=lambda k: k['title'].lower())

        directory.builder(modular_list, content='videos', as_playlist=kodi.setting('live_tv_mode') == '1')
