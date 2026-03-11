# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.
from __future__ import absolute_import, unicode_literals

import json

from random import shuffle, choice as random_choice
from resolveurl import add_plugin_dirs, resolve as resolve_url
from resolveurl.hmf import HostedMediaFile
from resolveurl.resolver import ResolverError
# noinspection PyUnresolvedReferences
from youtube_plugin.youtube.youtube_exceptions import YouTubeException
from tulip import directory, control
from tulip.log import log_debug
from resolveurl.lib.net import Net as net_client
from tulip.compat import urljoin, parse_qsl, urlencode, is_py2, urlparse, HTTPError
from tulip.utils import percent
from tulip.parsers import parseDOM
from tulip.cleantitle import stripTags
from scrapetube.wrapper import list_playlist_videos, list_channel_videos

from ..indexers.gm import MOVIES, SHORTFILMS, THEATER, GM_BASE, gm_source_maker, Indexer as gm_indexer
from ..indexers.kids import GK_BASE, gk_source_maker
from ..resolvers import youtube
from .kodi import prevent_failure
from .constants import YT_URL, HOSTS, SEPARATOR, PLUGINS_PATH, cache_function, cache_duration, PLAYBACK_HISTORY
from .utils import m3u8_picker, add_to_file

skip_directory = False


def conditionals(url):

    add_plugin_dirs(control.transPath(PLUGINS_PATH))

    def yt(uri):

        if uri.startswith('plugin://'):
            return uri

        if len(uri) == 11:

            uri = YT_URL + uri

        try:
            return youtube.wrapper(uri)
        except YouTubeException as exp:
            log_debug('Youtube resolver failure, reason: ' + repr(exp))
            return


    if not url:
        control.close_all()
        return

    if 'youtu' in url or len(url) == 11:

        log_debug('Resolving with youtube addon...')

        return yt(url)

    elif HOSTS(url) and HostedMediaFile(url).valid_url():

        try:
            stream = resolve_url(url)
            log_debug('Resolving with Resolveurl...')
        except HTTPError:
            return url

        return stream

    elif HostedMediaFile(url).valid_url():

        if control.setting('show_alt_vod') == 'true':

            try:
                stream = resolve_url(url)
                log_debug('Resolving with Resolveurl...')
            except ResolverError:
                return
            except HTTPError:
                return url

            return stream

        else:

            control.okDialog('AliveGR', control.lang(30354))
            return 'https://static.adman.gr/inpage/blank.mp4'

    elif GM_BASE in url:

        sources = gm_source_maker(url)
        stream = mini_picker(sources['links'])

        return conditionals(stream)

    elif urlparse(GK_BASE).netloc in url:

        streams = gk_source_maker(url)
        stream = mini_picker(streams['links'])

        if control.setting('check_streams') == 'true':
            return stream
        else:
            return conditionals(stream)

    else:

        log_debug('Passing direct link...')

        return url


def check_stream(stream_list, shuffle_list=False, start_from=0, show_pd=False, cycle_list=True):

    if not stream_list:
        return

    if shuffle_list:
        shuffle(stream_list)

    for (c, (h, stream)) in list(enumerate(stream_list[start_from:])):

        if stream.endswith('blank.mp4'):
            return stream

        if show_pd:
            pd = control.progressDialog
            pd.create(control.name(), ''.join([control.lang(30459), h.partition(': ')[2]]))

        try:
            resolved = conditionals(stream)
        except Exception:
            resolved = None

        if resolved is not None:
            if show_pd:
                pd.close()
            return resolved
        elif show_pd and pd.iscanceled():
            return
        elif c == len(stream_list[start_from:]) and not resolved:
            control.infoDialog(control.lang(30411))
            if show_pd:
                pd.close()
        elif resolved is None:
            if cycle_list:
                log_debug('Removing unplayable stream: {0}'.format(stream))
                stream_list.remove((h, stream))
                return check_stream(stream_list)
            else:
                if show_pd:
                    _percent = percent(c, len(stream_list[start_from:]))
                    pd.update(_percent, ''.join([control.lang(30459), h.partition(': ')[2]]))
                control.sleep(1000)
                continue


