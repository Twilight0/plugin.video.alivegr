# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import re
import json
from urllib.parse import urlencode
from datetime import datetime
from tulip import directory, kodi
from netclient import Net
from useragents import get_ua
from tulip.utils import py3_dec
from ..modules.utils import thgiliwt, pinned_from_file, get_all_stream_prefs, set_stream_pref, get_stream_pref
from ..modules.themes import iconname
from ..modules.constants import LIVE_GROUPS, cache_method, cache_duration, M3U_LINK, PINNED, ALIVEGR


def stream_priority_key(s):
    u = s.split('|')[0].lower()
    has_drm = 'drm=' in s.lower()
    is_embed = '/embed/' in u or u.endswith('.html') or u.endswith('.htm')
    if is_embed:
        return 99
    # Direct unencrypted HLS (.m3u8)
    if ('.m3u8' in u or '.hls' in u) and not has_drm:
        return 0
    # Direct unencrypted DASH (.mpd)
    if '.mpd' in u and not has_drm:
        return 1
    # Other direct streams
    if not has_drm and ('youtube' in u or 'twitch' in u):
        return 2
    if not has_drm:
        return 3
    # DRM streams
    return 10


def get_live_channel_list(live_group=None):
    """Retrieves processed and preference-applied live channels for a group."""
    live_data, _ = Indexer().live()
    if live_group is None:
        group_setting = kodi.setting('live_group')
    else:
        group_setting = str(live_group)

    try:
        group_idx = int(group_setting) - 1
        group = str(list(LIVE_GROUPS.values())[group_idx])
    except (IndexError, ValueError):
        group = None

    if group_setting not in ('0', '10'):
        live_data = [item for item in live_data if item['group'] == group]
    elif group_setting == '10':
        live_data = [item for item in live_data if item['title'] in pinned_from_file(PINNED)]

    stream_prefs = get_all_stream_prefs()
    for idx, item in enumerate(live_data):
        pref_idx = get_stream_pref(item['title'], stream_prefs)
        item_streams = item.get('streams')
        if item_streams:
            try:
                parsed_s = json.loads(item_streams)
                if pref_idx is not None and isinstance(pref_idx, int) and 0 <= pref_idx < len(parsed_s):
                    preferred_url = parsed_s[pref_idx]
                    item['url'] = preferred_url
                    reordered = [preferred_url] + [s for i, s in enumerate(parsed_s) if i != pref_idx]
                    item['streams'] = json.dumps(reordered)
            except Exception:
                pass

        item_payload = {
            'streams': item.get('streams'),
            'ch_index': idx,
            'title': item.get('title'),
            'live_group': group_setting
        }
        item.update(
            {
                'action': 'play', 'isPlayable': 'True', 'isFolder': 'False', 'duration': None,
                'query': json.dumps(item_payload)
            }
        )
    return live_data


