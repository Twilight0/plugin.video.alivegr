# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from xbmcaddon import Addon
from collections import OrderedDict
from urllib.parse import urljoin
from tulip.kodi import dataPath, join, cacheDirectory
from pickled import FunctionCache

cache_function = FunctionCache(cacheDirectory).cache_function
cache_method = FunctionCache(cacheDirectory).cache_method

########################################################################################################################

ART_ID = 'resource.images.alivegr.artwork'
LOGOS_ID = 'resource.images.alivegr.logos'
PLUGINS_ID = 'script.module.resolveurl.pluginsgr'
PLUGINS_PATH = 'special://home/addons/{0}/resources/plugins/'.format(PLUGINS_ID)
YT_ADDON_ID = 'plugin.video.youtube'
YT_ADDON = 'plugin://{0}'.format(YT_ADDON_ID)
YT_URL = 'https://www.youtube.com/watch?v='
YT_API = 'https://www.youtube.com/youtubei/v1/browse?key={}'
YT_PREFIX = YT_ADDON + '/play/?video_id='
PLAY_ACTION = '?action=play&url='

########################################################################################################################

WEBSITE = 'https://www.alivegr.net'
FACEBOOK = 'https://www.facebook.com/alivegr/'
TWITTER = 'https://x.com/TwilightZer0'
PAYPAL = 'https://www.paypal.me/AliveGR'
PATREON = 'https://www.patreon.com/twilight0'
SUPPORT = 'https://github.com/Twilight0/plugin.video.alivegr/issues'
FORUM = 'https://github.com/Twilight0/plugin.video.alivegr/discussions'

########################################################################################################################

M3U_LINK = 'https://raw.githubusercontent.com/komhsgr/m3u/refs/heads/main/Greekstreamtv.m3u'

########################################################################################################################

GM_BASE = 'https://greek-movies.com/'
GM_MOVIES = urljoin(GM_BASE, 'movies.php')
GM_SHOWS = urljoin(GM_BASE, 'shows.php')
GM_SERIES = urljoin(GM_BASE, 'series.php')
GM_ANIMATION = urljoin(GM_BASE, 'animation.php')
GM_THEATER = urljoin(GM_BASE, 'theater.php')
GM_SPORTS = urljoin(GM_BASE, 'sports.php')
GM_SHORTFILMS = urljoin(GM_BASE, 'shortfilm.php')
GM_MUSIC = urljoin(GM_BASE, 'music.php')
GM_SEARCH = urljoin(GM_BASE, 'search.php')
GM_PERSON = urljoin(GM_BASE, 'person.php')
GM_EPISODE = urljoin(GM_BASE, 'ajax.php?type=episode&epid={0}&view={1}')

########################################################################################################################

GF_BASE = 'https://greekfun.net'
GF_SEARCH = urljoin(GF_BASE,'/?ajax=search&q={}')
GF_EPISODES = urljoin(GF_BASE,'/?ajax=episodes&id=72')

########################################################################################################################

LIVE_GROUPS = OrderedDict(
    [
        ('Panhellenic', 30201), ('Pancypriot', 30202), ('International', 30203), ('Regional', 30207),
        ('Music', 30125), ('Cinema', 30205), ('Kids', 30032), ('Sports', 30094), ('Web TV', 30210)
    ]
)

QUERY_MAP = OrderedDict(
            [
                ('Live TV Channel', 30113), ('Movie', 30130), ('TV Serie', 30305), ('TV Show', 30133),
                ('Theater', 30068), ('Cartoon', 30097), ('Person', 30101)
            ]
        )

########################################################################################################################

PINNED = join(dataPath, 'pinned.txt')
SEARCH_HISTORY = join(dataPath, 'search_history.csv')
PLAYBACK_HISTORY = join(dataPath, 'playback_history.list')

########################################################################################################################

CACHE_DEBUG = Addon().getSetting('do_not_use_cache') == 'true' and Addon().getSetting('debug') == 'true'
SEPARATOR = ' - ' if Addon().getSetting('wrap_labels') == '1' else '[CR]'


def cache_duration(duration):
    if CACHE_DEBUG:
        return 0
    else:
        return duration
