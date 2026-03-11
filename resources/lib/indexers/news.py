# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.
from __future__ import absolute_import, unicode_literals

from tulip import control
from resolveurl.lib.net import Net as net_client
from tulip.init import syshandle, sysaddon
from tulip.cleantitle import replaceHTMLCodes
from tulip.parsers import parseDOM
from ..modules.themes import iconname
from ..modules.constants import ART_ID, cache_method, cache_duration


class Indexer:

    def __init__(self):

        self.list = []; self.data = []; self.directory = []
        self.fp_link = 'http://www.frontpages.gr'

    def news(self):

        items = [
            {
                'title': control.lang(30230),
                'icon': 'https://www.iconexperience.com/_img/v_collection_png/256x256/shadow/newspaper.png',
                'url': '{0}?action=papers'.format(sysaddon),
                'fanart': control.addonInfo('fanart')
            }
            ,
            {
                'title': control.lang(30118),
                'icon': control.addonmedia(addonid=ART_ID, theme='networks', icon='ert_icon.png', media_subfolder=False),
                'url': 'plugin://plugin.video.ert.gr/?action=categories&url=https%3A%2F%2Fwww.ertflix.gr%2Fshow%2Fnews',
                'fanart': control.addonmedia(addonid=ART_ID, theme='networks', icon='ert_fanart.jpg', media_subfolder=False)
            }
            ,
            {
                'title': control.lang(30119),
                'icon': control.addonmedia(addonid=ART_ID, theme='networks', icon='ant1_icon.png', media_subfolder=False),
                'url': 'plugin://plugin.video.antenna.gr/?action=videos&url=https%3a%2f%2fwww.ant1news.gr%2fvideos',
                'fanart': control.addonmedia(addonid=ART_ID, theme='networks', icon='ant1_fanart.jpg', media_subfolder=False)
            }
            ,
            {
                'title': control.lang(30120),
                'icon': control.addonmedia(addonid=ART_ID, theme='networks', icon='star_icon.png', media_subfolder=False),
                'url': 'plugin://plugin.video.star.gr/?action=news',
                'fanart': control.addonmedia(addonid=ART_ID, theme='networks', icon='star_fanart.jpg', media_subfolder=False)
            }
            ,
            {
                'title': control.lang(30122),
                'icon': control.addonmedia(addonid=ART_ID, theme='networks', icon='alpha_icon.png', media_subfolder=False),
                'url': 'plugin://plugin.video.alphatv.gr/?action=news&url=https%3a%2f%2fwww.alphatv.gr%2fnews',
                'fanart': control.addonmedia(addonid=ART_ID, theme='networks', icon='alpha_fanart.jpg', media_subfolder=False)
            }
            ,
            {
                'title': control.lang(30121),
                'icon': control.addonmedia(addonid=ART_ID, theme='networks', icon='skai_icon.png', media_subfolder=False),
                'url': 'plugin://plugin.video.skai.gr/?action=news',
                'fanart': control.addonmedia(addonid=ART_ID, theme='networks', icon='skai_fanart.jpg', media_subfolder=False)
            }
        ]

        for item in items:

            list_item = control.item(label=item['title'])
            list_item.setArt({'icon': item['icon'], 'fanart': item['fanart']})
            url = item['url']
            isFolder = True if 'papers' not in item['url'] else False
            self.list.append((url, list_item, isFolder))

        control.addItems(syshandle, self.list)
        control.directory(syshandle)

    @staticmethod
    def switcher():

        def seq(choose):

            control.setSetting('papers_group', choose)
            control.idle()
            control.sleep(100)
            control.refresh()

        groups = (
            [control.lang(30231), control.lang(30232), control.lang(30233), control.lang(30234)],
            ['0', '1', '2', '3']
        )

        choice = control.selectDialog(heading=control.lang(30049), list=groups[0])

        if choice <= len(groups[0]) and not choice == -1:
            seq(groups[1][choice])
        else:
            control.execute('Dialog.Close(all)')

    @cache_method(cache_duration(720))
    def front_pages(self):

        html = net_client().http_GET(self.fp_link).content

        try:
            groups = parseDOM(html.decode('utf-8'), 'div', attrs={'class': 'tabbertab.+?'})
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
            groups = parseDOM(html, 'div', attrs={'class': 'tabbertab.+?'})

        for group, papers in list(enumerate(groups)):

            items = parseDOM(papers, 'div', attrs={'class': 'thumber'})

            for i in items:

                title = parseDOM(i, 'img', attrs={'style': 'padding:5px.+?'}, ret='alt')[0]
                title = replaceHTMLCodes(title)
                image = parseDOM(i, 'img', attrs={'style': 'padding:5px.+?'}, ret='src')[0]
                image = ''.join([self.fp_link, image])
                link = image.replace('300.jpg', 'I.jpg')

                data = {'title': title, 'image': image, 'url': link, 'group': group}

                self.list.append(data)

        return self.list

    def papers_index(self):

        self.data = self.front_pages()

        for i in self.data:
            i.update({'action': None, 'isFolder': 'False'})

        try:
            self.list = [item for item in self.data if item['group'] == int(control.setting('papers_group'))]
        except Exception:
            self.list = [item for item in self.data if item['group'] == 0]
            control.setSetting('papers_group', '0')

        if control.setting('papers_group') == '1':
            integer = 30232
        elif control.setting('papers_group') == '2':
            integer = 30233
        elif control.setting('papers_group') == '3':
            integer = 30234
        else:
            integer = 30231

        switch = {
            'title': control.lang(30047).format(control.lang(integer)),
            'icon': iconname('switcher'),
            'action': 'papers_switcher'
        }

        if control.setting('show_pic_switcher') == 'true':

            li = control.item(label=switch['title'])
            li.setArt({'icon': switch['icon'],'fanart': control.addonInfo('fanart')})
            url = '{0}?action={1}'.format(sysaddon, switch['action'])
            control.addItem(syshandle, url, li)

        for i in self.list:

            li = control.item(label=i['title'])
            li.setArt({'icon': i['image'], 'poster': i['image'], 'thumb': i['image'], 'fanart': control.addonInfo('fanart')})
            li.setInfo('image', {'title': i['title'], 'picturepath': i['url']})
            url = i['url']
            self.directory.append((url, li, False))

        control.addItems(syshandle, self.directory)
        control.directory(syshandle)
