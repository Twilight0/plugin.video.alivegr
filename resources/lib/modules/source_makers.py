import json
import re
import binascii
from urllib.parse import urljoin, urlparse, parse_qsl
from fuzzywuzzy import fuzz
from tulip import kodi, cleantitle
from netclient import Net
from useragents import spoofer
from itertags import iwrapper
from scrapetube.wrapper import list_search
from ..modules.constants import (
    cache_function, cache_duration, GM_BASE
)
from ..modules.utils import thgiliwt
from tulip.utils import py3_dec
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

        link = iwrapper(html, 'a', ret='href', attrs={"class": "btn btn-primary"}).__next__()
        host = urlparse(link).netloc.replace('www.', '').capitalize()
        title = iwrapper(html, 'h3').__next__().text

        return {'links': [(''.join([kodi.i18n(30015), host]), link)], 'title': title}

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


@cache_function(cache_duration(360))
def gf_source_maker(var, url=None, title=None, search=None):

    data = None
    gf_movies_list = gist_getter(var)

    if url:

        index = int(dict(parse_qsl(urlparse(url).query)).get('id', 0))

        item = [i for i in gf_movies_list if i['index'] == index][0]
        links = item['urls']
        hosts = [''.join([kodi.i18n(30015), urlparse(i).netloc.split('.')[0].capitalize()]) for i in links]
        plot = item['plot']
        genre = item.get('genre', [kodi.i18n(30089)])

        data = {
            'links': list(zip(hosts, links)), 'plot': plot, 'genre': genre, 'year': item['year'],
            'title': item['title'], 'label': item['label'], 'image': spoofer(item['image'])
        }

    elif title:

        try:

            for i in gf_movies_list:
                score = fuzz.ratio(i['title'].lower(), title.lower())
                if score <= 70:
                    score = fuzz.ratio(i['label'].lower(), title.lower())
                if score >= 71:
                    log(f"Match found! Score for '{i['title']}' vs '{title}': {score}")
                    item = i
                    break
            else:
                raise IndexError

            links = item['urls']
            hosts = [''.join([kodi.i18n(30015), urlparse(i).netloc.split('.')[0].capitalize()]) for i in item['urls']]
            plot = item['plot']
            genre = item.get('genre', [kodi.i18n(30089)])
    
            data = {
                'links': list(zip(hosts, links)), 'plot': plot, 'genre': genre, 'year': item['year'],
                'title': item['title'], 'label': item['label'], 'image': spoofer(item['image'])
            }

        except (IndexError, KeyError):

            pass

    elif search:

        log('Initiating search')


        try:

            # items = [
            #     dict(
            #         i, image=spoofer(i.get('image') or 'https://openclipart.org/image/800px/144715')
            #     ) for i in gf_movies_list if fuzz.ratio(i['title'], search) >= 50
            # ]

            items = []
            for i in gf_movies_list:
                score = fuzz.ratio(i['title'].lower(), search.lower())
                if score <= 50:
                    score = fuzz.ratio(i['label'].lower(), search.lower())
                if score >= 51:
                    log(f"Match found! Score for '{i['title']}' vs '{search}': {score}")
                    items.append(
                        dict(
                            i, image=spoofer(i.get('image') or 'https://openclipart.org/image/800px/144715')
                        )
                    )
    
            return items

        except (IndexError, KeyError) as e:

            log(f'Error in {__name__}: {e}')
            return []

    # noinspection PyUnboundLocalVariable
    return data


@cache_function(cache_duration(360))
def gist_getter(var):

    try:
        result = Net().http_GET(
            py3_dec(thgiliwt(var))
        ).content
    except binascii.Error:
        result = Net().http_GET(var).content

    return json.loads(result)
