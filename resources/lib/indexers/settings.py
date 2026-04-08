# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import sys
from ..modules.themes import iconname
from ..modules.constants import ART_ID, PAYPAL, FORUM, TWITTER
from ..modules.utils import changelog
from tulip import kodi, directory


class Indexer:

    def __init__(self):

        self.list = []

    def menu(self):

        self.list = [
            {
                'title': '[B]' + kodi.addonInfo('name') + ': ' + kodi.i18n(30255) + '[/B]',
                'action': 'info',
                'icon': kodi.addonInfo('icon'),
                'isFolder': 'True'
            }
            ,
            {
                'title': '[B]' + kodi.addonInfo('name') + ': ' + kodi.i18n(30017) + '[/B]',
                'action': 'actions',
                'icon': kodi.addonInfo('icon'),
                'isFolder': 'True'
            }
            ,
            {
                'title': kodi.addonInfo('name') + ': ' +kodi.i18n(30011),
                'action': 'openSettings',
                'icon': iconname('settings'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30319),
                'action': 'global_settings',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
        ]

        if kodi.condVisibility('Window.IsVisible(programs)'):

            for i in self.list:
                i.update({'cm': [{'title': 30307, 'query': {'action': 'root'}}]})

        directory.builder(self.list)

    def actions(self):

        self.list = [
            {
                'title': kodi.addonInfo('name') + ': ' + kodi.i18n(30056),
                'action': 'cache_clear',
                'icon': iconname('empty'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.addonInfo('name') + ': ' + kodi.i18n(30135),
                'action': 'clear_bookmarks',
                'icon': iconname('empty'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.addonInfo('name') + ': ' + kodi.i18n(30408),
                'action': 'clear_search_history',
                'icon': iconname('empty'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.addonInfo('name') + ': ' + kodi.i18n(30471),
                'action': 'clear_playback_history',
                'icon': iconname('empty'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.addonInfo('name') + ': ' + kodi.i18n(30134),
                'action': 'reset_idx',
                'icon': iconname('settings'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30320) + ': ' + kodi.i18n(30272),
                'action': 'input_stream_addons',
                'icon': iconname('monitor'),
                'isFolder': 'True'
            }
            ,
            {
                'title': '[B]' + kodi.i18n(30340) + '[/B]',
                'action': 'changelog',
                'icon': kodi.addonInfo('icon'),
                'plot': changelog(get_text=True),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30295),
                'action': 'toggle_debug',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30341),
                'action': 'kodi_log_upload',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30472),
                'action': 'skin_debug',
                'isFolder': 'False',
                'isPlayable': 'False',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png')
            }
            ,
            {
                'title': kodi.i18n(30296),
                'action': 'force',
                'isFolder': 'False',
                'isPlayable': 'False',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png')
            }
        ]

        directory.builder(self.list)

    def info(self):

        separator = '[CR]' if kodi.setting('wrap_labels') == '0' else ' '

        try:
            disclaimer = kodi.addonInfo('disclaimer').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
            disclaimer = kodi.addonInfo('disclaimer')

        self.list = [
            {
                'title': kodi.i18n(30331),
                'action': 'welcome',
                'icon': kodi.addonInfo('icon'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30105),
                'action': 'dmca',
                'plot': disclaimer,
                'icon': kodi.addonmedia(
                    addonid=ART_ID, theme='icons', path='dmca.png'
                ),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30290),
                'action': 'pp',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30260).format(separator),
                'action': 'open_link',
                'url': FORUM,
                'plot': 'Github discussions',
                'icon': kodi.addonmedia(
                    addonid=ART_ID, theme='icons', path='github.png'
                ),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30271).format(separator),
                'action': 'open_link',
                'url': TWITTER,
                'plot': 'X Profile',
                'icon': kodi.addonmedia(
                    addonid=ART_ID, theme='icons', path='x.png'
                ),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30141) + ': [COLOR cyan]' + PAYPAL + '[/COLOR]',
                'action': 'open_link',
                'url': PAYPAL,
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30256).format(separator, kodi.addonInfo('version')),
                'action': 'force',
                'plot': kodi.i18n(30265),
                'icon': kodi.addonInfo('icon'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30257).format(separator, kodi.addon('script.module.tulip').getAddonInfo('version')),
                'action': 'force',
                'plot': kodi.i18n(30265),
                'icon': kodi.addon('script.module.tulip').getAddonInfo('icon'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {

                'title': kodi.i18n(30264).format(separator, kodi.addon('script.module.resolveurl').getAddonInfo('version')),
                'action': 'other_addon_settings',
                'query': 'script.module.resolveurl',
                'plot': kodi.i18n(30265),
                'icon': kodi.addon('script.module.resolveurl').getAddonInfo('icon'),
                'isFolder': 'False',
                'isPlayable': 'False'

            }
            ,
            {
                'title': kodi.i18n(30258).format(separator, kodi.kodi_version()),
                'action': 'system_info',
                'plot': kodi.i18n(30263),
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30303).format(separator, '.'.join([str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2])])),
                'action': 'system_info',
                'plot': kodi.i18n(30263),
                'image': kodi.addonmedia(addonid=ART_ID, theme='icons', path='profile.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
        ]

        directory.builder(self.list, content='movies')

    def input_stream_addons(self):

        self.list = [
            {
                'title': kodi.i18n(30253),
                'action': 'isa_enable',
                'isFolder': 'False',
                'isPlayable': 'False',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'cm': [{'title': 30253, 'query': {'action': 'other_addon_settings', 'query': 'inputstream.adaptive'}}]
            }
            ,
            {
                'title': kodi.i18n(30273),
                'action': 'other_addon_settings',
                'query': 'inputstream.adaptive',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png'),
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': kodi.i18n(30275),
                'action': 'rtmp_enable',
                'isFolder': 'False',
                'isPlayable': 'False',
                'icon': kodi.addonmedia(addonid=ART_ID, theme='icons', path='kodi.png')
            }
        ]

        directory.builder(self.list)
