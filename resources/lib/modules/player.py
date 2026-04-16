# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import json

from xbmcaddon import Addon
from collections import deque
from random import shuffle, choice as random_choice
from resolveurl import add_plugin_dirs, resolve as resolve_url
from resolveurl.hmf import HostedMediaFile
from resolveurl.resolver import ResolverError
# noinspection PyUnresolvedReferences
from youtube_plugin.youtube.youtube_exceptions import YouTubeException
from tulip import directory, kodi
from tulip.log import log
from netclient import Net
from urllib.parse import urljoin, parse_qsl, urlencode
from urllib.error import HTTPError
from tulip.utils import percent
from tulip.cleantitle import stripTags
from itertags import iwrapper

from ..indexers.vod import GM_MOVIES, GM_SHORTFILMS, GM_THEATER, GM_BASE
from .source_makers import gm_source_maker
from ..resolvers import youtube
from .constants import YT_URL, SEPARATOR, PLUGINS_PATH, cache_function, cache_duration, PLAYBACK_HISTORY
from .utils import add_to_file


def conditionals(url):

    add_plugin_dirs(kodi.transPath(PLUGINS_PATH))

    def yt(uri):

        if uri.startswith('plugin://'):
            return uri

        if len(uri) == 11:

            uri = YT_URL + uri

        try:
            return youtube.wrapper(uri)
        except YouTubeException as exp:
            log('Youtube resolver failure, reason: ' + repr(exp))
            return

    if not url:
        kodi.close_all()
        return

    if 'youtu' in url or len(url) == 11:

        log('Resolving with youtube addon...')

        return yt(url)

    elif HostedMediaFile(url).valid_url():

        try:
            stream = resolve_url(url)
            log('Resolving with Resolveurl...')
        except ResolverError:
            return None
        except HTTPError:
            return url

        return stream

    elif GM_BASE in url:

        sources = gm_source_maker(url)
        stream = stream_picker(sources['links'])

        return conditionals(stream)

    else:

        log('Passing direct link...')

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
            pd = kodi.progressDialog
            pd.create(kodi.name(), ''.join([kodi.i18n(30459), h.partition(': ')[2]]))

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
            kodi.infoDialog(kodi.i18n(30411))
            if show_pd:
                pd.close()
        elif resolved is None:
            if cycle_list:
                log('Removing unplayable stream: {0}'.format(stream))
                stream_list.remove((h, stream))
                return check_stream(stream_list)
            else:
                if show_pd:
                    _percent = percent(c, len(stream_list[start_from:]))
                    pd.update(_percent, ''.join([kodi.i18n(30459), h.partition(': ')[2]]))
                kodi.sleep(1000)
                continue


def stream_picker(links):

    if len(links) == 1:

        stream = links[0][1]

        return stream

    elif Addon().getSetting('action_type') == '2':

        try:
            if Addon().getSetting('check_streams') == 'false':
                stream = random_choice([link[1] for link in links])
            else:
                stream = check_stream(links)
        except Exception:
            return

        return stream

    else:

        choice = kodi.selectDialog(heading=kodi.i18n(30064), list=[link[0] for link in links])

        if choice == -1:
            return
        elif Addon().getSetting('check_streams') == 'false':
            return [link[1] for link in links][choice]
        else:
            return check_stream(links, False, start_from=choice, show_pd=True, cycle_list=False)


