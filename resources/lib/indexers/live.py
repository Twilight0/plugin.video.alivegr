# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.
from __future__ import absolute_import, unicode_literals

import re, json, codecs
from datetime import datetime
from base64 import b64decode
from tulip import control, directory
from resolveurl.lib.net import Net as net_client
from tulip.log import log_debug
from tulip.compat import str, is_py3, py3_dec
from tulip.utils import percent
from ..modules.themes import iconname
from ..modules.utils import thgiliwt, bourtsa, pinned_from_file
from ..modules.constants import LIVE_GROUPS, LOGOS_ID, PINNED, cache_method, cache_duration
from ..modules.player import conditionals


class Indexer:

    def __init__(self):

        self.list = []
        self.data = []
        self.groups = []
        self.alivegr = 'QjNi5SZ2lGbvcXYy9Cdl5mLydWZ2lGbh9yL6MHc0RHa'

    def switcher(self):

        def seq(group):

            control.setSetting('live_group', group)
            control.idle()
            control.sleep(100)

        self.groups = list(LIVE_GROUPS.values())
        translated = [control.lang(i) for i in self.groups]
        self.data = [control.lang(30048)] + self.groups + [control.lang(30282)]
        choice = control.selectDialog(
            heading=control.lang(30049), list=[control.lang(30048)] + translated + [control.lang(30282)]
        )

        if choice != -1:
            seq(str(choice))
            control.refresh()

    @cache_method(cache_duration(480))
    def live(self):

        if control.setting('debug') == 'false':

            result = net_client().http_GET(
                thgiliwt('==' + self.alivegr), headers={'User-Agent': 'AliveGR, version: ' + control.version()}
            ).nodecode(True).content

            result = bourtsa(b64decode(result))

        else:

            if control.setting('local_remote') == '0':
                local = control.setting('live_local')
                if is_py3:
                    with open(local, encoding='utf-8') as _json:
                        result = _json.read()
                else:
                    with codecs.open(local, encoding='utf-8') as _json:
                        result = _json.read()
            elif control.setting('local_remote') == '1':
                result = net_client().http_GET(control.setting('live_remote')).content
            else:
                result = net_client().http_GET(thgiliwt('==' + self.alivegr)).nodecode(True).content
                result = bourtsa(b64decode(result))

        result = py3_dec(result)
        channel_list = json.loads(result)
        channels = [i for i in channel_list['channels'] if i['enable']]
        updated = channel_list['updated']

        for channel in channels:

            title = channel['name']
            image = channel['logo']
            if not image.startswith('http'):
                image = control.addonmedia(image, LOGOS_ID, theme='logos', media_subfolder=False)
            group = channel['group']
            group = LIVE_GROUPS[group]
            url = channel['url']

            website = channel['website']

            info = channel['info']
            if len(info) == 5 and info[:5].isdigit():
                info = control.lang(int(info))

            if ' - ' in info:
                if control.setting('lang_split') == '0':
                    if 'Greek' in control.infoLabel('System.Language'):
                        info = info.partition(' - ')[2]
                    elif 'English' in control.infoLabel('System.Language'):
                        info = info.partition(' - ')[0]
                    else:
                        info = info
                elif control.setting('lang_split') == '1':
                    info = info.partition(' - ')[0]
                elif control.setting('lang_split') == '2':
                    info = info.partition(' - ')[2]
                else:
                    info = info

            data = (
                {
                    'title': title, 'image': image, 'group': str(group), 'url': url,
                    'genre': control.lang(group), 'plot': info, 'website': website
                }
            )

            self.list.append(data)

        return self.list, updated

    def live_tv(self, zapping=False, query=None):

        if control.setting('live_tv_mode') == '1' and query is None:
            zapping = True

        live_data = self.live()

        if live_data is None:
            log_debug('Live channels list did not load successfully')
            return

        self.list = live_data[0]

        if zapping or control.setting('preresolve_streams') == 'true':

            self.list = [i for i in self.list if not i['url'].startswith(('alivegr://', 'iptv://'))]

        if zapping and control.setting('live_group') not in ['0', '14']:

            value = int(control.setting('live_group')) - 1

            group = str(list(LIVE_GROUPS.values())[value])

            self.list = [item for item in self.list if item['group'] == group]

        elif control.setting('show_live_switcher') == 'true':

            if control.setting('live_group') not in ['0', '14'] and query is None:

                value = int(control.setting('live_group')) - 1

                group = str(list(LIVE_GROUPS.values())[value])

                self.list = [item for item in self.list if item['group'] == group]

        elif not zapping:

            if control.setting('live_group') not in ['0', '14'] and query is None:

                value = int(control.setting('live_group')) - 1

                group = str(list(LIVE_GROUPS.values())[value])

                self.list = [item for item in self.list if item['group'] == group]

        if control.setting('live_group') == '14' and query is None:

            self.list = [item for item in self.list if item['title'] in pinned_from_file(PINNED)]

        if control.setting('show_alt_live') == 'false':

            self.list = [
                item for item in self.list if not any(['BUP' in item['title'], re.search(r'\(\d\)', item['title'])])
            ]

        year = datetime.now().year

        for count, item in list(enumerate(self.list, start=1)):

            item.update(
                {
                    'action': 'play_resolved' if zapping and control.setting('preresolve_streams') == 'true' else 'play',
                    'isFolder': 'False', 'year': year, 'duration': None, 'code': str(count)
                }
            )

        for item in self.list:

            if control.setting('live_group') == '14':
                pin_cm = {'title': 30337, 'query': {'action': 'unpin', 'query': item['title']}}
            else:
                pin_cm = {'title': 30336, 'query': {'action': 'pin', 'query': item['title']}}

            menu = [pin_cm]

            r_and_c_cm = {'title': 30082, 'query': {'action': 'refresh_and_clear'}}

            if not zapping:
                menu.insert(1, r_and_c_cm)

            if item['website'] != 'None':
                web_cm = {'title': 30316, 'query': {'action': 'open_link', 'url': item['website']}}
                menu.insert(2, web_cm)

            pvr_client_cm = {'title': 30084, 'query': {'action': 'pvr_client', 'query': 'true'}}

            if control.condVisibility('Pvr.HasTVChannels'):
                menu.insert(3, pvr_client_cm)

            item.update({'cm': menu})

        if control.setting('show_live_switcher') == 'true' and zapping is False:

            if control.setting('live_group') == '0':
                label = control.lang(30048)
            elif control.setting('live_group') == '14':
                label = control.lang(30282)
            else:
                value = int(control.setting('live_group')) - 1
                group = int(list(LIVE_GROUPS.values())[value])
                label = control.lang(group)

            switch = {
                'title': label,
                'image': iconname('switcher'),
                'action': 'live_switcher',
                'plot': control.lang(30034) + '[CR]' + control.lang(30035) + live_data[1],
                'isFolder': 'False', 'isPlayable': 'False'
            }

            self.list.insert(0, switch)

        if control.setting('preresolve_streams') == 'true':

            pd = control.progressDialogGB
            pd.create(control.name())

            for item in self.list:

                try:
                    _percent = percent(int(item['code']), len(self.list))
                    pd.update(_percent)
                    new_stream = conditionals(item['url'])
                    if not new_stream:
                        raise Exception('Stream was not resolved, skipped')
                    item.update({'url': new_stream})
                except Exception as e:
                    log_debug('Failed to resolve ' + item['title'] + ' , reason: ' + repr(e))
                    continue

            pd.update(100)
            pd.close()

        if query:

            self.list = [i for i in self.list if query in i['title'].lower()]

            return self.list

        if not zapping:

            control.sortmethods('production_code')
            control.sortmethods('title')
            control.sortmethods('genre')

        directory.add(self.list, content='videos', as_playlist=zapping)


    @cache_method(cache_duration(480))
    def cached_live_m3u(self):

        result = net_client().http_GET(
            'https://raw.githubusercontent.com/komhsgr/m3u/refs/heads/main/Greekstreamtv.m3u', headers={'User-Agent': 'AliveGR, version: ' + control.version()}
            ).content

        items = re.findall(r'#EXTINF:.+?\n.+?$', result, re.M)

        for item in items:

            title = re.search(r',(.+)', item).group(1)
            try:
                image = re.search(r'tvg-logo="(.+)"', item).group(1)
            except AttributeError:
                image = control.addonInfo('icon')
            url = re.search(r'\n(.+)', item).group(1)

            data = {'title': title, 'image': image, 'url': url}

            self.list.append(data)

        return self.list

    def live_m3u(self):

        self.list = self.cached_live_m3u()

        for i in self.list:

            i.update({'action': 'play', 'isFolder': 'False'})

        directory.add(self.list)

    def modular(self, group):

        if group == '30125':
            fanart = 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
        elif group == '30032':
            fanart = 'http://cdn.iview.abc.net.au/thumbs/i/ls/LS1604H001S005786f5937ded19.22034349_1280.jpg'
        else:
            fanart = control.addonInfo('fanart')

        self.data = self.live()[0]
        self.list = [item for item in self.data if item['group'] == group]

        year = datetime.now().year

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:

            r_and_c_cm = {'title': 30082, 'query': {'action': 'refresh_and_clear'}}
            pin_cm = {'title': 30336, 'query': {'action': 'pin'}}
            item.update(
                {
                    'cm': [pin_cm, r_and_c_cm], 'year': year, 'duration': None, 'fanart': fanart
                }
            )

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)
