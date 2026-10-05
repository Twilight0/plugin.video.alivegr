import re
from urllib.parse import urljoin, urlparse
from tulip import kodi, cleantitle
from netclient import Net
from itertags import iwrapper
from scrapetube.wrapper import list_search
from ..modules.constants import (
    cache_function, cache_duration, GM_BASE
)
from tulip.log import log


@cache_function(cache_duration(360))
def gm_source_maker(url):

    if 'episode' in url:

        html = Net().http_POST(url.partition('?')[0], form_data=url.partition('?')[2]).content
        title = iwrapper(html, 'div').__next__().text

    else:

        html = Net().http_GET(url).content

    if 'episode' in url:

        episodes = re.findall(r'''(?:<a.+?/a>|<p.+?/p>)''', html)

        hl = []
        links = []

        for episode in episodes:

            pts = iwrapper(episode, 'a')
            lks = iwrapper(episode, 'a', ret='href')

            for link_ in lks:
                links.append(link_)

            if '<p style="margin-top:0px; margin-bottom:4px;">' in episode:

                host = iwrapper(episode, 'p').__next__().text.split('<')[0]

                for p in pts:
                    hl.append(''.join([host, kodi.i18n(30225), p.text]))

            else:

                for p in pts:
                    hl.append(p.text)

        links = [urljoin(GM_BASE, link) for link in links]
        hosts = [host.replace(u'προβολή στο ', kodi.i18n(30015)) for host in hl]

        links_list = list(zip(hosts, links))

        # noinspection PyUnboundLocalVariable
        data = {'links': links_list, 'title': title}

        if '<p class="text-muted text-justify">' in html:

            plot = iwrapper(html, 'p').__next__().text
            data.update({'plot': plot})

        return data

    elif 'view' in url:

        try:
            title = iwrapper(html, 'h3').__next__().text
        except Exception:
            title = ''

        return {'links': [(kodi.i18n(30015), url)], 'title': title}

    elif 'music' in url:

        title = re.search(r'''search\(['"](.+?)['"]\)''', html).group(1)

        link = list_search(query=title, limit=1)[0]['url']

        return {'links': [(''.join([kodi.i18n(30015), 'Youtube']), link)]}

    else:

        title = iwrapper(html, 'h2').__next__().text

        try:

            info = iwrapper(html, 'h4', attrs={'style': 'text-indent:10px;'}, lazify=True)

            if ',' in info[1].text:

                genre = info[1].text.lstrip(u'Είδος:').split(',')
                genre = [g.strip() for g in genre]

            else:

                genre = info[1].text.lstrip(u'Είδος:').strip()
                genre = [genre]

        except:

            genre = [kodi.i18n(30147)]

        div_tags = iwrapper(html, 'div')

        buttons = [i.text for i in list(div_tags) if 'margin: 0px 0px 10px 10px;' in i.attributes.get('style', '')]

        links = []
        hl = []

        for button in buttons:

            if 'btn btn-primary dropdown-toggle' in button:

                host = cleantitle.stripTags(iwrapper(button, 'button').__next__().text).strip()
                parts = iwrapper(button, 'li')

                for part in parts:

                    part_ = iwrapper(part.text, 'a').__next__().text
                    link = iwrapper(part.text, 'a', ret='href').__next__()
                    hl.append(', '.join([host, part_]))
                    links.append(link)

            else:

                host = iwrapper(button, 'a').__next__().text
                link = iwrapper(button, 'a', ret='href').__next__()

                hl.append(host)
                links.append(link)

        links = [urljoin(GM_BASE, link) for link in links]

        hosts = [host.replace(
            u'προβολή στο ', kodi.i18n(30015)
        ).replace(
            u'προβολή σε ', kodi.i18n(30015)
        ).replace(
            u'μέρος ', kodi.i18n(30225)
        ) for host in hl]

        links_list = list(zip(hosts, links))

        data = {'links': links_list, 'genre': genre, 'title': title}

        try:
            year_match = re.search(r'Έτος:\s*(\d{4})', html)
            if year_match:
                data['year'] = int(year_match.group(1))
        except Exception:
            pass

        try:
            img = iwrapper(html, 'img', attrs={'class': 'thumbnail img-responsive'}, ret='src').__next__()
            data['image'] = urljoin(GM_BASE, img)
        except Exception:
            pass

        if 'text-align: justify' in html:
            plot = iwrapper(html, 'p', attrs={'style': 'text-align: justify'}).__next__().text
        elif 'text-justify' in html:
            plot = iwrapper(html, 'p', attrs={'style': 'font-size:12pt.+'}).__next__().text
        else:
            plot = kodi.i18n(30085)

        data.update({'plot': plot})

        imdb_code = re.search(r'imdb.+?/title/([\w]+?)/', html)

        if imdb_code:

            code = imdb_code.group(1)
            data.update({'code': code})

        return data
