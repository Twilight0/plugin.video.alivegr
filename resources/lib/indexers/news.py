# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from urllib.parse import urljoin

from tulip import kodi
from tulip.cleantitle import replaceHTMLCodes
from tulip.init import syshandle, sysaddon
from netclient import Net
from useragents import FALLBACK_USER_AGENTS
from domparsers import parseDOM

from ..modules.themes import iconname
from ..modules.constants import cache_method, cache_duration, FRONTPAGES_BASE


class Indexer:

    GROUPS = {
        0: 30231,  # Politics
        1: 30232,  # Sports
        2: 30233,  # Economic
        3: 30234,  # Local
        4: 30515,  # Magazines
    }

    def __init__(self):

        self.list = []
        self.data = []
        self.directory = []
        self.fp_link = FRONTPAGES_BASE

    @staticmethod
    def switcher():

        def seq(choose):

            kodi.setSetting('papers_group', choose)
            kodi.idle()
            kodi.sleep(100)
            kodi.refresh()

        group_keys = list(Indexer.GROUPS.keys())
        group_labels = [kodi.i18n(Indexer.GROUPS[k]) for k in group_keys]

        choice = kodi.selectDialog(heading=kodi.i18n(30049), list=group_labels)

        if choice != -1 and choice < len(group_keys):
            seq(str(group_keys[choice]))
        else:
            kodi.execute('Dialog.Close(all)')

    @cache_method(cache_duration(720))
    def front_pages(self):

        try:
            headers = {'User-Agent': FALLBACK_USER_AGENTS[0]}
            response = Net().http_GET(self.fp_link, headers=headers)
            html = response.content
        except Exception:
            return []

        if isinstance(html, bytes):
            try:
                html = html.decode('utf-8')
            except UnicodeDecodeError:
                html = html.decode('latin-1', errors='replace')

        groups = parseDOM(html, 'div', attrs={'class': 'tabbertab'})

        for group, papers in enumerate(groups):

            items = parseDOM(papers, 'div', attrs={'class': 'thumber'})

            for i in items:

                btn = parseDOM(i, 'button', attrs={'class': 'coverZoomButton'}, ret='data-full-src')
                imgs = parseDOM(i, 'img', ret='src')
                if not imgs:
                    continue

                image = urljoin(self.fp_link, imgs[0])
                if btn and btn[0]:
                    link = urljoin(self.fp_link, btn[0])
                else:
                    link = image.replace('300.jpg', 'I.jpg')

                paper_names = parseDOM(i, 'div', attrs={'class': 'paperName'})
                if paper_names:
                    links = parseDOM(paper_names[0], 'a')
                    title = links[0] if links else paper_names[0]
                else:
                    alts = parseDOM(i, 'img', ret='alt')
                    title = alts[0] if alts else kodi.i18n(30236)

                title = replaceHTMLCodes(title)
                data = {'title': title, 'image': image, 'url': link, 'group': group}

                self.list.append(data)

        return self.list

    def papers_index(self):

        self.data = self.front_pages()

        for i in self.data:
            i.update({'action': None, 'isFolder': 'False'})

        try:
            active_group = int(kodi.setting('papers_group'))
        except (ValueError, TypeError):
            active_group = 0
            kodi.setSetting('papers_group', '0')

        self.list = [item for item in self.data if item['group'] == active_group]
        if not self.list and self.data:
            self.list = [item for item in self.data if item['group'] == 0]
            kodi.setSetting('papers_group', '0')
            active_group = 0

        group_label_id = self.GROUPS.get(active_group, 30231)

        switch = {
            'title': kodi.i18n(30047).format(kodi.i18n(group_label_id)),
            'icon': iconname('switcher'),
            'action': 'papers_switcher'
        }

        if kodi.setting('show_pic_switcher') == 'true':

            li = kodi.item(label=switch['title'])
            li.setArt({'icon': switch['icon'], 'fanart': kodi.addonInfo('fanart')})
            url = '{0}?action={1}'.format(sysaddon, switch['action'])
            kodi.addItem(syshandle, url, li)

        for i in self.list:

            li = kodi.item(label=i['title'])
            li.setArt({'icon': i['image'], 'poster': i['image'], 'thumb': i['image'], 'fanart': kodi.addonInfo('fanart')})
            li.setInfo('image', {'title': i['title'], 'picturepath': i['url']})
            url = i['url']
            self.directory.append((url, li, False))

        kodi.content(syshandle, 'images')
        kodi.addItems(syshandle, self.directory)
        kodi.directory(syshandle)

