# -*- coding: utf-8 -*-
import json
# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import re
from urllib.parse import urlparse
# noinspection PyUnresolvedReferences
import youtube_resolver
from ..modules.constants import YT_URL, YT_API, cache_function, cache_duration
from tulip import kodi
from netclient import Net
from useragents import get_ua
from ..modules.utils import stream_picker


@cache_function(cache_duration(360))
def generic(url, add_base=False):

    html = Net().http_GET(
        url, headers={'User-Agent': get_ua(), "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+"}
    ).content

    # try:

    api_key = re.search(r'innertubeApiKey": "(\w+?)"', html).group(1)
    version = re.search(r'''innertubeContextClientVersion": "([\d.]+?)"''', html).group(1)

    payload = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": version
            }
        },
        "browseId": [p for p in urlparse(url).path.split('/') if p not in ['', 'live']][0]
    }

    res = Net().http_POST(YT_API.format(api_key), form_data=payload, headers={'User-Agent': get_ua()}).content
    data = json.loads(res)

    video_id = data.get('videoRenderer').get('videoId')

    # except:
    #     return

    if not add_base:

        return video_id

    else:

        stream = YT_URL + video_id
        return stream


def wrapper(url):

    if url.endswith('/live'):

        url = generic(url)

        if not url:

            return

    streams = youtube_resolver.resolve(url)

    try:
        addon_enabled = kodi.addon_details('inputstream.adaptive').get('enabled')
    except KeyError:
        addon_enabled = False

    if not addon_enabled:

        streams = [s for s in streams if 'dash' not in s['title'].lower()]

    if kodi.condVisibility('Window.IsVisible(music)') and kodi.setting('audio_only') == 'true':

        audio_choices = [u for u in streams if 'dash/audio' in u and 'dash/video' not in u]

        if kodi.setting('yt_quality_picker') == '0':
            resolved = audio_choices[0]['url']
        else:
            qualities = [i['title'] for i in audio_choices]
            urls = [i['url'] for i in audio_choices]

            links = list(zip(qualities, urls))

            resolved = stream_picker(links)

        return resolved

    elif kodi.setting('yt_quality_picker') == '1':

        qualities = [i['title'] for i in streams]
        urls = [i['url'] for i in streams]

        links = list(zip(qualities, urls))
        resolved = stream_picker(links)

        return resolved

    else:

        resolved = streams[0]['url']

        return resolved
