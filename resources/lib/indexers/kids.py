# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.
from __future__ import absolute_import, unicode_literals

import re
from tulip import control, directory
from resolveurl.lib.net import Net as net_client
from tulip.cleantitle import replaceHTMLCodes
from tulip.parsers import parseDOM
from tulip.init import syshandle, sysaddon
from tulip.compat import urlsplit
from ..modules.themes import iconname
from ..modules.constants import YT_ADDON, cache_method, cache_duration, cache_function
from .gm import GM_BASE

GK_BASE = 'https://gamatomovies.tv'


class Indexer:

    def __init__(self):

        self.list = []
        self.data = []

    def kids(self):

        self.list = [
            # {
            #     'title': control.lang(30078),
            #     'action': 'kids_live',
            #     'icon': iconname('kids_live')
            # }
            # ,
            {
                'title': control.lang(30073),
                'action': 'listing',
                'url': ''.join([GM_BASE, 'movies.php?g=8&y=&l=&p=']),
                'icon': iconname('cartoon_movies')
            }
            ,
            {
                'title': control.lang(30092),
                'action': 'listing',
                'url': ''.join([GM_BASE, 'shortfilm.php?g=8&y=&l=&p=']),
                'icon': iconname('cartoon_short')
            }
            ,
            {
                'title': control.lang(30072),
                'action': 'cartoon_series',
                'icon': iconname('cartoon_series')
            }
            ,
            # {
            #     'title': control.lang(30074),
            #     'action': 'cartoon_collection',
            #     'icon': iconname('cartoon_collection')
            # }
            # ,
            # {
            #     'title': control.lang(30075),
            #     'action': 'educational',
            #     'icon': iconname('educational')
            # }
            # ,
            # {
            #     'title': control.lang(30262),
            #     'action': 'activate_other_addon',
            #     'url': 'plugin://plugin.video.ert.gr/?action=categories&url=https%3A%2F%2Fwww.ertflix.gr%2Fshow%2Fchildren',
            #     'icon': iconname('cartoon_collection'),
            #     'isFolder': 'False', 'isPlayable': 'False'
            # }
            # ,
            # {
            #     'title': control.lang(30076),
            #     'action': 'kids_songs',
            #     'icon': iconname('kids_songs')
            # }
        ]

        directory.add(self.list)

    def cartoon_collection(self):

        self.data = [
            {
                'title': u'Classical Films - Κλασσικά Κινηματογραφημένα',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PLF0A5359586D57FE8/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/X9RxumkELfE/mqdefault.jpg'
            }
            ,
            {
                'title': u'Mythology - Μυθολογία',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PL3E1C926284F12F32/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/kpd-Z_VK6Jc/mqdefault.jpg'
            }
            ,
            {
                'title': u'Aesop\'s Fables - Αισώπου Μύθοι',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PL4FF9F773D3596E60/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/Gkr-pV_gY48/mqdefault.jpg'
            }
            ,
            {
                'title': u'Greek Fairy Tales - Ελληνικά Παραμύθια',
                'url': '{0}/channel/UC9VmWb5Wd5sc4E4k1CevEug/'.format(YT_ADDON),
                'icon': 'https://yt3.ggpht.com/-n8KoGQ6U_zc/AAAAAAAAAAI/AAAAAAAAAAA/SoUWvy5-Tb8/s256-c-k-no-mo-rj-c0xffffff/photo.jpg'
            }
            ,
            {
                'title': u'Fairy Tales & Songs - Παραμύθια και Τραγούδια',
                'url': '{0}/channel/UCClAFTnbGditvz9_7_7eumw/playlists/'.format(YT_ADDON),
                'icon': 'https://yt3.ggpht.com/-mBPhzUcDIHM/AAAAAAAAAAI/AAAAAAAAAAA/pNQi44zsLq8/s256-c-k-no-mo-rj-c0xffffff/photo.jpg'
            }
            ,
            {
                'title': u'Collection Miscellaneous - Συλλογή Διάφορα',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PL4075DA390F6E82B1/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/MPtZ_VHNg34/mqdefault.jpg'
            }
        ]

        additional = {
                'title': u'Various full length movies - Διάφορες ταινίες πλήρους μήκους',
                'url': '{0}?action={1}'.format(sysaddon, 'cartoon_various'),
                'icon': iconname('kids')
            }

        if control.setting('show_alt_vod') == 'true':
            self.data.insert(0, additional)

        for item in self.data:
            if control.setting('lang_split') == '0':
                if 'Greek' in control.infoLabel('System.Language'):
                    li = control.item(label=item['title'].partition(' - ')[2])
                elif 'English' in control.infoLabel('System.Language'):
                    li = control.item(label=item['title'].partition(' - ')[0])
                else:
                    li = control.item(label=item['title'])
            elif control.setting('lang_split') == '1':
                li = control.item(label=item['title'].partition(' - ')[0])
            elif control.setting('lang_split') == '2':
                li = control.item(label=item['title'].partition(' - ')[2])
            else:
                li = control.item(label=item['title'])
            li.setArt({'icon': item['icon'], 'fanart': control.addonInfo('fanart')})
            self.list.append((item['url'], li, True))

        control.addItems(syshandle, self.list)
        control.directory(syshandle)

    def educational(self):

        self.data = [
            {
                'title': u'Learn about animals - Μάθε για τα ζώα',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PL7Adbo89X3LRboPyGr30sIRMnc20C77ui/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/_fDdVYJA9Vk/mqdefault.jpg'
            }
            ,
            {
                'title': u'Secondary school education - Εκπαίδευση Δημοτικού Σχολείου',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PL7Adbo89X3LQvxn7RyUySvQy6C6hTUTXf/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/isxjo7M2h74/mqdefault.jpg'
            }
            ,
            {
                'title': u'Sexual Education for children - Σεξουαλική Αγωγή για παιδιά',
                'url': '{0}/channel/UCsKQX1G7XQO2a5nD9nrse-Q/playlist/PL7Adbo89X3LRy-LRQEeRdT_kf5iFdofsu/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/l9gN1F6S3bc/mqdefault.jpg'
            }
            ,
            {
                'title': u'World\'s Seven Ancient Miracles - Τα Επτά Θαύματα του Αρχαίου Κόσμου',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeThKG7GK1k2DRgB5im-vPHc/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/5nEDQ_jYJIo/mqdefault.jpg'
            }
            ,
            {
                'title': u'The land of Knowledge - Η Χώρα των Γνώσεων',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeS-ZVlk0vgNdx5igsFvYN8s/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/K-Ba9l2uDDk/mqdefault.jpg'
            }
            ,
            {
                'title': u'Ancient Egypt - Αρχαία Αίγυπτος',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeTrRcdIHjtziNEkqPqalUOa/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/pV8EMy8gaXI/mqdefault.jpg'
            }
            ,
            {
                'title': u'Explorers & Seafarers - Εξερευνητές και Θαλασσοπόροι',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeQRBb7ayyynWgYEUbkQKPpJ/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/SPdnnVNZgwc/mqdefault.jpg'
            }
            ,
            {
                'title': u'Mini Encyclopaedia - Μικρή Εγκυκλοπαίδεια',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeTLMi1bFqLC_cn5ZAtqSvlV/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/o31_SNQFYhc/mqdefault.jpg'
            }
            ,
            {
                'title': u'Miscellaneous Documentaties - Διάφορα Ντοκυμαντέρ',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeRY94Yga82ZYsPJ9Xbe3OiZ/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/Vf_o_Q5ZQRg/mqdefault.jpg'
            }
            ,
            {
                'title': u'Learn Ancient Greek - Μάθετε Αρχαία Ελληνικά',
                'url': '{0}/channel/UC5quWsvOBNUaR-Duv3K-JFA/playlist/PLxqCshQO3A1HnlHwxda3wX_kzY-C0gpZq/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/st01jb_Xb7g/mqdefault.jpg'
            }
            ,
            {
                'title': u'Drawings - Ζωγραφιές',
                'url': '{0}/channel/UC5quWsvOBNUaR-Duv3K-JFA/playlist/PLxqCshQO3A1FmjzGXbfIjTSXcysLfPfKM/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/GdiLSXePno8/mqdefault.jpg'
            }
        ]

        for item in self.data:
            if control.setting('lang_split') == '0':
                if 'Greek' in control.infoLabel('System.Language'):
                    li = control.item(label=item['title'].partition(' - ')[2])
                elif 'English' in control.infoLabel('System.Language'):
                    li = control.item(label=item['title'].partition(' - ')[0])
                else:
                    li = control.item(label=item['title'])
            elif control.setting('lang_split') == '1':
                li = control.item(label=item['title'].partition(' - ')[0])
            elif control.setting('lang_split') == '2':
                li = control.item(label=item['title'].partition(' - ')[2])
            else:
                li = control.item(label=item['title'])
            li.setArt({'icon': item['icon'], 'fanart': control.addonInfo('fanart')})
            self.list.append((item['url'], li, True))

        control.addItems(syshandle, self.list)
        control.directory(syshandle)

    def kids_songs(self):

        self.data = [
            {
                'title': u'Zouzounia TV kids songs - Παιδικά Τραγούδια από τα Ζουζούνια',
                'url': 'plugin://plugin.video.zouzounia.tv/',
                'icon': 'https://yt3.ggpht.com/-zhH35bOsqec/AAAAAAAAAAI/AAAAAAAAAAA/LxUO6o-ZHPc/s256-c-k-no-mo-rj-c0xffffff/photo.jpg'
            }
            ,
            {
                'title': u'Greek songs with lyrics No.1 - Ελληνικά παιδικά τραγούδια με στίχους No.1',
                'url': '{0}/channel/UCUmGu9Ncu5NeaEjwpLXW0PQ/'.format(YT_ADDON),
                'icon': 'https://yt3.ggpht.com/-MVbyrB7DJrY/AAAAAAAAAAI/AAAAAAAAAAA/WjLUCzyX3zI/s256-c-k-no-mo-rj-c0xffffff/photo.jpg'
            }
            ,
            {
                'title': u'Greek songs with lyrics No.2 - Ελληνικά παιδικά τραγούδια με στίχους No.2',
                'url': '{0}/channel/UCyENiZwRYzfXzbwP-Mxk9oA/'.format(YT_ADDON),
                'icon': 'https://yt3.ggpht.com/-Jdrq5I2r5Tc/AAAAAAAAAAI/AAAAAAAAAAA/z7IPqFS7jqA/s256-c-k-no-mo-rj-c0xffffff/photo.jpg'
            }
            ,
            {
                'title': u'Greek Karaoke - Ελληνικό Καραόκε',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeRlD0w1GXbitRL6sbyMscVi/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/Iz5P8xJel-U/mqdefault.jpg'
            }
            ,
            {
                'title': u'Karaoke for English Learning - Μαθαίνω Αγγλικά με καραόκε',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeSL-M5Q0qG3Eszj0I1O98bT/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/L2atYpQ7Zbg/mqdefault.jpg'
            }
            ,
            {
                'title': u'Learning Music for Kids - Μαθαίνω Μουσική, για παιδιά',
                'url': '{0}/channel/UCp_0VMwvn5LeJMhtreBFIcA/playlist/PLP25S0MkvCeRr5VH-HylSX89MHXQ_KyS0/'.format(YT_ADDON),
                'icon': 'https://i.ytimg.com/vi/w5tF5J_BNfI/mqdefault.jpg'
            }
        ]

        for item in self.data:
            if control.setting('lang_split') == '0':
                if 'Greek' in control.infoLabel('System.Language'):
                    li = control.item(label=item['title'].partition(' - ')[2])
                elif 'English' in control.infoLabel('System.Language'):
                    li = control.item(label=item['title'].partition(' - ')[0])
                else:
                    li = control.item(label=item['title'])
            elif control.setting('lang_split') == '1':
                li = control.item(label=item['title'].partition(' - ')[0])
            elif control.setting('lang_split') == '2':
                li = control.item(label=item['title'].partition(' - ')[2])
            else:
                li = control.item(label=item['title'])
            li.setArt({'icon': item['icon'], 'fanart': control.addonInfo('fanart')})
            self.list.append((item['url'], li, True))

        control.addItems(syshandle, self.list)
        control.directory(syshandle)

    @cache_method(cache_duration(180))
    def _cartoon_various(self, url):

        if url is None:
            url = '{0}/genre/kids'.format(GK_BASE)

        html = net_client().http_GET(url).content

        try:
            next_link = parseDOM(html, 'a', attrs={'class': 'arrow_pag'}, ret='href')[-1]
        except Exception:
            next_link = None

        html = parseDOM(html, 'div', attrs={'class': 'items'})[0]

        items = parseDOM(html, 'article', attrs={'id': r'post-\d+'})

        for item in items:

            h3 = parseDOM(item, 'h3')[0]
            title = parseDOM(h3, 'a')[0]
            title = replaceHTMLCodes(title)
            url = parseDOM(h3, 'a', ret='href')[0]

            meta = parseDOM(item, 'div', attrs={'class': 'metadata'})[0]

            try:

                span = parseDOM(meta, 'span')
                etos = [s for s in span if len(s) == 4][0]
                plot = parseDOM(item, 'div', attrs={'class': 'texto'})[0]
                duration = [s for s in span if s.endswith('min')][0]
                duration = int(re.search(r'(\d+)', duration).group(1)) * 60

            except IndexError:

                plot = u'Μεταγλωτισμένο'
                etos = '2022'
                duration = 3600

            year = ''.join(['(', etos, ')'])
            label = ' '.join([title, year])
            try:
                image = parseDOM(item, 'img', ret='data-lazy-src')[0]
            except Exception:
                image = parseDOM(item, 'img', ret='src')[0]

            i = {
                'title': title, 'label': label, 'url': url, 'image': image, 'nextlabel': 30334,
                'plot': plot, 'duration': duration, 'year': int(etos)
            }

            if next_link:
                i.update({'next': next_link, 'nexticon': iconname('next')})

            self.list.append(i)

        return self.list

    def cartoon_various(self, url):

        self.list = self._cartoon_various(url)

        for item in self.list:

            item.update({'action': 'play', 'isFolder': 'False', 'nextaction': 'cartoon_various'})

            refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
            unwatched_cm = {'title': 30228, 'query': {'action': 'toggle_watched'}}
            item.update({'cm': [refresh_cm, unwatched_cm]})

        directory.add(self.list)


@cache_function(cache_duration(360))
def gk_source_maker(link):

    html = net_client().http_GET(link).content
    urls = parseDOM(html, 'tr', attrs={'id': 'link-\d+'})
    item_data = parseDOM(html, 'div', attrs={'class': 'data'})[0]
    title = parseDOM(item_data, 'h1')[0]
    year = parseDOM(item_data, 'span', attrs={'itemprop': 'dateCreated'})[0]
    year = re.search(r'(\d{4})', year).group(1)
    image = parseDOM(html, 'img', attrs={'itemprop': 'image'}, ret='src')[0]
    urls = [u for u in parseDOM(urls, 'a', ret='href')]
    urls = [net_client(ssl_verify=False).http_GET(u).get_url() for u in urls]

    hosts = [''.join([control.lang(30015), urlsplit(url).netloc]) for url in urls]

    data = {
        'links': list(zip(hosts, urls)), 'title': title, 'year': int(year), 'image': image
    }

    return data
