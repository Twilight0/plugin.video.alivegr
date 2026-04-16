# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from tulip import kodi
from os import path


def lang_choice():

    selections = [kodi.i18n(30217), kodi.i18n(30218), kodi.i18n(30312), kodi.i18n(30327)]

    dialog = kodi.selectDialog(selections)

    if dialog == 0:
        kodi.execute('Addon.Default.Set(kodi.resource.language)')
    elif dialog == 1:
        languages = [kodi.i18n(30286), kodi.i18n(30299)]
        layouts = ['English QWERTY', 'Greek QWERTY']
        indices = kodi.dialog.multiselect(kodi.name(), languages)
        kodi.set_gui_setting('locale.keyboardlayouts', [layouts[i] for i in indices])
    elif dialog == 2:
        kodi.set_gui_setting('locale.charset', 'CP1253')
        kodi.set_gui_setting('subtitles.charset', 'CP1253')
    elif dialog == 3:
        kodi.execute('Dialog.Close(all)')
        kodi.execute('ActivateWindow(interfacesettings)')
    else:
        kodi.execute('Dialog.Close(all)')


def isa_enable():

    try:

        enabled = kodi.addon_details('inputstream.adaptive').get('enabled')

    except Exception:

        enabled = False

    try:

        if enabled:

            kodi.infoDialog(kodi.i18n(30254))
            return

        else:

            xbmc_path = kodi.join('special://xbmc', 'addons', 'inputstream.adaptive')
            home_path = kodi.join('special://home', 'addons', 'inputstream.adaptive')

            if path.exists(kodi.transPath(xbmc_path)) or path.exists(kodi.transPath(home_path)):

                yes = kodi.yesnoDialog(kodi.i18n(30252))

                if yes:

                    kodi.enable_addon('inputstream.adaptive')
                    kodi.infoDialog(kodi.i18n(30402))

            else:

                try:

                    kodi.execute('InstallAddon(inputstream.adaptive)')

                except Exception:

                    kodi.okDialog(heading='AliveGR', line1=kodi.i18n(30323))

    except Exception:

        kodi.infoDialog(kodi.i18n(30278))


def rtmp_enable():

    try:

        enabled = kodi.addon_details('inputstream.rtmp').get('enabled')

    except Exception:

        enabled = False

    try:

        if enabled:

            kodi.infoDialog(kodi.i18n(30276))
            return

        else:

            xbmc_path = kodi.join('special://xbmc', 'addons', 'inputstream.rtmp')
            home_path = kodi.join('special://home', 'addons', 'inputstream.rtmp')

            if path.exists(kodi.transPath(xbmc_path)) or path.exists(kodi.transPath(home_path)):

                yes = kodi.yesnoDialog(kodi.i18n(30277))

                if yes:

                    kodi.enable_addon('inputstream.rtmp')
                    kodi.infoDialog(kodi.i18n(30402))

            else:

                try:

                    kodi.execute('InstallAddon(inputstream.rtmp)')

                except Exception:

                    kodi.okDialog(heading='AliveGR', line1=kodi.i18n(30323))

    except Exception:

        kodi.infoDialog(kodi.i18n(30279))


def log_upload():

    exists = kodi.condVisibility('System.HasAddon(script.kodi.loguploader)')
    addon_path = kodi.transPath(kodi.join('special://', 'home', 'addons', 'script.kodi.loguploader'))

    if not exists:

        if path.exists(addon_path):
            kodi.enable_addon('script.kodi.loguploader')
        else:
            kodi.execute('InstallAddon(script.kodi.loguploader)')

        while not path.exists(addon_path):
            kodi.sleep(1000)
        else:
            kodi.execute('RunScript(script.kodi.loguploader)')

    else:

        kodi.execute('RunScript(script.kodi.loguploader)')


def force():

    kodi.execute('UpdateAddonRepos')
    kodi.infoDialog(kodi.i18n(30261))
