# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import inspect
import json
import re

from xbmcaddon import Addon
from collections import deque
from random import shuffle
from resolveurl import add_plugin_dirs, resolve as resolve_url
from resolveurl.hmf import HostedMediaFile
from resolveurl.resolver import ResolverError
from tulip import directory, kodi
from tulip.log import log
from netclient import Net
from useragents import FALLBACK_USER_AGENTS
from urllib.parse import urljoin, parse_qsl, urlencode
from urllib.error import HTTPError
from tulip.utils import percent
from tulip.cleantitle import stripTags
from itertags import iwrapper

from ..indexers.vod import GM_MOVIES, GM_SHORTFILMS, GM_THEATER, GM_BASE
from .source_makers import gm_source_maker
from .constants import (
    YT_URL, SEPARATOR, PLUGINS_PATH, cache_function, cache_duration, PLAYBACK_HISTORY
)
from .utils import add_to_file


def conditionals(url, params=None):

    add_plugin_dirs(kodi.transPath(PLUGINS_PATH))

    if not url:
        kodi.close_all()
        return

    elif HostedMediaFile(url).valid_url():

        hmf = HostedMediaFile(url)
        is_audio = Addon().getSetting('audio_only') == 'true' and (
            kodi.condVisibility('Window.IsVisible(music)') or
            (bool(params) and any(
                params.get(k) for k in ('album', 'artist', 'tracknumber', 'audio', 'audio_only')
            )) or
            (bool(params) and (
                params.get('content') in ('songs', 'music') or
                params.get('infotype') in ('music', 'song')
            ))
        )
        stream = None
        if is_audio:
            try:
                resolvers = hmf.get_resolvers(validated=True)
                if resolvers:
                    resolver = resolvers[0]
                    if hasattr(resolver, 'get_media_url'):
                        spec = inspect.getfullargspec(resolver.get_media_url)
                        if 'audio_only' in (spec.args or []) or 'audio_only' in (spec.kwonlyargs or []):
                            host, media_id = resolver.get_host_and_id(url)
                            log(f'Resolving audio-only with {getattr(resolver, "name", "resolver")}...')
                            res = resolver.get_media_url(host, media_id, audio_only=True)
                            if isinstance(res, (tuple, list)):
                                res = res[0]
                            if res and res.startswith('//'):
                                res = 'http:' + res
                            stream = res
            except Exception as e:
                log(f'Audio-only resolution failed: {e}')
                stream = None

        if not stream:
            try:
                stream = hmf.resolve()
                log('Resolving with Resolveurl...')
            except ResolverError:
                return None
            except HTTPError:
                return url

        return stream

    elif GM_BASE in url:

        gm_sources = gm_source_maker(url)

        links = gm_sources.get('links', [])
        if not links:
            kodi.close_all()
            return None

        stream = stream_picker(links)
        if not stream:
            kodi.close_all()
            return None

        return conditionals(stream, params)

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
        # kodi.infoDialog(links[0][0])

        return stream

    else:

        choice = kodi.selectDialog(heading=kodi.i18n(30064), list=[link[0] for link in links])

        if choice == -1:
            return
        elif Addon().getSetting('check_streams') == 'false':
            return [link[1] for link in links][choice]
        else:
            return check_stream(links, False, start_from=choice, show_pd=True, cycle_list=False)


def gm_directory(url, params):

    sources = gm_source_maker(url)

    links = sources['links']

    items = []

    title = sources.get('title') or params.get('title') or params.get('name') or ''
    image = params.get('image') or sources.get('image') or ''
    if image:
        image = urljoin(GM_BASE, image)
    description = sources.get('plot') or params.get('plot') or kodi.i18n(30085)

    genre = sources.get('genre') or [kodi.i18n(30089)]
    if not isinstance(genre, list):
        genre = [genre]

    year_val = params.get('year') or sources.get('year') or 0
    try:
        year = int(year_val)
    except (ValueError, TypeError):
        year = 0

    for h, l in links:

        label = title + SEPARATOR + h if title else h

        data = {
            'label': label, 'title': title, 'url': l, 'image': image, 'plot': description,
            'year': year, 'genre': genre, 'name': title
        }

        items.append(data)

    return items


