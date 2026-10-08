# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from xbmcaddon import Addon
from collections import OrderedDict
from urllib.parse import urljoin
from datetime import datetime
from tulip.kodi import dataPath, join, cacheDirectory, i18n
from pickled import FunctionCache

cache_function = FunctionCache(cacheDirectory).cache_function
cache_method = FunctionCache(cacheDirectory).cache_method

########################################################################################################################

ART_ID = 'resource.images.alivegr.artwork'
LOGOS_ID = 'resource.images.alivegr.logos'
PLUGINS_ID = 'script.module.resolveurl.pluginsgr'
PLUGINS_PATH = 'special://home/addons/{0}/resources/plugins/'.format(PLUGINS_ID)
YT_URL = 'https://www.youtube.com/watch?v='
PLAY_ACTION = '?action=play&url='
ALIVEGR = (
    '42bzpmLoN2Xyd2L3FmcvYmY0IGN3YmZ2QDZ0EGN4EWMwQGOzcDZxYGZ1EjYyUzYvADdodWasl2dU9SbvNmL05WZ052bj'
    'JXZzVnY1hGdpdmL0NXan9yL6MHc0RHa'
)

########################################################################################################################

WEBSITE = 'https://github.com/Twilight0/plugin.video.alivegr'
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

PLAYLIST_BASE = 'https://playlist.gr/'
PLAYLIST_AJAX = urljoin(PLAYLIST_BASE, 'ajax.php')
PLAYLIST_SEARCH = urljoin(PLAYLIST_BASE, 'search.php')

########################################################################################################################

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

GENRES = {
    'κωμωδία': i18n(30021),
    'δράμα': i18n(30023),
    'δράση': i18n(30024),
    'έγκλημα': i18n(30026),
    'ρομαντική': i18n(30029),
    'κοινωνική': i18n(30038),
    'θρίλλερ': i18n(30040),
    'μυστηρίου': i18n(30041),
    'οικογενειακή': i18n(30042),
    'μιούσικαλ': i18n(30044),
    'βιογραφία': i18n(30069),
    'επιστημονικής φαντασίας': i18n(30065),
    'ιστορική': i18n(30070),
    'πολεμική': i18n(30071),
    'πολιτική': i18n(30061),
    'ερωτική': i18n(30116),
    'μυθοπλασία': i18n(30118),
    'παιδικό': i18n(30117),
    'ντοκυμαντέρ': i18n(30077),
    'περιπέτεια': i18n(30084),
    'κινουμένων σχεδίων': i18n(30087),
    'αστυνομική': i18n(30088),
    'άλλο': i18n(30089),
    'τρόμου': i18n(30132),

}

########################################################################################################################

########################################################################################################################

PINNED = join(dataPath, 'pinned.txt')
SEARCH_HISTORY = join(dataPath, 'search_history.csv')
PLAYBACK_HISTORY = join(dataPath, 'playback_history.list')
STREAM_PREFS = join(dataPath, 'stream_preferences.json')
ALIVEGR_M3U = join(dataPath, 'alivegr.m3u')
GREEK_EPG_XML = 'https://ext.greektv.app/epg/epg.xml.gz'

########################################################################################################################

CACHE_DEBUG = (Addon().getSetting('do_not_use_cache') == 'true' and Addon().getSetting('debug') == 'true') or (Addon().getSetting('debug') == 'true' and Addon().getSetting('local_remote') == '0')
SEPARATOR = ' - ' if Addon().getSetting('wrap_labels') == '1' else '[CR]'


def cache_duration(duration):
    if CACHE_DEBUG:
        return 0
    else:
        return duration
