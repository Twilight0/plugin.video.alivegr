# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import re
import youtube_resolver
from ..modules.constants import YT_URL, cache_function, cache_duration
from tulip import kodi
from netclient import Net
from ..modules.utils import stream_picker


@cache_function(cache_duration(360))
def generic(url, add_base=False):

    html = Net().http_GET(url).content

    try:
        video_id = re.search(r'videoId.+?([\w-]{11})', html).group(1)
    except AttributeError:
        return

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
