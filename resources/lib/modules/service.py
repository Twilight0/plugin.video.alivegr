# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import sys
import xbmc
import xbmcaddon

__addon__ = 'plugin.video.alivegr'
__sysaddon__ = 'plugin://{}/'.format(__addon__)


class SettingsMonitor(xbmc.Monitor):

    def __init__(self):

        super(SettingsMonitor, self).__init__()
        self.addon = xbmcaddon.Addon(__addon__)

    def onSettingsChanged(self):

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
