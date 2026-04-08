# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import re
import json
from urllib.parse import urljoin, urlparse
from tulip import directory, kodi, cleantitle
from tulip.utils import list_divider, iteritems
from netclient import Net
from itertags import iwrapper
from ..modules.themes import iconname
from ..modules.constants import (
    cache_function, cache_method, cache_duration, SEPARATOR, GM_BASE, GM_MOVIES, GM_SHOWS, GM_SERIES, GM_ANIMATION, GM_THEATER,
    GM_SPORTS, GM_SHORTFILMS, GM_MUSIC, GM_SEARCH, GM_PERSON, GM_EPISODE
)
from ..modules.utils import page_menu


@cache_function(cache_duration(720))
def gm_root(url):

    root_list = []
    groups_list = []

    html = Net().http_GET(url).content

    if url == GM_SPORTS:

        sports_index = iwrapper(html, 'div', attrs={'class': 'col-xs-6 text-center'}).__next__().text
        return sports_index

    elif url == GM_MUSIC:

        music_index = iwrapper(html, 'div', attrs={'class': 'col-sm-5 col-md-4'}).__next__().text
        return music_index

    else:

        result = iwrapper(html, 'div', attrs={'class': 'row', 'style': 'margin-bottom: 20px;'}).__next__().text
        items = re.findall('(<option  ?value=.*?</option>)', result, re.U)
        groups = iwrapper(result, 'option', attrs={'selected': None})

        for group_match in groups:

            group = group_match.text
            if group == u'ΑΡΧΙΚΑ':
                group = group.replace(u'ΑΡΧΙΚΑ', '30213')
            elif group == u'ΕΤΟΣ':
                group = group.replace(u'ΕΤΟΣ', '30090')
            elif group == u'ΚΑΝΑΛΙ':
                group = group.replace(u'ΚΑΝΑΛΙ', '30211')
            elif group == u'ΕΙΔΟΣ':
                group = group.replace(u'ΕΙΔΟΣ', '30200')
            elif group == u'ΠΑΡΑΓΩΓΗ':
                group = group.replace(u'ΠΑΡΑΓΩΓΗ', '30212')
            groups_list.append(group)

        for item in items:

            name = iwrapper(item, 'option', attrs={'value': '.+?.php.+?'}).__next__().text
            name = name.replace(u'σήμερα', kodi.i18n(30268))
            title = name[0].capitalize() + name[1:]
            link = iwrapper(item, 'option', ret='value').__next__()
            indexer = urlparse(link).query
            index = urljoin(GM_BASE, link)

            if indexer.startswith('l='):
                group = '30213'
            elif indexer.startswith('y='):
                group = '30090'
            elif indexer.startswith('c='):
                group = '30211'
            elif indexer.startswith('g='):
                group = '30200'
            elif indexer.startswith('p='):
                group = '30212'
            else:
                group = ''

            root_list.append({'title': title, 'group': group, 'url': index})

        return root_list, groups_list


