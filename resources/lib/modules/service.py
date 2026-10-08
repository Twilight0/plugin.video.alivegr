# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only

import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

__addon_id__ = 'plugin.video.alivegr'

ADDON_PATH = xbmcvfs.translatePath(xbmcaddon.Addon(__addon_id__).getAddonInfo('path'))
if ADDON_PATH not in sys.path:
    sys.path.insert(0, ADDON_PATH)

sys.path.append(xbmcvfs.translatePath('special://home/addons/script.module.tulip/resources/lib'))


class AliveGRPlayer(xbmc.Player):

    def __init__(self, service):
        super(AliveGRPlayer, self).__init__()
        self.service = service
        self.live_populated = False
        self.repeat_set = False

    def onAVStarted(self):
        self.handle_playback_started()

    def onPlayBackStarted(self):
        self.handle_playback_started()

    def handle_playback_started(self):
        if self.live_populated:
            return
        if not self.isPlayingVideo():
            return

        pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        if pl.size() != 1:
            if pl.size() > 1:
                self.live_populated = True
                self.repeat_set = True
            return

        current_title = (
            xbmcgui.Window(10000).getProperty('alivegr_playing_title')
            or xbmc.getInfoLabel('Player.Title')
        )

        if not current_title:
            return

        xbmc.log(f'AliveGR Service: Checking zapping playlist for "{current_title}" (pl size: {pl.size()})', xbmc.LOGINFO)

        try:
            from resources.lib.indexers.live import get_live_channel_list, Indexer
            channels = get_live_channel_list()
            current_idx = -1
            for i, ch in enumerate(channels):
                if ch.get('title') == current_title or ch.get('title', '').strip().lower() == current_title.strip().lower():
                    current_idx = i
                    break

            if current_idx == -1:
                all_channels, _ = Indexer().live()
                matching = [c for c in all_channels if c.get('title') == current_title or c.get('title', '').strip().lower() == current_title.strip().lower()]
                if matching:
                    group = matching[0].get('group')
                    channels = [c for c in all_channels if c.get('group') == group]
                    channels.sort(key=lambda k: k.get('title', '').lower())
                    for i, ch in enumerate(channels):
                        if ch.get('title') == current_title or ch.get('title', '').strip().lower() == current_title.strip().lower():
                            current_idx = i
                            break

            if current_idx == -1:
                xbmc.log(f'AliveGR Service: "{current_title}" not found in live channels', xbmc.LOGDEBUG)
                return

            if len(channels) <= 1:
                return

            self.live_populated = True
            xbmcgui.Window(10000).clearProperty('alivegr_playing_title')
            self.populate_playlist(pl, channels, current_idx)

        except Exception as e:
            xbmc.log(f'AliveGR Service: error in handle_playback_started: {e}', xbmc.LOGERROR)

    def populate_playlist(self, pl, channels, current_idx):
        from urllib.parse import quote_plus
        sysaddon = 'plugin://plugin.video.alivegr/'

        def build_entry(item):
            action = f"{sysaddon}?action=play"
            url_p = f"url={quote_plus(item['url'])}"
            title_p = f"title={quote_plus(item['title'])}" if item.get('title') else None
            image_p = f"image={quote_plus(item['image'])}" if item.get('image') else None
            streams_p = f"streams={quote_plus(item['streams'])}" if item.get('streams') else None
            plot_p = f"plot={quote_plus(item['plot'])}" if item.get('plot') else None
            genre_p = f"genre={quote_plus(item['genre'])}" if item.get('genre') else None
            parts = [q for q in [action, url_p, title_p, image_p, streams_p, plot_p, genre_p] if q]
            query_str = '&'.join(parts)

            it = xbmcgui.ListItem(label=item.get('title', ''))
            it.setProperty('IsPlayable', 'true')
            if item.get('image'):
                it.setArt({'icon': item['image'], 'thumb': item['image'], 'poster': item['image']})
            if item.get('plot'):
                it.setInfo('video', {'title': item.get('title', ''), 'plot': item.get('plot', '')})
            return query_str, it

        # Subsequent channels in lineup
        for i in range(current_idx + 1, len(channels)):
            q, it = build_entry(channels[i])
            pl.add(q, it)

        # Preceding channels in lineup (to wrap around circularly)
        for i in range(0, current_idx):
            q, it = build_entry(channels[i])
            pl.add(q, it)

        xbmc.executebuiltin('PlayerControl(RepeatAll)')
        self.repeat_set = True

        xbmc.log(
            f'AliveGR Service: Zapping playlist populated with {len(channels)} channels '
            f'(active channel: #{current_idx} "{channels[current_idx].get("title")}", pl size: {pl.size()})',
            xbmc.LOGINFO
        )

    def onPlayBackStopped(self):
        self.live_populated = False
        try:
            xbmcgui.Window(10000).clearProperty('alivegr_playing_title')
        except Exception:
            pass
        if self.repeat_set:
            self.repeat_set = False
            xbmc.executebuiltin('PlayerControl(RepeatOff)')
        self.service.onPlayBackStopped()

    def onPlayBackEnded(self):
        self.live_populated = False
        try:
            xbmcgui.Window(10000).clearProperty('alivegr_playing_title')
        except Exception:
            pass
        if self.repeat_set:
            self.repeat_set = False
            xbmc.executebuiltin('PlayerControl(RepeatOff)')
        self.service.onPlayBackEnded()


class AliveGRService(xbmc.Monitor):

    def __init__(self):

        super(AliveGRService, self).__init__()
        self.addon = xbmcaddon.Addon(__addon_id__)
        self.auto_start = self.addon.getSetting('auto_start') == 'true'
        self.player = AliveGRPlayer(self)

        if self.auto_start:
            self.launch_logic()

    def onSettingsChanged(self):

        new_val = self.addon.getSetting('auto_start') == 'true'

        if new_val and not self.auto_start:

            self.launch_logic()

        self.auto_start = new_val

        if __addon_id__ in xbmc.getInfoLabel('Container.PluginName'):
            xbmc.executebuiltin('Container.Refresh')

    def onPlayBackStopped(self):
        pass

    def onPlayBackEnded(self):
        pass

    def launch_logic(self):

        retries = 0

        while not xbmc.getCondVisibility('Window.IsActive(home)') and not self.abortRequested():

            if retries > 60:
                xbmc.log('AliveGR launched: Retry #' + str(retries), xbmc.LOGDEBUG)
                break
            xbmc.sleep(200)
            retries += 1

        xbmc.executebuiltin(f'RunAddon({__addon_id__})')


if __name__ == '__main__':

    monitor = AliveGRService()

    while not monitor.abortRequested():

        if monitor.waitForAbort(5):
            break

    del monitor.player
