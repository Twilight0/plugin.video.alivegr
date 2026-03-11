# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.
from __future__ import absolute_import, unicode_literals

import json, re

from tulip import control, directory
from tulip.parsers import parseDOM
from resolveurl.lib.net import Net as net_client
from tulip.log import log_debug
from tulip.compat import urljoin, iteritems
from ..modules.themes import iconname
from ..modules.constants import ART_ID, cache_method, cache_duration, YT_ADDON
from ..modules.utils import thgiliwt, thumb_maker, yt_playlist
from . import gm


# noinspection PyUnboundLocalVariable
class Indexer:

    def __init__(self):

        self.list = []; self.data = []
        self.mgreekz_id = 'https://www.youtube.com/channel/UClMj1LyMRBMu_TG1B1BirqQ/'
        self.mgreekz_id = self.mgreekz_id.replace('https://www.youtube.com/channel', '{0}/channel'.format(YT_ADDON))
        if control.setting('audio_only') == 'true' and control.condVisibility('Window.IsVisible(music)'):
            self.content = 'songs'
            self.infotype = 'music'
        else:
            self.content = 'musicvideos'
            self.infotype = 'video'

    def menu(self):

        self.list = [
            {
                'title': control.lang(30170),
                'action': 'music_live',
                'image': iconname('monitor'),
                'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
            }
            ,
            {
                'title': control.lang(30124),
                'action': 'gm_music',
                'image': iconname('music'),
                'fanart': 'https://cdn.allwallpaper.in/wallpapers/1280x720/1895/music-hd-1280x720-wallpaper.jpg'
            }
            ,
            {
                'title': control.lang(30126),
                'action': 'mgreekz_index',
                'image': 'https://pbs.twimg.com/profile_images/697098521527328772/VY8e_klm_400x400.png',
                'fanart': control.addonmedia(
                    addonid=ART_ID, theme='networks', icon='mgz_fanart.jpg', media_subfolder=False
                ),
                'isFolder': 'False', 'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(30269),
                'action': 'top50_list',
                'url': 's1GeuATNw9GdvcXYy9Cdl5mLydWZ2lGbh9yL6MHc0RHa',
                'image': control.addonInfo('icon'),
                'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
            }
            ,
            {
                'title': control.lang(30292),
                'action': 'techno_choices',
                'url': 'PLZF-_NNdxpb5s1vjh6YSMTyjjlfiZhgbp',
                'image': control.addonInfo('icon'),
                'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
            }
        ]

        if control.condVisibility('Window.IsVisible(music)'):
            del self.list[0]

        directory.add(self.list)

    def gm_music(self):

        html = gm.root(gm.MUSIC)

        options = re.compile(r'(<option  value=.+?</option>)', re.U).findall(html)

        for option in options:

            title = parseDOM(option, 'option')[0]
            link = parseDOM(option, 'option', ret='value')[0]
            link = urljoin(gm.GM_BASE, link)

            data = {'title': title, 'url': link, 'image': iconname('music'), 'action': 'artist_index'}

            self.list.append(data)

        directory.add(self.list)

    @cache_method(cache_duration(2880))
    def music_list(self, url):

        html = net_client().http_GET(url).content

        try:

            html = html.decode('utf-8')

        except Exception:

            pass

        if 'albumlist' in html:
            artist = [parseDOM(html, 'h4')[0].partition(' <a')[0]]
        else:
            artist = None

        if control.setting('audio_only') == 'true' and control.condVisibility('Window.IsVisible(music)') and artist is not None:
            artist = ''.join(artist)

        if 'songlist' in html:
            songlist = parseDOM(html, 'div', attrs={'class': 'songlist'})[0]
            items = parseDOM(songlist, 'li')
        elif 'albumlist' in html:
            albumlist = parseDOM(html, 'div', attrs={'class': 'albumlist'})[0]
            items = parseDOM(albumlist, 'li')
        else:
            artistlist = parseDOM(html, 'div', attrs={'class': 'artistlist'})[0]
            items = parseDOM(artistlist, 'li')

        if 'icon/music' in html:
            icon = parseDOM(html, 'img', attrs={'class': 'img-responsive'}, ret='src')[-1]
            icon = urljoin(gm.GM_BASE, icon)
        else:
            icon = iconname('music')

        for item in items:

            title = parseDOM(item, 'a')[0]
            link = parseDOM(item, 'a', ret='href')[0]
            link = urljoin(gm.GM_BASE, link)

            if 'gapi.client.setApiKey' in html:
                link = gm.gm_source_maker(url)['links'][0]

            data = {'title': title, 'url': link, 'image': icon}

            if artist:

                data.update({'artist': artist})

            self.list.append(data)

        return self.list

    def artist_index(self, url, get_list=False):

        self.list = self.music_list(url)

        for item in self.list:
            item.update({'action': 'album_index'})
            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            item.update({'cm': [bookmark_cm]})

        if get_list:
            return self.list
        else:
            directory.add(self.list)

    def album_index(self, url):

        self.list = self.music_list(url)

        for item in self.list:

            try:
                year = int(item['title'].partition(' (')[2][:-1])
            except ValueError:
                year = None

            item.update(
                {
                    'action': 'songs_index', 'name': item['title'].partition(' (')[0],
                }
            )

            if year:
                item.update({'year': year})

        directory.add(self.list, content=self.content, infotype=self.infotype)

    def songs_index(self, url, album):

        self.list = self.music_list(url)

        for count, item in list(enumerate(self.list, start=1)):

            item.update({'action': 'play', 'isFolder': 'False'})
            add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
            clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
            try:
                item.update({'cm': [add_to_playlist, clear_playlist], 'album': album.encode('latin-1'), 'tracknumber': count})
            except:
                item.update({'cm': [add_to_playlist, clear_playlist], 'album': album, 'tracknumber': count})

        directory.add(self.list, content=self.content, infotype=self.infotype)

    def mgreekz_index(self):

        control.execute('Container.Update("{0}")'.format(self.mgreekz_id))

    @cache_method(cache_duration(2880))
    def _top50(self, url):

        if control.setting('debug') == 'false':

            playlist = net_client().http_GET(thgiliwt(url), headers={'User-Agent': 'AliveGR, version: ' + control.version()}).content

        else:

            if control.setting('local_remote') == '0':
                local = control.setting('top50_local')
                try:
                    with open(local, encoding='utf-8') as xml:
                        playlist = xml.read()
                except Exception:
                    with open(local) as xml:
                        playlist = xml.read()
            elif control.setting('local_remote') == '1':
                playlist = net_client().http_GET(control.setting('top50_remote')).content
            else:
                playlist = net_client().http_GET(url).content

        self.data = parseDOM(playlist, 'item')

        for item in self.data:

            title = parseDOM(item, 'title')[0]
            genre = parseDOM(item, 'genre')[0]
            url = parseDOM(item, 'url')[0]
            image = thumb_maker(url.rpartition('=')[2])
            plot = parseDOM(item, 'description')[0]
            duration = parseDOM(item, 'duration')[0].split(':')
            duration = (int(duration[0]) * 60) + int(duration[1])

            item_data = (
                {
                    'label': title, 'title': title.partition(' - ')[2], 'image': image, 'url': url, 'plot': plot,
                    'comment': plot, 'duration': duration, 'genre': genre
                }
            )

            self.list.append(item_data)

        return self.list

    def top50_list(self, url):

        self.list = self._top50(url)

        if self.list is None:
            log_debug('Developer\'s picks section failed to load')
            return

        for count, item in list(enumerate(self.list, start=1)):
            add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
            clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
            item.update(
                {
                    'action': 'play', 'isFolder': 'False', 'cm': [add_to_playlist, clear_playlist],
                    'album': control.lang(30269), 'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg',
                    'tracknumber': count, 'code': count, 'artist': [item['label'].partition(' - ')[0]]
                }
            )

            if control.setting('audio_only') == 'true' and control.condVisibility('Window.IsVisible(music)'):
                item['artist'] = item['artist'][0]

        control.sortmethods('tracknum', mask='%A')
        directory.add(self.list, content=self.content, infotype=self.infotype)

    def techno_choices(self, url):

        self.list = yt_playlist(url)

        if self.list is None:

            return

        for i in self.list:
            i.update(
                {
                    'action': 'play', 'isFolder': 'False',
                }
            )

        directory.add(self.list)
