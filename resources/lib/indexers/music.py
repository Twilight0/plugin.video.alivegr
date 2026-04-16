# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import json, re
from collections import deque
from xbmcaddon import Addon
from tulip import kodi, directory
from itertags import iwrapper
from netclient import Net
from tulip.utils import iteritems
from urllib.parse import urljoin
from ..modules.themes import iconname
from ..modules.source_makers import gm_source_maker
from ..modules.constants import cache_method, cache_duration, YT_ADDON, GM_MUSIC
from ..modules.utils import yt_playlist
from . import vod


# noinspection PyUnboundLocalVariable
class Indexer:

    def __init__(self):

        self.list = []; self.data = []
        self.mgreekz_id = 'https://www.youtube.com/channel/UClMj1LyMRBMu_TG1B1BirqQ/'
        self.mgreekz_id = self.mgreekz_id.replace('https://www.youtube.com/channel', '{0}/channel'.format(YT_ADDON))
        if Addon().getSetting('audio_only') == 'true' and kodi.condVisibility('Window.IsVisible(music)'):
            self.content = 'songs'
            self.infotype = 'music'
        else:
            self.content = 'musicvideos'
            self.infotype = 'video'

    def menu(self):

        self.list = [
            {
                'title': kodi.i18n(30170),
                'action': 'music_live',
                'image': iconname('monitor'),
                'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg',
                'isFolder': 'True'
            }
            ,
            {
                'title': kodi.i18n(30124),
                'action': 'gm_music',
                'image': iconname('music'),
                'fanart': 'https://cdn.allwallpaper.in/wallpapers/1280x720/1895/music-hd-1280x720-wallpaper.jpg',
                'isFolder': 'True'
            }
            # ,
            # {
            #     'title': kodi.i18n(30126),
            #     'action': 'mgreekz_index',
            #     'image': 'https://pbs.twimg.com/profile_images/697098521527328772/VY8e_klm_400x400.png',
            #     'fanart': kodi.addonmedia(
            #         addonid=ART_ID, theme='networks', path='mgz_fanart.jpg', media_subfolder=False
            #     ),
            #     'isFolder': 'False', 'isPlayable': 'False'
            # }
            # ,
            # {
            #     'title': kodi.i18n(30269),
            #     'action': 'top50_list',
            #     'url': 's1GeuATNw9GdvcXYy9Cdl5mLydWZ2lGbh9yL6MHc0RHa',
            #     'image': kodi.addonInfo('icon'),
            #     'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
            # }
            # ,
            # {
            #     'title': kodi.i18n(30292),
            #     'action': 'techno_choices',
            #     'url': 'PLZF-_NNdxpb5s1vjh6YSMTyjjlfiZhgbp',
            #     'image': kodi.addonInfo('icon'),
            #     'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg',
            #     'isFolder': 'True'
            # }
        ]

        if kodi.condVisibility('Window.IsVisible(music)'):
            del self.list[0]

        directory.builder(self.list)

    def gm_music(self):

        html = vod.gm_root(GM_MUSIC)

        options = re.compile(r'(<option  value=.+?</option>)', re.U).findall(html)

        for option in options:

            obj = iwrapper(option, 'option').__next__()
            title = obj.text
            link = urljoin(vod.GM_BASE, obj.attributes['value'])

            data = {
                'title': title, 'url': link, 'image': iconname('music'), 'action': 'artist_index',
                'isFolder': 'True'
            }

            self.list.append(data)

        directory.builder(self.list)

    @cache_method(cache_duration(2880))
    def music_list(self, url):

        html = Net().http_GET(url).content

        try:

            html = html.decode('utf-8')

        except Exception:

            pass

        if 'albumlist' in html:
            artist = [iwrapper(html, 'h4').__next__().text.partition(' <a')[0]]
        else:
            artist = None

        if Addon().getSetting('audio_only') == 'true' and kodi.condVisibility('Window.IsVisible(music)') and artist is not None:
            artist = ''.join(artist)

        if 'songlist' in html:
            songlist = iwrapper(html, 'div', attrs={'class': 'songlist'}).__next__().text
            items = iwrapper(songlist, 'li')
        elif 'albumlist' in html:
            albumlist = iwrapper(html, 'div', attrs={'class': 'albumlist'}).__next__().text
            items = iwrapper(albumlist, 'li')
        else:
            artistlist = iwrapper(html, 'div', attrs={'class': 'artistlist'}).__next__().text
            items = iwrapper(artistlist, 'li')

        if 'icon/music' in html:
            icon = deque(iwrapper(html, 'img', attrs={'class': 'img-responsive'}, ret='src'), maxlen=1).pop()
            icon = urljoin(vod.GM_BASE, icon)
        else:
            icon = iconname('music')

        for item in items:

            title = iwrapper(item.text, 'a').__next__().text
            link = iwrapper(item.text, 'a', ret='href').__next__()
            link = urljoin(vod.GM_BASE, link)

            if 'gapi.client.setApiKey' in html:
                link = gm_source_maker(url)['links'][0]

            data = {'title': title, 'url': link, 'image': icon}

            if artist:

                data.update({'artist': artist})

            self.list.append(data)

        return self.list

    def artist_index(self, url, get_list=False):

        self.list = self.music_list(url)

        for item in self.list:
            item.update({'action': 'album_index', 'isFolder': 'True'})
            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            item.update({'cm': [bookmark_cm]})

        if get_list:
            return self.list
        else:
            directory.builder(self.list)

    def album_index(self, url):

        self.list = self.music_list(url)

        for item in self.list:

            try:
                year = int(item['title'].partition(' (')[2][:-1])
            except ValueError:
                year = None

            item.update(
                {
                    'action': 'songs_index', 'name': item['title'].partition(' (')[0], 'isFolder': 'True'
                }
            )

            if year:
                item.update({'year': year})

        directory.builder(self.list, content=self.content, infotype=self.infotype)

    def songs_index(self, url, album):

        self.list = self.music_list(url)

        for count, item in list(enumerate(self.list, start=1)):

            item.update({'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})
            add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
            clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
            try:
                item.update({'cm': [add_to_playlist, clear_playlist], 'album': album.encode('latin-1'), 'tracknumber': count})
            except:
                item.update({'cm': [add_to_playlist, clear_playlist], 'album': album, 'tracknumber': count})

        directory.builder(self.list, content=self.content, infotype=self.infotype)

    # def mgreekz_index(self):
    #
    #     kodi.execute('Container.Update("{0}")'.format(self.mgreekz_id))

    # @cache_method(cache_duration(2880))
    # def _top50(self, url):
    #
    #     if kodi.setting('debug') == 'false':
    #
    #         playlist = Net().http_GET(thgiliwt(url), headers={'User-Agent': 'AliveGR, version: ' + kodi.version()}).content
    #
    #     else:
    #
    #         if kodi.setting('local_remote') == '0':
    #             local = kodi.setting('top50_local')
    #             try:
    #                 with open(local, encoding='utf-8') as xml:
    #                     playlist = xml.read()
    #             except Exception:
    #                 with open(local) as xml:
    #                     playlist = xml.read()
    #         elif kodi.setting('local_remote') == '1':
    #             playlist = Net().http_GET(kodi.setting('top50_remote')).content
    #         else:
    #             playlist = Net().http_GET(url).content
    #
    #     self.data = iwrapper(playlist, 'item')
    #
    #     for item in self.data:
    #
    #         title = parseDOM(item, 'title')[0]
    #         genre = parseDOM(item, 'genre')[0]
    #         url = parseDOM(item, 'url')[0]
    #         image = thumb_maker(url.rpartition('=')[2])
    #         plot = parseDOM(item, 'description')[0]
    #         duration = parseDOM(item, 'duration')[0].split(':')
    #         duration = (int(duration[0]) * 60) + int(duration[1])
    #
    #         item_data = (
    #             {
    #                 'label': title, 'title': title.partition(' - ')[2], 'image': image, 'url': url, 'plot': plot,
    #                 'comment': plot, 'duration': duration, 'genre': genre
    #             }
    #         )
    #
    #         self.list.append(item_data)
    #
    #     return self.list

    # def top50_list(self, url):
    #
    #     self.list = self._top50(url)
    #
    #     if self.list is None:
    #         log('Developer\'s picks section failed to load')
    #         return
    #
    #     for count, item in list(enumerate(self.list, start=1)):
    #         add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
    #         clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
    #         item.update(
    #             {
    #                 'action': 'play', 'isFolder': 'False', 'cm': [add_to_playlist, clear_playlist],
    #                 'album': kodi.i18n(30269), 'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg',
    #                 'tracknumber': count, 'code': count, 'artist': [item['label'].partition(' - ')[0]],
    #                 'isPlayable': 'True'
    #             }
    #         )
    #
    #         if kodi.setting('audio_only') == 'true' and kodi.condVisibility('Window.IsVisible(music)'):
    #             item['artist'] = item['artist'][0]
    #
    #     kodi.setsortmethod('tracknum', mask='%A')
    #     directory.builder(self.list, content=self.content, infotype=self.infotype)

    def techno_choices(self, url):

        self.list = yt_playlist(url)

        if self.list is None:

            return

        for i in self.list:
            i.update(
                {
                    'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'
                }
            )

        directory.builder(self.list)
