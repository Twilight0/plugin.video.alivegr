import re
import random
from urllib.parse import urljoin, urlparse
from tulip import kodi, cleantitle
from tulip.log import log
from netclient import Net
from itertags import iwrapper
from scrapetube.wrapper import list_search
from ..modules.constants import (
    cache_function, cache_duration, GM_BASE
)


@cache_function(cache_duration(360))
def gm_source_maker(url):

    if 'episode' in url:

        html = Net().http_POST(url.partition('?')[0], form_data=url.partition('?')[2]).content

    else:

        html = Net().http_GET(url).content

    if 'episode' in url:

        episodes = re.findall(r'''(?:<a.+?/a>|<p.+?/p>)''', html)

        hl = []
        links = []

        for episode in episodes:

            if '<p style="margin-top:0px; margin-bottom:4px;">' in episode:

                host = iwrapper(episode, 'p').__next__().text.split('<')

                pts = iwrapper(episode, 'a')
                lks = iwrapper(episode, 'a', ret='href')

                for p in pts:
                    hl.append(u''.join([host, kodi.i18n(30225), p.text]))

                for link_ in lks:
                    links.append(link_)

            else:

                pts = iwrapper(episode, 'a')
                lks = iwrapper(episode, 'a', ret='href')

                for p in pts:
                    hl.append(p.text)

                for link_ in lks:
                    links.append(link_)

        links = [urljoin(GM_BASE, link) for link in links]
        hosts = [host.replace(u'προβολή στο ', kodi.i18n(30015)) for host in hl]

        links_list = list(zip(hosts, links))

        data = {'links': links_list}

        if '<p class="text-muted text-justify">' in html:

            plot = iwrapper(html, 'p').__next__().text
            data.update({'plot': plot})

        return data

    elif 'view' in url:

        link = iwrapper(html, 'a', ret='href', attrs={"class": "btn btn-primary"}).__next__()
        host = urlparse(link).netloc.replace('www.', '').capitalize()

        return {'links': [(''.join([kodi.i18n(30015), host]), link)]}

    elif 'music' in url:

        title = re.search(r'''search\(['"](.+?)['"]\)''', html).group(1)

        link = list_search(query=title, limit=1)[0]['url']

        return {'links': [(''.join([kodi.i18n(30015), 'Youtube']), link)]}

    else:

        try:

            info = iwrapper(html, 'h4', attrs={'style': 'text-indent:10px;'}, lazify=True)

            if ',' in info[1].text:

                genre = info[1].text.lstrip(u'Είδος:').split(',')
                genre = random.choice(genre)
                genre = genre.strip()

            else:

                genre = info[1].text.lstrip(u'Είδος:').strip()

        except:

            genre = kodi.i18n(30147)

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

        data = {'links': links_list, 'genre': genre}

        if 'text-align: justify' in html:
            plot = iwrapper(html, 'p', attrs={'style': 'text-align: justify'}).__next__().text
        elif 'text-justify' in html:
            plot = iwrapper(html, 'p', attrs={'style': 'font-size:12pt.+'}).__next__().text
        else:
            plot = kodi.i18n(30085)

        log(plot)

        data.update({'plot': plot})

        imdb_code = re.search(r'imdb.+?/title/([\w]+?)/', html)

        if imdb_code:

            code = imdb_code.group(1)
            data.update({'code': code})

        return data

def gf_source_maker():

    pass