def mini_picker(links):

    if len(links) == 1:

        stream = links[0][1]

        return stream

    elif control.setting('action_type') == '2' or skip_directory:

        try:
            if control.setting('check_streams') == 'false':
                stream = random_choice([link[1] for link in links])
            else:
                stream = check_stream(links)
        except Exception:
            return

        return stream

    else:

        choice = control.selectDialog(heading=control.lang(30064), list=[link[0] for link in links])

        if choice == -1:
            return
        elif control.setting('check_streams') == 'false':
            return [link[1] for link in links][choice]
        else:
            return check_stream(links, False, start_from=choice, show_pd=True, cycle_list=False)


def gm_directory(url, params):

    sources = gm_source_maker(url)

    lists = sources['links']

    items = []

    try:
        description = sources['plot']
    except KeyError:
        try:
            description = params.get('plot').encode('latin-1')
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
            description = params.get('plot')
        if not description:
            description = control.lang(30085)

    try:
        genre = sources['genre']
    except KeyError:
        genre = control.lang(30147)

    for h, l in lists:

        html = net_client(ssl_verify=False).http_GET(l).content
        button = parseDOM(html, 'a', attrs={'role': 'button'}, ret='href')[0]
        image = parseDOM(html, 'img', attrs={'class': 'thumbnail img-responsive'}, ret='src')[0]
        image = urljoin(GM_BASE, image)
        title = parseDOM(html, 'h3')[0]
        year = [y[-4:] for y in parseDOM(html, 'h4') if str(y[-4:]).isdigit()][0]
        try:
            episode = stripTags(parseDOM(html, 'h4')[-1])
            if episode[-4:].isdigit():
                raise IndexError
            episode = episode.partition(': ')[2].strip()
            label = title + ' - ' + episode + SEPARATOR + h
            title = title + ' - ' + episode
        except IndexError:
            label = title + SEPARATOR + h
        # plot = title + '[CR]' + control.lang(30090) + ': ' + year + '[CR]' + description

        if is_py2:
            title = title + ' ({})'.format(year)

        data = {
            'label': label, 'title': title, 'url': button, 'image': image, 'plot': description,
            'year': int(year), 'genre': genre, 'name': title
        }

        if control.setting('check_streams') == 'true':
            data.update({'query': json.dumps(sources['links'])})

        items.append(data)

    return items


def gk_directory(url):

    items = []

    sources = gk_source_maker(url)

    links = sources['links']

    t = sources['title']
    y = sources['year']
    i = sources['image']

    for h, l in links:

        label = SEPARATOR.join([t, h])

        data = {
            'label': label, 'title': '{0} ({1})'.format(t, y), 'url': l, 'image': i, 'year': y
        }

        if control.setting('check_streams') == 'true':
            data.update({'query': json.dumps(links)})

        items.append(data)

    return items


@cache_function(cache_duration(660))
def items_directory(url, params):

    if 'greek-movies.com' in url:

        return gm_directory(url, params)

    else:

        return gk_directory(url)


def directory_picker(url, argv):

    params = dict(parse_qsl(argv[2][1:]))

    items = items_directory(url, params)

    if items is None:
        return

    for i in items:

        add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
        clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
        i.update({'cm': [add_to_playlist, clear_playlist], 'action': 'play', 'isFolder': 'False'})

    directory.add(
        items, content='movies', argv=argv
    )

    prevent_failure()


def dash_conditionals(stream):

    try:

        inputstream_adaptive = control.addon_details('inputstream.adaptive').get('enabled')

    except KeyError:

        inputstream_adaptive = False

    m3u8_dash = ('.hls' in stream or '.m3u8' in stream) and control.setting('m3u8_quality_picker') == '2' and not 'greektv.ca' in stream

    dash = ('.mpd' in stream or 'dash' in stream or '.ism' in stream or m3u8_dash) and inputstream_adaptive

    mimetype = None
    manifest_type = None

    if dash:

        if '.hls' in stream or '.m3u8' in stream:
            manifest_type = 'hls'
            mimetype = 'application/vnd.apple.mpegurl'
        elif '.ism' in stream:
            manifest_type = 'ism'
        else:
            manifest_type = 'mpd'

        log_debug('Activating adaptive parameters for this url: ' + stream)

    return dash, m3u8_dash, mimetype, manifest_type