@cache_function(cache_duration(660))
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
            description = kodi.i18n(30085)

    try:
        genre = sources['genre']
    except KeyError:
        genre = kodi.i18n(30147)

    for h, l in lists:

        html = Net().http_GET(l).content
        button = iwrapper(html, 'a', attrs={'role': 'button'}, ret='href').__next__()
        image = iwrapper(html, 'img', attrs={'class': 'thumbnail img-responsive'}, ret='src').__next__()
        image = urljoin(GM_BASE, image)
        title = iwrapper(html, 'h3').__next__().text
        try:
            year = [y.text[-4:] for y in iwrapper(html, 'h4') if str(y.text[-4:]).isdigit()][0]
        except IndexError:
            year = [y.text[-2:] for y in iwrapper(html, 'h4') if str(y.text[-2:]).isdigit()][0]
            numeric_year = int(year)
            if numeric_year < 100:
                if numeric_year >= 40:
                    numeric_year += 1900
                else:
                    numeric_year += 2000
            year = str(numeric_year)
        try:
            episode = stripTags(deque(iwrapper(html, 'h4'), maxlen=1).pop().text)
            if episode[-4:].isdigit():
                raise IndexError
            episode = episode.partition(': ')[2].strip()
            label = title + ' - ' + episode + SEPARATOR + h
            title = title + ' - ' + episode
        except IndexError:
            label = title + SEPARATOR + h
        # plot = title + '[CR]' + kodi.i18n(30090) + ': ' + year + '[CR]' + description

        # if is_py2:
        #     title = title + ' ({})'.format(year)

        data = {
            'label': label, 'title': title, 'url': button, 'image': image, 'plot': description,
            'year': int(year), 'genre': genre, 'name': title
        }

        if Addon().getSetting('check_streams') == 'true':
            data.update({'query': json.dumps(sources['links'])})

        items.append(data)

    return items


def directory_picker(url, argv):

    params = dict(parse_qsl(argv[2][1:]))

    items = gm_directory(url, params)

    if items is None:
        return

    for i in items:

        add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
        clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
        i.update({'cm': [add_to_playlist, clear_playlist], 'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})

    directory.builder(
        items, content='movies', argv=argv
    )


def dash_conditionals(stream):

    try:

        inputstream_adaptive = kodi.addon_details('inputstream.adaptive').get('enabled')

    except KeyError:

        inputstream_adaptive = False

    m3u8_dash = ('.hls' in stream or '.m3u8' in stream) and Addon().getSetting('m3u8_quality_picker') == '1'

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

        log('Activating adaptive parameters for this url: ' + stream)

    return dash, m3u8_dash, mimetype, manifest_type


def player(url, params):

    if url is None:
        log('Nothing playable was found')
        return

    url = url.replace('&amp;', '&')

    directory_boolean = GM_MOVIES in url or GM_SHORTFILMS in url or GM_THEATER in url or (
        'episode' in url and GM_BASE in url
    )

    if directory_boolean and Addon().getSetting('action_type') == '1':
        directory.run_builtin(action='directory', url=url)
        return

    log('Attempting to play this url: ' + url)

    if params.get('query') and Addon().getSetting('check_streams') == 'true':
        sl = json.loads(params.get('query'))
        index = int(kodi.infoLabel('Container.CurrentItem')) - 1
        stream = check_stream(sl, False, start_from=index, show_pd=True, cycle_list=False)
    else:
        stream = conditionals(url)

    if not stream:

        log('Failed to resolve this url: {0}'.format(url))

        return

    elif Addon().getSetting('show_history') == 'true':
        params.update({'isFolder': 'False'})
        add_to_file(PLAYBACK_HISTORY, json.dumps(params))

    try:
        plot = params.get('plot').encode('latin-1')
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        plot = params.get('plot')

    if not plot and 'greek-movies.com' in url:
        plot = gm_source_maker(url).get('plot')

    dash, m3u8_dash, mimetype, manifest_type = dash_conditionals(stream)

    # if not m3u8_dash and kodi.setting('m3u8_quality_picker') == '1' and '.m3u8' in stream:
    #
    #     try:
    #
    #         stream = m3u8_picker(stream)
    #
    #     except TypeError:
    #
    #         pass

    if stream != url:

        log('Stream has been resolved: ' + stream)

    else:

        log('Attempting direct playback: ' + stream)

    licence_type = None
    licence_key = None

    # process headers if necessary:
    if '|' in stream:

        stream, sep, headers = stream.rpartition('|')

        headers = dict(parse_qsl(headers))

        if 'DRM' in headers:
            drm = headers.pop('DRM')
            licence_type = drm[0]
            licence_key = json.dumps(drm[1])

        log('Appending custom headers: ' + repr(headers))

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

        directory.resolve(
            stream, meta=meta, icon=image, dash=dash, manifest_type=manifest_type, mimetype=mimetype,
            licence_type=licence_type, licence_key=licence_key
        )

    except:

        kodi.execute('Dialog.Close(all)')
        kodi.infoDialog(kodi.i18n(30112))