def directory_picker(url, argv):

    params = dict(parse_qsl(argv[2][1:]))
    sources = gm_source_maker(url)
    items = gm_directory(url, params)

    if items is None:
        return

    for i in items:

        add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
        clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
        i.update({'cm': [add_to_playlist, clear_playlist], 'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})

        if Addon().getSetting('check_streams') == 'true':
            i.update({'query': json.dumps(sources['links'])})

    directory.builder(
        items, content='movies', argv=argv
    )


def dash_conditionals(stream):
    try:

        inputstream_adaptive = kodi.addon_details('inputstream.adaptive').get('enabled')

    except KeyError:

        inputstream_adaptive = False

    m3u8_dash = ('.hls' in stream or '.m3u8' in stream)

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


def is_stream_available(stream_url):
    """
    Robust pre-flight stream tester.
    Validates that:
    1. The stream URL is accessible and does not return 4xx/5xx HTTP errors.
    2. The response is an actual media stream/manifest and NOT an HTML webpage (e.g. embed or error page).
    3. For HLS (.m3u8), verifies the presence of valid M3U headers (#EXTM3U / #EXT).
    4. For DASH (.mpd), verifies the XML structure (<MPD).
    5. If ClearKey DRM is specified, verifies that the MPD manifest actually advertises ClearKey support.
    """
    if not stream_url:
        return False

    if stream_url.startswith('plugin://') or stream_url.startswith('rtmp'):
        return True

    test_url = stream_url.split('|')[0]
    if not test_url.startswith('http'):
        return True

    if 'googlevideo.com' in test_url or '127.0.0.1' in test_url or 'localhost' in test_url:
        return True

    # Immediate rejection for known non-media embed/html web paths
    if '/embed/' in test_url or test_url.endswith('.html') or test_url.endswith('.htm'):
        log(f'Tester rejected web page / embed URL: {test_url}')
        return False

    headers = {
        'User-Agent': FALLBACK_USER_AGENTS[0],
        'Range': 'bytes=0-4096'
    }
    raw_drm = None
    if '|' in stream_url:
        try:
            raw_h = stream_url.split('|')[1]
            for k, v in parse_qsl(raw_h):
                if k == 'DRM':
                    raw_drm = v
                else:
                    headers[k] = v
        except Exception:
            pass

    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    try:
        req = Request(test_url, headers=headers)
        with urlopen(req, timeout=2.5) as resp:
            status = getattr(resp, 'status', 200)
            if status not in (200, 206):
                log(f'Tester rejected HTTP status {status} for {test_url}')
                return False

            ct = resp.headers.get('Content-Type', '').lower()
            if 'text/html' in ct:
                log(f'Tester rejected text/html Content-Type for {test_url}')
                return False

            chunk = resp.read(4096).decode('utf-8', errors='ignore').strip()

            if chunk.startswith('<!DOCTYPE') or '<html' in chunk.lower():
                log(f'Tester rejected HTML document payload for {test_url}')
                return False

            # HLS validation
            if '.m3u8' in test_url or 'mpegurl' in ct:
                if not chunk.startswith('#EXTM3U') and '#EXT' not in chunk:
                    log(f'Tester rejected invalid HLS playlist header for {test_url}')
                    return False

            # DASH MPD validation
            if '.mpd' in test_url or 'dash+xml' in ct:
                c_lower = chunk.lower()
                if '<mpd' not in c_lower:
                    log(f'Tester rejected invalid MPD XML for {test_url}')
                    return False
                # If ClearKey DRM is specified, check that manifest actually advertises ClearKey or CENC
                if raw_drm and 'clearkey' in raw_drm.lower():
                    # ClearKey SystemID: 1077efec-c0b2-4d02-ace3-3c1e52e2fb4b, or MPEG-CENC
                    if '1077efec' not in c_lower and 'clearkey' not in c_lower and 'mp4protection:2011' not in c_lower:
                        log(f'Tester rejected MPD: ClearKey/CENC not supported in manifest for {test_url}')
                        return False

            return True

    except HTTPError as e:
        log(f'Tester rejected HTTP {e.code} for {test_url}')
        return False
    except Exception as e:
        log(f'Tester rejected with exception {e} for {test_url}')
        return False


def handle_channel_failure(params, query_data):
    """
    Handles playback failure for live channels by automatically jumping to the next channel in the
    container/playlist, with a loop guard of 5 max attempts.
    """
    if Addon().getSetting('auto_channel_jump') == 'false':
        return

    # Only apply auto-jump to live channels
    is_live = False
    if isinstance(query_data, dict):
        if any(k in query_data for k in ('ch_index', 'live_group', 'modular_group', 'streams')):
            is_live = True
    elif params.get('streams'):
        is_live = True

    if not is_live:
        return

    import xbmcgui
    win = xbmcgui.Window(10000)
    try:
        fail_count = int(win.getProperty('alivegr_fail_count') or '0')
    except (ValueError, TypeError):
        fail_count = 0

    if fail_count >= 5:
        win.setProperty('alivegr_fail_count', '0')
        kodi.infoDialog('Multiple channels failed. Stopped auto-jump.', heading=kodi.name(), time=4000)
        return

    win.setProperty('alivegr_fail_count', str(fail_count + 1))

    # Check playlist mode
    try:
        import xbmc
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        if playlist.size() > 1:
            log('Auto-jump: In playlist mode, advancing to next playlist item')
            kodi.player().playnext()
            return
    except Exception:
        pass

    # Method 1: Check Kodi Container for the next list item
    next_url = kodi.infoLabel('Container.ListItem(1).FileNameAndPath')
    next_title = kodi.infoLabel('Container.ListItem(1).Title')

    if next_url and 'plugin.video.alivegr' in next_url and 'action=play' in next_url:
        curr_title = params.get('title') or 'Channel'
        log(f'Auto-jump: Advancing via Container to next item: {next_title} ({next_url})')
        kodi.infoDialog(
            f"{curr_title} unavailable. Trying {next_title}...",
            heading=kodi.name(),
            time=2500
        )
        kodi.execute('Action(Down)')
        kodi.sleep(200)
        kodi.execute(f'PlayMedia({next_url})')
        return

    # Method 2: If Container item not available, look up from live channel list
    if isinstance(query_data, dict):
        ch_index = query_data.get('ch_index')
        live_group = query_data.get('live_group')
        modular_group = query_data.get('modular_group')

        try:
            from ..indexers.live import get_live_channel_list, Indexer as LiveIndexer
            if modular_group:
                ch_list, _ = LiveIndexer().live()
                ch_list = [item for item in ch_list if item['group'] == modular_group]
                ch_list.sort(key=lambda k: k['title'].lower())
            else:
                ch_list = get_live_channel_list(live_group)

            if ch_index is not None and isinstance(ch_index, int) and (ch_index + 1) < len(ch_list):
                next_item = ch_list[ch_index + 1]
                next_title = next_item.get('title', 'Next Channel')
                curr_title = params.get('title') or 'Channel'
                log(f'Auto-jump: Advancing via channel list to index {ch_index + 1}: {next_title}')
                kodi.infoDialog(
                    f"{curr_title} unavailable. Trying {next_title}...",
                    heading=kodi.name(),
                    time=2500
                )
                from tulip.init import sysaddon
                from urllib.parse import quote_plus
                next_url_val = next_item.get('url', '')
                next_query = next_item.get('query', '')
                next_image = next_item.get('image', '')
                parts = [
                    f'{sysaddon}?action=play',
                    f'url={quote_plus(next_url_val)}',
                    f'title={quote_plus(next_title)}',
                    f'image={quote_plus(next_image)}' if next_image else None,
                    f'query={quote_plus(next_query)}' if next_query else None
                ]
                play_uri = '&'.join([p for p in parts if p])
                kodi.execute(f'PlayMedia({play_uri})')
                return
        except Exception as e:
            log(f'Auto-jump channel list fallback error: {e}')


def player(url, params):

    if url is None:
        log('Nothing playable was found')
        return

    url = url.replace('&amp;', '&')

    directory_boolean = any(
        [
            GM_MOVIES in url, GM_SHORTFILMS in url, GM_THEATER in url,
            ('episode' in url and GM_BASE in url)
        ]
    )

    if directory_boolean and Addon().getSetting('action_type') == '1':
        directory.run_builtin(
            action='directory', url=url, title=params.get('title'),
            image=params.get('image'), plot=params.get('plot'),
            year=params.get('year'), name=params.get('name')
        )
        return

    log('Attempting to play this url: ' + url)

    query_param = params.get('query')
    query_data = None
    if query_param:
        try:
            query_data = json.loads(query_param)
        except Exception:
            query_data = None

    candidate_streams = None
    if isinstance(query_data, dict):
        raw_s = query_data.get('streams')
        if raw_s:
            try:
                candidate_streams = json.loads(raw_s) if isinstance(raw_s, str) else raw_s
            except Exception:
                candidate_streams = None
    elif params.get('streams'):
        try:
            raw_s = params.get('streams')
            candidate_streams = json.loads(raw_s) if isinstance(raw_s, str) else raw_s
        except Exception:
            candidate_streams = None

    if isinstance(query_data, list) and Addon().getSetting('check_streams') == 'true':
        sl = query_data
        index = int(kodi.infoLabel('Container.CurrentItem')) - 1
        stream = check_stream(sl, False, start_from=index, show_pd=True, cycle_list=False)
    else:
        stream = conditionals(url, params)
        if stream and not is_stream_available(stream):
            log(f'Primary stream unavailable: {stream}')
            stream = None

        # Fallback to secondary streams if initial stream fails and fallback is enabled (defaults to true)
        allow_fallback = Addon().getSetting('live_stream_fallback') != 'false'
        if not stream and allow_fallback and candidate_streams and isinstance(candidate_streams, list) and len(candidate_streams) > 1:
            def stream_reliability_key(s_entry):
                u = s_entry.split('|')[0].lower()
                # Direct unencrypted HLS is #1 priority
                if ('.m3u8' in u or '.hls' in u) and 'DRM' not in s_entry:
                    return 0
                # YouTube / Twitch streams are #2
                if 'youtube' in u or 'youtu.be' in u or 'twitch' in u:
                    return 1
                # Direct unencrypted DASH
                if '.mpd' in u and 'DRM' not in s_entry:
                    return 2
                # DRM streams
                if 'DRM' in s_entry:
                    return 3
                return 4

            remaining = [s for s in candidate_streams if s != url]
            remaining.sort(key=stream_reliability_key)

            for alt_idx, alt_url in enumerate(remaining, start=1):
                log(f'Attempting fallback stream #{alt_idx}: {alt_url}')
                kodi.infoDialog(
                    f"Testing stream source #{alt_idx}...",
                    heading=params.get('title') or kodi.name(),
                    time=1200
                )
                cand_resolved = conditionals(alt_url, params)
                if cand_resolved and is_stream_available(cand_resolved):
                    stream = cand_resolved
                    url = alt_url
                    log(f'Fallback to stream #{alt_idx} succeeded: {stream}')
                    break

    if not stream:

        log('Failed to resolve this url: {0}'.format(url))

        kodi.execute('Dialog.Close(all)')
        try:
            from tulip.init import syshandle
            kodi.resolve(syshandle, False, kodi.item())
        except Exception:
            pass

        handle_channel_failure(params, query_data)

        return

    elif Addon().getSetting('show_history') == 'true':
        params.update({'isFolder': 'False'})
        add_to_file(PLAYBACK_HISTORY, json.dumps(params))

    try:
        plot = params.get('plot').encode('latin-1')
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        plot = params.get('plot')

    if not plot and 'greek-movies.com' in url and 'view' not in url:
        plot = gm_source_maker(url).get('plot')

    dash, m3u8_dash, mimetype, manifest_type = dash_conditionals(stream)

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
            raw_drm = headers.pop('DRM')
            try:
                drm = json.loads(raw_drm) if isinstance(raw_drm, str) else raw_drm
                licence_type = drm[0]
                licence_key = json.dumps(drm[1]) if not isinstance(drm[1], str) else drm[1]
            except Exception as e:
                log(f'Failed to parse DRM parameter: {e}')

        log('Appending custom headers: ' + repr(headers))

        stream = sep.join([stream, urlencode(headers)])

    image = params.get('image', '')
    name = params.get('name')
    title = params.get('title', '')

    if name:
        meta = {'title': name}
    else:
        meta = {'title': title}

    if plot:
        meta.update({'plot': plot})

    try:

        directory.resolve(
            stream, meta=meta, icon=image, dash=dash, manifest_type=manifest_type, mimetype=mimetype,
            licence_type=licence_type, licence_key=licence_key
        )

        try:
            import xbmcgui
            win = xbmcgui.Window(10000)
            win.setProperty('alivegr_fail_count', '0')
            win.setProperty('alivegr_playing_title', title)
        except Exception:
            pass

    except Exception as e:

        log(f'Playback error: {e}')
        kodi.execute('Dialog.Close(all)')
        kodi.infoDialog(kodi.i18n(30112))
        try:
            from tulip.init import syshandle
            kodi.resolve(syshandle, False, kodi.item())
        except Exception:
            pass
        handle_channel_failure(params, query_data)