def pseudo_live(url):

    if url.endswith('fifties'):
        url = '{0}movies.php?y=7&l=&g=&p='.format(GM_BASE)
    elif url.endswith('sixties'):
        url = '{0}movies.php?y=6&l=&g=&p='.format(GM_BASE)
    elif url.endswith('seventies'):
        url = '{0}movies.php?y=5&l=&g=&p='.format(GM_BASE)
    elif url.endswith('eighties'):
        url = '{0}movies.php?y=4&l=&g=&p='.format(GM_BASE)
    else:
        url = '{0}movies.php?g=8&y=&l=&p='.format(GM_BASE)

    if 'channel' in url:
        movie_list = list_channel_videos(urlparse(url).path[1:])
    elif 'playlist' in url:
        movie_list = list_playlist_videos(urlparse(url).path[1:])
    else:
        movie_list = gm_indexer().listing(url, get_listing=True)

    if 'youtube' in url:
        movie_list = [i for i in movie_list if i['duration'] >= 240]

    if not url.endswith('kids') and 'youtube' not in url:

        movie_list = [i for i in movie_list if i['url']]

    for i in movie_list:
        i.update({'action': 'play_skipped', 'isFolder': 'False'})

    plot = None

    if control.setting('pseudo_live_mode') == '0':

        choice = random_choice(movie_list)

        meta = {'title': choice['title'], 'image': choice['image']}

        if 'youtube' not in url:
            plot = gm_source_maker(choice['url']).get('plot')

        if plot:
            meta.update({'plot': plot})

        player(choice['url'], meta)

    else:

        shuffle(movie_list)

        directory.add(movie_list, as_playlist=True, auto_play=True)


def player(url, params):

    global skip_directory

    if url is None:
        log_debug('Nothing playable was found')
        return

    if url.startswith('alivegr://'):
        log_debug('Attempting pseudo live playback')
        skip_directory = True
        pseudo_live(url)
        return

    url = url.replace('&amp;', '&')
    skip_directory = params.get('action') == 'play_skipped'

    directory_boolean = MOVIES in url or SHORTFILMS in url or THEATER in url or GK_BASE in url or (
        'episode' in url and GM_BASE in url
    )

    if directory_boolean and control.setting('action_type') == '1' and not skip_directory:
        directory.run_builtin(action='directory', url=url)
        return

    log_debug('Attempting to play this url: ' + url)

    if params.get('action') == 'play_resolved':
        stream = url
    elif params.get('query') and control.setting('check_streams') == 'true':
        sl = json.loads(params.get('query'))
        index = int(control.infoLabel('Container.CurrentItem')) - 1
        stream = check_stream(sl, False, start_from=index, show_pd=True, cycle_list=False)
    else:
        stream = conditionals(url)

    if not stream:

        log_debug('Failed to resolve this url: {0}'.format(url))

        return

    elif control.setting('show_history') == 'true' and not url.startswith('alivegr://'):
        params.update({'isFolder': 'False'})
        add_to_file(PLAYBACK_HISTORY, json.dumps(params))

    try:
        plot = params.get('plot').encode('latin-1')
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        plot = params.get('plot')

    if not plot and 'greek-movies.com' in url:
        plot = gm_source_maker(url).get('plot')

    dash, m3u8_dash, mimetype, manifest_type = dash_conditionals(stream)

    if not m3u8_dash and control.setting('m3u8_quality_picker') == '1' and '.m3u8' in stream:

        try:

            stream = m3u8_picker(stream)

        except TypeError:

            pass

    if stream != url:

        log_debug('Stream has been resolved: ' + stream)

    else:

        log_debug('Attempting direct playback: ' + stream)

    # process headers if necessary:
    if '|' in stream:

        stream, sep, headers = stream.rpartition('|')

        headers = dict(parse_qsl(headers))

        log_debug('Appending custom headers: ' + repr(headers))

        stream = sep.join([stream, urlencode(headers)])

    try:

        image = params.get('image').encode('latin-1')
        title = params.get('title').encode('latin-1')

    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):

        image = params.get('image')
        title = params.get('title')

    meta = {'title': title}

    if plot:

        meta.update({'plot': plot})

    try:

        directory.resolve(stream, meta=meta, icon=image, dash=dash, manifest_type=manifest_type, mimetype=mimetype)

        if url.startswith('iptv://') or 'kineskop.tv' in url:
            control.execute('PlayerControl(RepeatOne)')

    except:

        control.execute('Dialog.Close(all)')
        control.infoDialog(control.lang(30112))
