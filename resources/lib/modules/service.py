# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import xbmc
import xbmcaddon

__addon__ = 'plugin.video.alivegr'


class SettingsMonitor(xbmc.Monitor):

    def __init__(self):

        super(SettingsMonitor, self).__init__()
        self.addon = xbmcaddon.Addon(__addon__)

    def onSettingsChanged(self):

        self.show_clear_bookmarks = self.addon.getSetting('show_clear_bookmarks')
        self.paginate_items = self.addon.getSetting('paginate_items')
        self.wrap_labels = self.addon.getSetting('wrap_labels')
        self.lang_split = self.addon.getSetting('lang_split')
        self.theme = self.addon.getSetting('theme')
        self.show_live = self.addon.getSetting('show_live')
        self.show_m3u = self.addon.getSetting('show_m3u')
        # self.show_pvr = self.addon.getSetting('show_pvr')
        # self.show_networks = self.addon.getSetting('show_networks')
        # self.show_news = self.addon.getSetting('show_news')
        self.show_movies = self.addon.getSetting('show_movies')
        self.show_short_films = self.addon.getSetting('show_short_films')
        self.show_series = self.addon.getSetting('show_series')
        self.show_shows = self.addon.getSetting('show_shows')
        self.show_theater = self.addon.getSetting('show_theater')
        self.show_docs = self.addon.getSetting('show_docs')
        self.show_sports = self.addon.getSetting('show_sports')
        self.show_kids = self.addon.getSetting('show_kids')
        self.show_misc = self.addon.getSetting('show_history')
        # self.show_radio = self.addon.getSetting('show_radio')
        self.show_music = self.addon.getSetting('show_music')
        self.show_search = self.addon.getSetting('show_search')
        self.show_bookmarks = self.addon.getSetting('show_bookmarks')
        self.show_settings = self.addon.getSetting('show_settings')
        self.show_quit = self.addon.getSetting('show_quit')
        self.live_tv_mode = self.addon.getSetting('live_tv_mode')
        self.show_live_switcher = self.addon.getSetting('show_live_switcher')
        self.show_vod_switcher = self.addon.getSetting('show_vod_switcher')
        # self.show_pic_switcher = self.addon.getSetting('show_pic_switcher')

        self.action()

    @staticmethod
    def action():

        if __addon__ in xbmc.getInfoLabel('Container.PluginName'):
            xbmc.executebuiltin('Container.Refresh')


if __name__ == '__main__':

    monitor = SettingsMonitor()

    # Keep the script running until Kodi shuts down
    while not monitor.abortRequested():
        # Wait for 10 seconds or until abort is requested
        if monitor.waitForAbort(10):
            break