class Indexer:

    def __init__(self):

        self.list = []
        self.data = []
        self.years = []

        self.switch = {
            'title': kodi.i18n(30045).format(kodi.i18n(int(kodi.setting('vod_group')))),
            'icon': iconname('switcher'), 'action': 'vod_switcher', 'isFolder': 'False', 'isPlayable': 'False'
        }

    def vod_switcher(self, url):

        _, self.data = gm_root(url)

        translated = [kodi.i18n(int(i)) for i in self.data]

        choice = kodi.selectDialog(heading=kodi.i18n(30062), list=translated)

        if choice <= len(self.data) and not choice == -1:
            kodi.setSetting('vod_group', self.data[choice])
            kodi.idle()
            kodi.sleep(100)  # ensure setting has been saved
            kodi.refresh()
        else:
            kodi.execute('Dialog.Close(all)')

    def movies(self):

        self.data, _ = gm_root(GM_MOVIES)

        try:
            self.list = [item for item in self.data if item['group'] == kodi.setting('vod_group')]
        except Exception:
            kodi.setSetting('vod_group', '30213')
            self.list = self.data

        # cm_menu = {'title': 30034, 'query': {'action': 'refresh'}}

        for item in self.list:

            item.update({'icon': iconname('movies'), 'action': 'listing', 'isFolder': 'True'})

        if kodi.setting('show_vod_switcher'):

            self.switch.update({'url': GM_MOVIES})

            self.list.insert(0, self.switch)

        directory.builder(self.list)

    def short_films(self):

        self.data = gm_root(GM_SHORTFILMS)[0]

        try:
            self.list = [item for item in self.data if item['group'] == kodi.setting('vod_group')]
        except Exception:
            kodi.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('short'), 'action': 'listing', 'isFolder': 'True'})

        if kodi.setting('show_vod_switcher'):

            self.switch.update({'url': GM_SHORTFILMS})
            self.list.insert(0, self.switch)

        directory.builder(self.list)

    def series(self):

        self.data = gm_root(GM_SERIES)[0]

        try:
            self.list = [item for item in self.data if item['group'] == kodi.setting('vod_group')]
        except Exception:
            kodi.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('series'), 'action': 'listing', 'isFolder': 'True'})

        if kodi.setting('show_vod_switcher'):
            self.switch.update({'url': GM_SERIES})

            self.list.insert(0, self.switch)

        directory.builder(self.list)

    def shows(self):

        self.data = gm_root(GM_SHOWS)[0]

        try:
            self.list = [item for item in self.data if item['group'] == kodi.setting('vod_group')]
        except Exception:
            kodi.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('shows'), 'action': 'listing', 'isFolder': 'True'})

        if kodi.setting('show_vod_switcher'):
            self.switch.update({'url': GM_SHOWS})

            self.list.insert(0, self.switch)

        directory.builder(self.list)

    def cartoons_series(self):

        self.data = gm_root(GM_ANIMATION)[0]

        try:
            self.list = [item for item in self.data if item['group'] == kodi.setting('vod_group')]
        except Exception:
            kodi.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('cartoon_series'), 'action': 'listing', 'isFolder': 'True'})

        if kodi.setting('show_vod_switcher'):
            self.switch.update({'url': GM_ANIMATION})

            self.list.insert(0, self.switch)

        directory.builder(self.list)

    def theater(self):

        self.data = gm_root(GM_THEATER)[0]

        try:
            self.list = [item for item in self.data if item['group'] == kodi.setting('vod_group')]
        except Exception:
            kodi.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('theater'), 'action': 'listing', 'isFolder': 'True'})

        if kodi.setting('show_vod_switcher'):
            self.switch.update({'url': GM_THEATER})

            self.list.insert(0, self.switch)

        directory.builder(self.list)

    @cache_method(cache_duration(720))
    def items_list(self, url, post=None):

        indexer = urlparse(url).query

        ################################################################################################
        #                                                                                              #
        if 'movies.php' in url:                                                                        #
            length = 10                                                                                #
        elif 'shortfilm.php' in url:                                                                   #
            length = 6                                                                                 #
        elif 'theater.php' in url:                                                                     #
            length = 8                                                                                 #                                                                                    #
        else:                                                                                          #
            length = 2                                                                                 #
        #                                                                                              #
        ################################################################################################

        for year in range(1, length):

            if indexer.startswith('l='):
                p = 'y=' + str(year) + '&g=&p='
            elif indexer.startswith('g='):
                p = 'y=' + str(year) + '&l=&p='
            elif indexer.startswith('p='):
                p = 'y=' + str(year) + '&l=&g='
            elif indexer.startswith('c='):
                p = 'y=' + str(year) + '&l=&g='
            else:
                p = ''

            self.years.append(p)

        if indexer.startswith(
                ('l=', 'g=', 's=', 'p=', 'c=')
        ) and 'movies.php' in url or 'shortfilm.php' in url or 'theater.php' in url:

            for content in self.years:
                links = GM_BASE + url.rpartition('/')[2].partition('&')[0] + '&' + content
                htmls = Net().http_GET(links).content
                self.data.append(htmls)

            result = u''.join(self.data)

            content = iwrapper(result, 'div', attrs={'class': 'col-xs-6 col-sm-4 col-md-3'})

        else:

            if post:
                html = Net().http_POST(url, form_data=post).content
            else:
                html = Net().http_GET(url).content

            content = iwrapper(html, 'div', attrs={'class': 'col-xs-6 col-sm-4 col-md-3'})

        contents = ''.join([i.text for i in list(content)])
        items = re.findall('(<a.*?href.*?div.*?</a>)', contents, re.U)

        for item in items:

            title = iwrapper(item, 'h4').__next__().text

            image = iwrapper(item, 'img', ret='src').__next__()

            image = urljoin(GM_BASE, image)
            link = iwrapper(item, 'a', ret='href').__next__()
            link = urljoin(GM_BASE, link)
            pattern = re.compile(r'(.*?) \((\d{4})')
            label = pattern.search(title)
            year = int(label.group(2))
            name = label.group(1)

            self.list.append(
                {
                    'label': title, 'title': name, 'url': link, 'image': image, 'year': year, 'name': name
                }
            )

        return self.list

    def listing(self, url, post=None, get_listing=False):

        self.list = self.items_list(url, post)

        for item in self.list:

            item['url'] = item['url'].replace('http://', 'https://')

            if url.startswith(
                    (
                            GM_MOVIES, GM_THEATER, GM_SHORTFILMS, GM_PERSON, GM_SEARCH
                    )
            ) and item['url'].startswith(
                (
                        GM_MOVIES, GM_THEATER, GM_SHORTFILMS, GM_PERSON
                )
            ):
                item.update({'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})
            elif url.startswith(GM_SPORTS):
                item.update({'action': 'events', 'isFolder': 'True'})
            else:
                item.update({'action': 'episodes', 'isFolder': 'True'})

        for item in self.list:

            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
            item.update({'cm': [bookmark_cm, refresh_cm]})

        if get_listing:

            return self.list

        if len(self.list) > int(kodi.setting('pagination_integer')) and kodi.setting('paginate_items') == 'true':

            if kodi.setting('sort_method') == '0':

                self.list.sort(
                    key=lambda k: cleantitle.strip_accents(k['title'].lower()),
                    reverse=kodi.setting('reverse_order') == 'true'
                )

            elif kodi.setting('sort_method') == '1':

                self.list.sort(key=lambda k: k['year'], reverse=kodi.setting('reverse_order') == 'true')

            try:

                pages = list_divider(self.list, int(kodi.setting('pagination_integer')))
                self.list = pages[int(kodi.setting('page'))]
                reset = False

            except Exception:

                pages = list_divider(self.list, int(kodi.setting('pagination_integer')))
                self.list = pages[0]
                reset = True

            self.list.insert(0, page_menu(len(pages), reset=reset))

        if kodi.setting('paginate_items') == 'false' or len(self.list) <= int(kodi.setting('pagination_integer')):

            kodi.setsortmethod(mask='%Y')
            kodi.setsortmethod('label', mask='%Y')
            kodi.setsortmethod('year')

        if url.startswith((GM_MOVIES, GM_THEATER, GM_SHORTFILMS)):
            directory.builder(self.list, content='movies')
        else:
            directory.builder(self.list, content='tvshows')

    @cache_method(cache_duration(720))
    def epeisodia(self, url):

        html = Net().http_GET(url).content
        image = iwrapper(html, 'img', attrs={'class': 'thumbnail.*?'}, ret='src').__next__()
        image = urljoin(GM_BASE, image)
        try:
            year = iwrapper(html, 'h4', attrs={'style': 'text-indent:10px;'}).__next__().text
        except (IndexError, StopIteration):
            year = iwrapper(html, 'h4', attrs={'style': 'padding-left:10px;'}).__next__().text
        year = int(re.search(r'(\d{4})', year).group(1))
        name = iwrapper(html, 'h2').__next__().text

        result = iwrapper(html, 'div', attrs={'style': 'margin:20px 0px 20px 0px;'}).__next__().text

        episodes = re.findall(r'onclick="loadEpisode(.*?)">(.*?)</button>', result)

        if str('text-justify') in html:
            plot = iwrapper(html, 'p', attrs={'class': 'text-justify'}).__next__().text
        else:
            plot = kodi.i18n(30085)

        try:
            info = iwrapper(html, 'h4', attrs={'style': 'text-indent:10px;'}, lazify=True)
            genre = info[1].text.lstrip(u'Είδος:').strip()
        except IndexError:
            info = iwrapper(html, 'h4', attrs={'style': 'padding-left:10px;'}, lazify=True)
            genre = info[1].text.lstrip(u'Είδος:').strip()

        dictionary = {
            u'Ιαν': '01', u'Φεβ': '02', u'Μάρ': '03',
            u'Απρ': '04', u'Μάι': '05', u'Ιούν': '06',
            u'Ιούλ': '07', 'Αύγ': '08', u'Σεπ': '09',
            u'Οκτ': '10', u'Νοέ': '11', u'Δεκ': '12'
        }

        for eid, title in episodes:

            link = re.search(r'\'([\w-]+)\', \'(\w{1,2})\'', eid)
            link = GM_EPISODE.format(link.group(1), link.group(2))

            if '\'n\')' in eid:
                group = '1bynumber'
                if '.' in title:
                    try:
                        season = title.partition('.')[0]
                    except Exception:
                        season = title.partition('.')[0][0]
                    episode_num = title.partition('.')[2]
                    title = kodi.i18n(30067) + ' ' + season + '.' + episode_num
                else:
                    title = kodi.i18n(30067) + ' ' + title
            elif '\'d\')' in eid:
                group = '2bydate'
                row = result.split(eid)[0]
                y = re.findall(r'<h4.+?bold.+?(\d{4})', row, re.U)[-1]
                m = re.findall(r'width:50px..?>(.+?)<', row, re.U)[-1]
                m = dictionary[m]
                prefix = '0' + title if len(title) == 1 else title
                title = prefix + '-' + m + '-' + y
            else:
                group = '3bytitle'

            self.list.append(
                {
                    'label': name + SEPARATOR + title, 'title': name + ' - ' + title, 'url': link, 'group': group,
                    'name': name, 'image': image, 'plot': plot, 'year': year,
                    'genre': genre
                }
            )

        return self.list

    def episodes(self, url):

        self.list = self.epeisodia(url)

        for item in self.list:

            refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
            item.update({'action': 'play', 'isFolder': 'False', 'isPlayable': 'True', 'cm': [refresh_cm]})

        if kodi.setting('episodes_reverse') == 'true':

            self.list = sorted(
                self.list,
                key=lambda k: k['group'] if k['group'] in ['1bynumber', '2bydate'] else k['title'], reverse=True
            )[::-1]

        else:

            self.list = sorted(self.list, key=lambda k: k['group'])

        if len(self.list) > int(kodi.setting('pagination_integer')) and kodi.setting('paginate_items') == 'true':

            try:

                pages = list_divider(self.list, int(kodi.setting('pagination_integer')))
                self.list = pages[int(kodi.setting('page'))]
                reset = False

            except Exception:

                pages = list_divider(self.list, int(kodi.setting('pagination_integer')))
                self.list = pages[0]
                reset = True

            self.list.insert(0, page_menu(len(pages), reset=reset))

        kodi.setsortmethod()
        # kodi.setsortmethod('title')
        # kodi.setsortmethod('year')

        directory.builder(self.list, content='episodes')

    def gm_sports(self):

        html = gm_root(GM_SPORTS)

        options = re.compile('(<option value.+?</option>)', re.U).findall(html)

        icons = ['https://www.shareicon.net/data/256x256/2015/11/08/157712_sport_512x512.png',
                 'https://www.shareicon.net/data/256x256/2015/12/07/196797_ball_256x256.png']

        items = list(zip(options, icons))

        for item, image in items:

            title = iwrapper(item, 'option').__next__().text
            url = iwrapper(item, 'option', ret='value').__next__()
            url = cleantitle.replaceHTMLCodes(url)
            index = urljoin(GM_BASE, url)

            data = {
                'title': title, 'action': 'listing', 'url': index,
                'image': image, 'isFolder': 'True', 'isPlayable': 'False'
            }
            self.list.append(data)

        directory.builder(self.list)

    @cache_method(cache_duration(720))
    def event_list(self, url):

        html = Net().http_GET(url).content
        items = iwrapper(html, 'div', attrs={'style': 'margin-bottom: 10px'})

        for item in items:

            title = iwrapper(item.text, 'a', attrs={'class': 'btn btn-default'}).__next__().text
            image = iwrapper(html, 'img', attrs={'class': 'thumbnail img-responsive pull-right'}, ret='src').__next__()
            image = urljoin(GM_BASE, image)
            link = iwrapper(item, 'button', attrs={'class': 'btn btn-default'}, ret='href').__next__()
            link = urljoin(GM_BASE, link)
            plot = iwrapper(item, 'span', attrs={'class': 'pull-right'}).__next__().text

            self.list.append(
                {
                    'title': title, 'url': link, 'plot': plot,
                    'image': image
                }
            )

        return self.list

    def events(self, url):

        self.list = self.event_list(url)

        for item in self.list:
            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            item.update({'cm': [bookmark_cm], 'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})

        directory.builder(self.list)

    @cache_method(cache_duration(720))
    def persons_listing(self, url, post):

        html = Net().http_POST(url, form_data=post).content

        content = iwrapper(html, 'div', attrs={'style': 'margin-left:20px;'}).__next__().text

        persons = iwrapper(content, 'h4')

        for person in persons:

            title = iwrapper(person.text, 'a').__next__().text
            url = urljoin(GM_BASE, iwrapper(person.text, 'a', ret='href').__next__())

            i = {'title': title, 'url': url}

            self.list.append(i)

        return self.list

    def persons_index(self, url, post, get_list=True):

        self.list = self.persons_listing(url, post)

        if self.list is None:
            return

        for item in self.list:

            item.update({'action': 'listing', 'isFolder': 'True', 'icon': iconname('user')})

            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
            item.update({'cm': [bookmark_cm, refresh_cm]})

        if get_list:
            return self.list
        else:
            directory.builder(self.list)