class Indexer:

    def __init__(self):

        pass

    @staticmethod
    def switcher():

        def seq(group):
            kodi.setSetting('live_group', group)
            kodi.idle()
            kodi.sleep(100)

        groups = list(LIVE_GROUPS.values())
        translated = [kodi.i18n(i) for i in groups]
        choice = kodi.selectDialog(heading=kodi.i18n(30049), list=[kodi.i18n(30048)] + translated + [kodi.i18n(30282)])

        if choice != -1:
            seq(str(choice))
            if str(choice) != kodi.setting('live_group'):
                kodi.refresh()
            else:
                kodi.execute('Dialog.Close(all)')

    @cache_method(cache_duration(480))
    def live(self):

        if kodi.setting('debug') == 'false':

            result = Net().http_GET(
                py3_dec(thgiliwt('=' + ALIVEGR))
            ).content

            # result = Net().http_GET('https://pastebin.com/raw/YxxuQEtP').content

            # result = bourtsa(b64decode(result))

        else:

            if kodi.setting('local_remote') == '0':
                local = kodi.setting('live_local')
                with open(local, encoding='utf-8') as _json:
                    result = _json.read()
            elif kodi.setting('local_remote') == '1':
                result = Net().http_GET(kodi.setting('live_remote')).content
            else:
                result = Net().http_GET(py3_dec(thgiliwt('=' + ALIVEGR))).content
                # result = bourtsa(b64decode(result))

        try:
            channels = json.loads(result)
        except json.decoder.JSONDecodeError:
            try:
                channels = json.loads(re.sub(r'(\b\w+)"(\w+\b)', r"\1'\2", result))
            except Exception:
                channels = json.loads(result.replace('\'', '"'))
        # channels = [i for i in channel_list['channels'] if i['enable']]
        updated = channels['updated']
        live_list = []

        year = datetime.now().year

        for channel in channels['channels']:

            title = channel['name']
            image = channel['logo']
            group = channel['group']
            group = LIVE_GROUPS.get(group, 30210)
            website = channel['website']
            info = channel['info']

            # Handle both new 'streams' schema and legacy 'url' schema
            streams_raw = channel.get('streams')
            packed_streams = []

            if streams_raw and isinstance(streams_raw, list):
                for s in streams_raw:
                    if isinstance(s, dict):
                        s_url = s.get('url')
                        if not s_url:
                            continue
                        s_headers = dict(s.get('headers') or {})
                        s_drm = s.get('drm')
                        if s_drm:
                            s_headers['DRM'] = json.dumps(s_drm)
                        if s_headers:
                            packed_streams.append('|'.join([s_url, urlencode(s_headers)]))
                        else:
                            packed_streams.append(s_url)
                    elif isinstance(s, str) and s:
                        packed_streams.append(s)
            else:
                # Legacy schema fallback
                url = channel.get('url', [])
                headers = channel.get('headers')
                if headers == 'random':
                    headers = {'User-Agent': get_ua(), 'Referer': channel.get('website', 'https://www.greektv.live/')}
                drm = channel.get('drm')
                if drm:
                    if not isinstance(headers, dict):
                        headers = {}
                    headers.update({'DRM': json.dumps(drm)})

                for idx, u in enumerate(url):
                    if not u:
                        continue
                    if idx == 0 and headers:
                        packed_streams.append('|'.join([u, urlencode(headers)]))
                    else:
                        packed_streams.append(u)

            if not packed_streams:
                continue

            packed_streams.sort(key=stream_priority_key)

            if len(info) == 5 and info[:5].isdigit():
                info = kodi.i18n(int(info))

            if ' - ' in info:
                if kodi.setting('lang_split') == '0':
                    if 'Greek' in kodi.infoLabel('System.Language'):
                        info = info.partition(' - ')[2]
                    elif 'English' in kodi.infoLabel('System.Language'):
                        info = info.partition(' - ')[0]
                    else:
                        info = info
                elif kodi.setting('lang_split') == '1':
                    info = info.partition(' - ')[0]
                elif kodi.setting('lang_split') == '2':
                    info = info.partition(' - ')[2]
                else:
                    info = info

            data = (
                {
                    'title': title, 'image': image, 'group': str(group),
                    'genre': kodi.i18n(group), 'plot': info, 'website': website, 'year': year,
                    'url': packed_streams[0], 'streams': json.dumps(packed_streams)
                }
            )

            live_list.append(data)

        return live_list, updated

    def live_tv(self, query=None):

        if query is not None:
            live_data = get_live_channel_list('0')
        else:
            live_data = get_live_channel_list()

        _, updated = self.live()

        live_group = int(kodi.setting('live_group')) - 1

        for item in live_data:

            if kodi.setting('live_group') == '10':
                pin_cm = {'title': 30337, 'query': {'action': 'unpin', 'query': item['title']}}
            else:
                pin_cm = {'title': 30336, 'query': {'action': 'pin', 'query': item['title']}}

            menu = [pin_cm]

            # If channel has alternative streams, add "Choose Stream" context menu
            item_streams = item.get('streams')
            if item_streams:
                try:
                    parsed_s = json.loads(item_streams)
                    if len(parsed_s) > 1:
                        stream_cm = {
                            'title': 30064,
                            'query': {
                                'action': 'live_stream_picker',
                                'title': item['title'],
                                'streams': item.get('streams'),
                                'image': item.get('image', ''),
                                'plot': item.get('plot', '')
                            }
                        }
                        menu.append(stream_cm)
                except Exception:
                    pass

            group_changer = {'title': 30034, 'query': {'action': 'live_switcher'}}

            if kodi.setting('live_switcher_mode') == '1':
                menu.insert(1, group_changer)

            item.update({'cm': menu})

        if kodi.setting('live_switcher_mode') == '0':

            if kodi.setting('live_group') == '0':
                label = kodi.i18n(30048)
            elif kodi.setting('live_group') == '10':
                label = kodi.i18n(30282)
            else:
                group = int(list(LIVE_GROUPS.values())[live_group])
                label = kodi.i18n(group)

            switch = {
                'title': label,
                'image': iconname('switcher'),
                'action': 'live_switcher',
                'plot': kodi.i18n(30034) + '[CR]' + kodi.i18n(30035) + updated,
                'isFolder': 'False', 'isPlayable': 'False'
            }

            live_data.insert(0, switch)

        if query:

            queried_list = [i for i in live_data if query in i['title'].lower()]

            return queried_list

        kodi.setsortmethod()
        kodi.setsortmethod('production_code')
        kodi.setsortmethod('title')
        kodi.setsortmethod('genre', mask='%C')

        directory.builder(live_data, content='videos', add_all_at_once=True)

    @cache_method(cache_duration(480))
    def cached_live_m3u(self):

        result = Net().http_GET(
            M3U_LINK, headers={'User-Agent': 'AliveGR, version: ' + kodi.version()}
        ).content

        items = re.findall(r'#EXTINF:.+?\n.+?$', result, re.M)

        m3u_list = []

        for item in items:

            title = re.search(r',(.+)', item).group(1)
            try:
                image = re.search(r'tvg-logo="(.+)"', item).group(1)
            except AttributeError:
                image = kodi.addonInfo('icon')
            url = re.search(r'\n(.+)', item).group(1)

            data = {'title': title, 'image': image, 'url': url}

            m3u_list.append(data)

        return m3u_list

    def live_m3u(self):

        m3u_list = self.cached_live_m3u()

        for i in m3u_list:
            i.update({'action': 'play', 'isFolder': 'False', 'isPlayable': 'True'})

        directory.builder(m3u_list, content='videos', as_playlist=kodi.setting('live_tv_mode') == '1')

    def modular(self, group):

        if group == '30125':
            fanart = 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
        elif group == '30032':
            fanart = 'https://cdn.iview.abc.net.au/thumbs/i/ls/LS1604H001S005786f5937ded19.22034349_1280.jpg'
        else:
            fanart = kodi.addonInfo('fanart')

        channel_list, _ = self.live()
        modular_list = [item for item in channel_list if item['group'] == group]

        year = datetime.now().year
        stream_prefs = get_all_stream_prefs()

        modular_list.sort(key=lambda k: k['title'].lower())

        for idx, item in enumerate(modular_list):
            # Apply stream preference if saved
            pref_idx = get_stream_pref(item['title'], stream_prefs)
            item_streams = item.get('streams')
            if item_streams:
                try:
                    parsed_s = json.loads(item_streams)
                    if pref_idx is not None and isinstance(pref_idx, int) and 0 <= pref_idx < len(parsed_s):
                        preferred_url = parsed_s[pref_idx]
                        item['url'] = preferred_url
                        reordered = [preferred_url] + [s for i, s in enumerate(parsed_s) if i != pref_idx]
                        item['streams'] = json.dumps(reordered)
                except Exception:
                    pass

            pin_cm = {'title': 30336, 'query': {'action': 'pin'}}
            menu = [pin_cm]

            # If channel has alternative streams, add "Choose Stream" context menu
            if item_streams:
                try:
                    parsed_s = json.loads(item_streams)
                    if len(parsed_s) > 1:
                        stream_cm = {
                            'title': 30064,
                            'query': {
                                'action': 'live_stream_picker',
                                'title': item['title'],
                                'streams': item.get('streams'),
                                'image': item.get('image', ''),
                                'plot': item.get('plot', '')
                            }
                        }
                        menu.append(stream_cm)
                except Exception:
                    pass

            item_payload = {
                'streams': item.get('streams'),
                'ch_index': idx,
                'title': item.get('title'),
                'modular_group': group
            }
            item.update(
                {'action': 'play', 'isFolder': 'False', 'isPlayable': 'True',
                 'cm': menu, 'year': year, 'duration': None, 'fanart': fanart,
                 'query': json.dumps(item_payload)
                 }
            )

        directory.builder(modular_list, content='videos')

    @staticmethod
    def live_stream_picker(params):
        """Displays a dialog allowing the user to select and store a stream preference for a channel."""
        raw_streams = params.get('streams')
        title = params.get('title', '')
        if not raw_streams:
            return

        try:
            streams_list = json.loads(raw_streams)
        except Exception:
            return

        if not streams_list or len(streams_list) <= 1:
            return

        current_pref = get_all_stream_prefs().get(title, 0)
        if not isinstance(current_pref, int) or not (0 <= current_pref < len(streams_list)):
            current_pref = 0

        labels = []
        for idx, s in enumerate(streams_list, start=1):
            url_part = s.split('|')[0]
            # Build friendly label
            if '.mpd' in url_part:
                tag = 'DASH MPD'
            elif '.m3u8' in url_part:
                tag = 'HLS m3u8'
            elif 'youtube' in url_part or 'youtu.be' in url_part:
                tag = 'YouTube'
            elif 'kick.com' in url_part:
                tag = 'Kick'
            elif 'twitch.tv' in url_part:
                tag = 'Twitch'
            else:
                tag = 'Direct'

            if '|' in s and 'DRM' in s:
                tag += ' (DRM)'

            domain = url_part.split('//')[-1].split('/')[0]
            is_selected = (idx - 1) == current_pref
            text = f"#{idx}: {tag} [{domain}]"
            if is_selected:
                labels.append(f"[B]* {text}[/B]")
            else:
                labels.append(text)

        choice = kodi.selectDialog(heading=f"{kodi.i18n(30064)} - {title}", list=labels, preselect=current_pref)
        if choice == -1:
            return

        # Store stream choice persistently
        set_stream_pref(title, choice)

        # Subtle feedback to user
        clean_label = labels[choice].replace('[B]', '').replace('[/B]', '').lstrip('* ')
        msg = f"{title}: #{choice + 1} ({clean_label})"
        kodi.infoDialog(msg, heading=kodi.i18n(30064), time=2000)

        # Refresh directory listing to apply new primary URL immediately
        kodi.refresh()
