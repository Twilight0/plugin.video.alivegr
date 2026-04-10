# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

import os.path
from os import rename
import re
import pickled
import sqlite3
from itertags import iwrapper
from tulip import kodi, directory, cleantitle
from netclient import Net
from urllib.parse import parse_qsl, urlparse
from tulip.log import log
from .themes import iconname
from .constants import WEBSITE, PINNED, SEARCH_HISTORY, PLAYBACK_HISTORY, cache_duration
from tulip.kodi import update_repositories
from os import path
from time import time
from base64 import b64decode
from zlib import decompress, compress
from scrapetube.wrapper import list_playlist_videos, list_playlists


########################################################################################################################

leved = 'Q2dw5CchN3c39mck9ydhJ3L0VmbuI3ZlZXasF2LvoDc0RHa'
reset_cache = pickled.FunctionCache(kodi.cacheDirectory).reset_cache
cache_function = pickled.FunctionCache(kodi.cacheDirectory).cache_function


def stream_picker(links):

    _choice = kodi.selectDialog(heading=kodi.i18n(30006), list=[link[0] for link in links])

    if _choice <= len(links) and not _choice == -1:
        popped = [link[1] for link in links][_choice]
        return popped


# def m3u8_picker(url):
#
#     try:
#
#         if '|' not in url:
#             raise TypeError
#
#         link, _, head = url.rpartition('|')
#
#         headers = dict(parse_qsl(head))
#         streams = m3u8.load(link, headers=headers).playlists
#
#     except TypeError:
#
#         streams = m3u8.load(url).playlists
#
#     if not streams:
#         return url
#
#     qualities = []
#     urls = []
#
#     for stream in streams:
#
#         quality = repr(stream.stream_info.resolution).strip('()').replace(', ', 'x')
#
#         if quality == 'None':
#             quality = 'Auto'
#
#         uri = stream.absolute_uri
#
#         qualities.append(quality)
#
#         try:
#
#             if '|' not in url:
#                 raise TypeError
#
#             urls.append(uri + ''.join(url.rpartition('|')[1:]))
#
#         except TypeError:
#             urls.append(uri)
#
#     if len(qualities) == 1:
#
#         kodi.infoDialog(kodi.i18n(30220).format(qualities[0]))
#
#         return url
#
#     links = list(zip(qualities, urls))
#
#     return stream_picker(links)


def i18n():

    lang = 'el_GR' if 'Greek' in kodi.infoLabel('System.Language') else 'en_GB'

    return lang


def thumb_maker(video_id, hq=False):

    return 'http://img.youtube.com/vi/{0}/{1}.jpg'.format(video_id, 'mqdefault' if not hq else 'maxresdefault')


def other_addon_settings(query):

    try:

        if query == 'script.module.resolveurl':

            from resolveurl import display_settings
            display_settings()

        else:

            kodi.openSettings(addon_id=query)

    except Exception:

        pass


def reset_idx(notify=True, forceit=False):

    if kodi.setting('reset_idx') == 'true' or forceit:

        if kodi.setting('reset_live') == 'true' or forceit:

            kodi.setSetting('live_group', '0')

        kodi.setSetting('vod_group', '30213')
        kodi.setSetting('papers_group', '0')

        if notify:
            kodi.infoDialog(message=kodi.i18n(30402), time=3000)

        log('Indexers have been reset')


def activate_other_addon(url, query=None):

    if not url.startswith('plugin://'):
        url = ''.join(['plugin://', url, '/'])

    parsed = urlparse(url)

    if not kodi.condVisibility('System.HasAddon({0})'.format(parsed.netloc)):
        kodi.execute('InstallAddon({0})'.format(parsed.netloc))

    params = dict(parse_qsl(parsed.query))
    action = params.get('action')
    url = params.get('url')

    directory.run_builtin(addon_id=parsed.netloc, action=action, url=url, content_type=query)


def cache_clear(notify=True):

    log('Cache has been cleared')
    reset_cache()


def purge_bookmarks():

    if path.exists(kodi.bookmarksFile):
        if kodi.yesnoDialog(line1=kodi.i18n(30214)):
            kodi.deleteFile(kodi.bookmarksFile)
            kodi.infoDialog(kodi.i18n(30402))
        else:
            kodi.infoDialog(kodi.i18n(30403))
    else:
        kodi.infoDialog(kodi.i18n(30139))


def clear_search_history():

    if path.exists(SEARCH_HISTORY):
        if kodi.yesnoDialog(line1=kodi.i18n(30484).format(path.basename(SEARCH_HISTORY))):
            kodi.deleteFile(SEARCH_HISTORY)
            kodi.infoDialog(kodi.i18n(30402))
            kodi.refresh()
        else:
            kodi.infoDialog(kodi.i18n(30403))
    else:
        kodi.infoDialog(kodi.i18n(30347))


def clear_playback_history():

    if path.exists(PLAYBACK_HISTORY):
        if kodi.yesnoDialog(line1=kodi.i18n(30484).format(path.basename(PLAYBACK_HISTORY))):
            kodi.deleteFile(PLAYBACK_HISTORY)
            kodi.infoDialog(kodi.i18n(30402))
            kodi.refresh()
        else:
            kodi.infoDialog(kodi.i18n(30403))
    else:
        kodi.infoDialog(kodi.i18n(30347))


def tools_menu():

    kodi.execute('Dialog.Close(all)')

    kodi.execute('ActivateWindow(programs,"plugin://plugin.video.alivegr/?content_type=executable",return)')


def call_info():

    kodi.close_all()

    kodi.execute('ActivateWindow(programs,"plugin://plugin.video.alivegr/?content_type=executable&action=info",return)')


def greeting():

    kodi.infoDialog(kodi.i18n(30263))


def refresh():

    kodi.refresh()


def refresh_and_clear():

    cache_clear()
    kodi.sleep(100)
    refresh()


def thgiliwt(s):

    string = s[::-1]

    return b64decode(string)


def pawsesac(s, ison=''):

    string = s.swapcase()

    string = string + ison
    return string


def bourtsa(s):

    return decompress(s)


def xteni(s):

    return compress(s)


def geo_loc():

    json_obj = Net().http_GET('https://extreme-ip-lookup.com/json/').get_json()

    if not json_obj or 'error' in json_obj:
        json_obj = Net().http_GET('https://ip-api.com/json/').get_json()

    if not json_obj or 'error' in json_obj:
        json_obj = Net().http_GET('https://geoip.siliconweb.com/geo.json').get_json()

    country = json_obj.get('country', 'Worldwide')

    return country


def pin_to_file(file_, txt):

    if not kodi.exists(file_):
        kodi.makeFiles(kodi.dataPath)

    if not txt:
        return

    if txt not in pinned_from_file(file_):

        with open(file_, 'a') as f:
            f.writelines(txt + '\n')


def pinned_from_file(file_):

    if kodi.exists(file_):

        with open(file_, 'r') as f:
            text = [i.rstrip('\n') for i in f.readlines()][::-1]

        return text

    else:

        return ['']


def unpin_from_file(file_, txt):

    with open(file_, 'r') as f:
        text = [i.rstrip('\n') for i in f.readlines()]

    text.remove(txt)

    with open(file_, 'w') as f:
        if not text:
            text = ''
        else:
            text = '\n'.join(text) + '\n'
        f.write(text)


def pin(query):

    kodi.busy()

    # title = kodi.infoLabel('ListItem.Title')
    # pin_to_file(PINNED, title)
    pin_to_file(PINNED, query)

    kodi.infoDialog(kodi.i18n(30338), time=750)

    kodi.idle()


def unpin(query):

    kodi.busy()

    # title = kodi.infoLabel('ListItem.Title')
    # unpin_from_file(PINNED, title)
    unpin_from_file(PINNED, query)

    kodi.sleep(100)
    kodi.refresh()

    kodi.infoDialog(kodi.i18n(30338), time=750)

    kodi.idle()


def setup_various_keymaps(keymap):

    keymap_settings_folder = kodi.transPath('special://profile/keymaps')

    if not path.exists(keymap_settings_folder):
        kodi.makeFile(keymap_settings_folder)

    if keymap == 'previous':

        location = kodi.join(keymap_settings_folder, 'alivegr_tvguide.xml')

        lang_int = 30022

        def seq():

            previous_keymap = """<keymap>
    <tvguide>
        <keyboard>
            <key id="61448">previousmenu</key>
        </keyboard>
    </tvguide>
    <tvchannels>
        <keyboard>
            <key id="61448">previousmenu</key>
        </keyboard>
    </tvchannels>
</keymap>
"""

            with open(location, 'w') as f:
                f.write(previous_keymap)

    elif keymap == 'mouse':

        location = kodi.transPath(kodi.join('special://profile', 'keymaps', 'alivegr_mouse.xml'))

        lang_int = 30238

        def seq():

            string_start = '<keymap><slideshow><mouse>'
            string_end = '</mouse></slideshow></keymap>'
            string_for_left = '<leftclick>NextPicture</leftclick>'
            string_for_right = '<rightclick>PreviousPicture</rightclick>'
            string_for_middle = '<middleclick>Rotate</middleclick>'
            string_for_up = '<wheelup>ZoomIn</wheelup>'
            string_for_down = '<wheeldown>ZoomOut</wheeldown>'

            classes = [
                string_for_left, string_for_right, string_for_middle,
                string_for_up, string_for_down
            ]

            map_left = kodi.i18n(30241)
            map_right = kodi.i18n(30242)
            map_middle = kodi.i18n(30243)
            map_up = kodi.i18n(30244)
            map_down = kodi.i18n(30245)

            keys = [
                map_left, map_right, map_middle, map_up, map_down
            ]

            kodi.okDialog(kodi.name(), kodi.i18n(30240))

            indices = kodi.dialog.multiselect(kodi.name(), keys)

            if not indices:

                kodi.infoDialog(kodi.i18n(30246))

            else:

                finalized = []

                for i in indices:
                    finalized.append(classes[i])

                joined = ''.join(finalized)

                to_write = string_start + joined + string_end

                with open(location, 'w') as f:
                    f.write(to_write)

                kodi.execute('Action(reloadkeymaps)')

    elif keymap == 'samsung':

        string = '''<keymap>
    <global>
        <keyboard>
            <key id="61670">contextmenu</key>
        </keyboard>
    </global>
    <fullscreenvideo>
        <keyboard>
            <key id="61670">osd</key>
        </keyboard>
    </fullscreenvideo>
    <visualisation>
        <keyboard>
            <key id="61670">osd</key>
        </keyboard>
    </visualisation>
</keymap>'''

        location = kodi.join(keymap_settings_folder, 'samsung.xml')

        lang_int = 30022

        def seq():

            with open(location, 'w') as f:
                f.write(string)

    elif keymap == 'stop_playback':

        string = '''<keymap>
    <fullscreenvideo>
        <keyboard>
            <key id="61448">stop</key>
        </keyboard>
        <keyboard>
            <key id="61448" mod="longpress">back</key>
        </keyboard>
    </fullscreenvideo>
    <visualisation>
        <keyboard>
            <key id="61448">stop</key>
        </keyboard>
        <keyboard>
            <key id="61448" mod="longpress">back</key>
        </keyboard>
    </visualisation>
</keymap>'''

        location = kodi.join(keymap_settings_folder, 'stop_playback.xml')

        lang_int = 30022

        def seq():

            with open(location, 'w') as f:
                f.write(string)

    yes = kodi.yesnoDialog(kodi.i18n(lang_int))

    if yes:

        if path.exists(location):

            choices = [kodi.i18n(30248), kodi.i18n(30249)]

            _choice = kodi.selectDialog(choices, heading=kodi.i18n(30247))

            if _choice == 0:

                seq()
                kodi.okDialog(kodi.name(), kodi.i18n(30027) + ', ' + (kodi.i18n(30028)))
                kodi.infoDialog(kodi.i18n(30402))
                kodi.execute('Action(reloadkeymaps)')

            elif _choice == 1:

                kodi.deleteFile(location)
                kodi.infoDialog(kodi.i18n(30402))
                kodi.execute('Action(reloadkeymaps)')

            else:

                kodi.infoDialog(kodi.i18n(30403))

        else:

            seq()
            kodi.okDialog(kodi.name(), kodi.i18n(30027) + ', ' + (kodi.i18n(30028)))
            kodi.infoDialog(kodi.i18n(30402))

            kodi.execute('Action(reloadkeymaps)')

    else:

        kodi.infoDialog(kodi.i18n(30403))


def isa_setup():

    settings_file = '''<settings version="2">
    <setting id="MINBANDWIDTH" default="true">0</setting>
    <setting id="MAXBANDWIDTH" default="true">0</setting>
    <setting id="MAXRESOLUTION" default="true">0</setting>
    <setting id="MAXRESOLUTIONSECURE" default="true">0</setting>
    <setting id="STREAMSELECTION">2</setting>
    <setting id="MEDIATYPE" default="true">0</setting>
    <setting id="HDCPOVERRIDE" default="true">false</setting>
    <setting id="IGNOREDISPLAY" default="true">false</setting>
    <setting id="DECRYPTERPATH" default="true">special://xbmcbinaddons</setting>
    <setting id="WIDEVINE_API" default="true">10</setting>
    <setting id="PRERELEASEFEATURES" default="true">false</setting>
</settings>
'''

    def wizard():

        lines = settings_file.splitlines()[1:-1]

        for line in lines:

            kodi.addon('inputstream.adaptive').setSetting(
                re.search(r'id="(\w+)"', line).group(1), re.search(r'>([\w/:]+)<', line).group(1)
            )

    if kodi.yesnoDialog(line1=kodi.i18n(30022)):

        wizard()
        kodi.infoDialog(message=kodi.i18n(30402), time=3000)


def yt_setup():

    def wizard():

        kodi.addon('plugin.video.youtube').setSetting('kodion.setup_wizard', 'false')
        kodi.addon('plugin.video.youtube').setSetting('youtube.language', 'el')
        kodi.addon('plugin.video.youtube').setSetting('youtube.region', 'GR')
        kodi.infoDialog(message=kodi.i18n(30402), time=3000)

    def yt_mpd():

        kodi.addon('plugin.video.youtube').setSetting('kodion.video.quality.mpd', 'true')
        kodi.addon('plugin.video.youtube').setSetting('kodion.mpd.videos', 'true')
        kodi.addon('plugin.video.youtube').setSetting('kodion.mpd.live_streams', 'true')
        kodi.infoDialog(message=kodi.i18n(30402), time=3000)

########################################################################################################################

    if kodi.yesnoDialog(line1=kodi.i18n(30132)):

        wizard()

    if kodi.condVisibility('System.HasAddon(inputstream.adaptive)') and kodi.yesnoDialog(line1=kodi.i18n(30287)):

        yt_mpd()


########################################################################################################################


def file_to_text(file_):

    try:

        with open(file_, encoding='utf-8') as text:
            result = text.read()

    except Exception:

        with open(file_) as text:
            result = text.read()

    return result


def trim_content(f):

    history_size = int(kodi.setting('history_size'))

    file_ = open(f, 'r', encoding='utf-8')

    text = [i.rstrip('\n') for i in file_.readlines()][::-1]

    file_.close()

    if len(text) > history_size:

        file_ = open(f, 'w', encoding='utf-8')

        dif = history_size - len(text)
        result = text[:dif][::-1]
        file_.write('\n'.join(result) + '\n')
        file_.close()


def add_to_file(f, text, trim_file=True):

    if not text:
        return

    try:

        file_ = open(f, 'r', encoding='utf-8')
        if text + '\n' in file_.readlines():
            return
        else:
            pass
        file_.close()

    except IOError:
        log('File {0} does not exist, creating new...'.format(os.path.basename(f)))

    file_ = open(f, 'a', encoding='utf-8')

    file_.writelines(text + '\n')
    file_.close()
    if trim_file:
        trim_content(f=f)


def process_file(f, text, mode='remove'):

    file_ = open(f, 'r', encoding='utf-8')

    lines = file_.readlines()
    file_.close()

    if text + '\n' in lines:
        if mode == 'change':
            idx = lines.index(text + '\n')
            search_type, _, search_term = lines[idx].strip('\n').partition(',')
            str_input = kodi.inputDialog(heading=kodi.i18n(30445), default=search_term)
            str_input = cleantitle.strip_accents(str_input)
            lines[idx] = ','.join([search_type, str_input]) + '\n'
        else:
            lines.remove(text + '\n')
    else:
        return

    file_ = open(f, 'w', encoding='utf-8')
    file_.write(''.join(lines))
    file_.close()

    kodi.refresh()


def read_from_file(f):

    """
    Reads from history file which is stored in plain text, line by line
    :return: List
    """

    if kodi.exists(f):

        file_ = open(f, 'r', encoding='utf-8')
        text = [i.rstrip('\n') for i in file_.readlines()][::-1]

        file_.close()

        return text

    else:

        return


def changelog(get_text=False):

    if kodi.setting('changelog_lang') == '0' and 'Greek' in kodi.infoLabel('System.Language'):
        change_txt = 'changelog.el.txt'
    elif (
            kodi.setting('changelog_lang') == '0' and 'Greek' not in kodi.infoLabel('System.Language')
    ) or kodi.setting('changelog_lang') == '1':
        change_txt = 'changelog.en.txt'
    else:
        change_txt = 'changelog.el.txt'

    change_txt = kodi.join(kodi.addonPath, 'resources', 'texts', change_txt)

    if get_text:
        return file_to_text(change_txt).partition(u'\n\n')[0]
    else:
        kodi.dialog.textviewer(kodi.addonInfo('name') + ', ' + kodi.i18n(30110), file_to_text(change_txt))


def dmca():

    location = kodi.join(
        kodi.transPath(kodi.addonInfo('path')), 'resources', 'texts', 'dmca_{0}.txt'.format(i18n())
    )

    kodi.dialog.textviewer(kodi.addonInfo('name'), file_to_text(location))


def pp():

    location = kodi.join(
        kodi.transPath(kodi.addonInfo('path')), 'resources', 'texts', 'pp_{0}.txt'.format(i18n())
    )

    kodi.dialog.textviewer(kodi.addonInfo('name'), file_to_text(location))


def disclaimer():

    try:
        text = kodi.addonInfo('disclaimer').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        text = kodi.addonInfo('disclaimer')

    kodi.dialog.textviewer(kodi.addonInfo('name') + ', ' + kodi.i18n(30129), text)


def do_not_ask_again():

    kodi.setSetting('new_version_prompt', 'false')

    kodi.okDialog('AliveGR', kodi.i18n(30361))


def prompt():

    kodi.okDialog('AliveGR', kodi.i18n(30356).format(remote_version()))

    choices = [kodi.i18n(30357), kodi.i18n(30358), kodi.i18n(30359)]

    _choice = kodi.selectDialog(choices, heading=kodi.i18n(30482))

    if _choice == 0:
        update_repositories()
    elif _choice == 1:
        kodi.close_all()
    elif _choice == 2:
        do_not_ask_again()


def welcome():

    choices = [kodi.i18n(30329), kodi.i18n(30340), kodi.i18n(30129), kodi.i18n(30333)]

    _choice = kodi.selectDialog(choices, heading=kodi.i18n(30267).format(kodi.version()))

    if _choice in [0, -1]:
        kodi.close_all()
    elif _choice == 1:
        changelog()
    elif _choice == 2:
        disclaimer()
    elif _choice == 3:
        kodi.open_web_browser(WEBSITE)


def new_version(new=False):

    version_file = kodi.join(kodi.dataPath, 'version.txt')

    if not path.exists(version_file) or new:

        if not path.exists(kodi.dataPath):

            kodi.makeFile(kodi.dataPath)

        try:
            with open(version_file, mode='w', encoding='utf-8') as f:
                f.write(kodi.version())
        except Exception:
            with open(version_file, 'w') as f:
                f.write(kodi.version())

        return True

    else:

        try:
            with open(version_file, encoding='utf-8') as f:
                version = f.read()
        except Exception:
            with open(version_file) as f:
                version = f.read()

        if version != kodi.version():
            return new_version(new=True)
        else:
            return False


@cache_function(cache_duration(360))
def remote_version():

    url = 'https://raw.githubusercontent.com/Twilight0/repository.twilight0/refs/heads/master/repo_dir/plugin.video.alivegr/addon.xml'
    xml = Net().http_GET(url).content

    version = iwrapper(xml, 'addon', attrs={'id': kodi.addonInfo('id')}, ret='version').__next__()

    version = int(version.replace('.', ''))

    return version


def rename_history_csv():

    try:
        if not kodi.exists(SEARCH_HISTORY):
            rename(SEARCH_HISTORY.replace('search_', ''), SEARCH_HISTORY)
    except Exception:
        pass


def checkpoint():

    check = time() + 10800

    try:
        new_version_prompt = kodi.setting('new_version_prompt') == 'true' and remote_version() > int(kodi.version().replace('.', ''))
    except ValueError:  # will fail if version install is alpha or beta
        new_version_prompt = False

    rename_history_csv()

    if new_version():

        # if kodi.yesnoDialog(kodi.i18n(30267)):
        #     changelog()
        welcome()

        cache_clear(notify=False)
        reset_idx(notify=False)
        clean_old_textures()

        if kodi.setting('debug') == 'true':

            log(
                'Debug settings have been reset, please do not touch these settings manually,'
                ' they are *only* meant to help developer test various aspects.'
            )

            kodi.setSetting('debug', 'false')

        kodi.setSetting('last_check', str(check))

    elif new_version_prompt and time() > float(kodi.setting('last_check')):

        prompt()
        kodi.setSetting('last_check', str(check))


def clean_old_textures():

    base_path = kodi.transPath('special://profile/')
    textures_path = kodi.join(base_path, 'Thumbnails')
    db_path = kodi.join(base_path, 'Database/Textures13.db')

    try:

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Find the cached filenames for your specific assets
        query = "SELECT cachedurl FROM texture WHERE url LIKE ? OR url LIKE ?"
        params = (f"%{kodi.addonInfo('id')}/icon.png", f"%{kodi.addonInfo('id')}/fanart.jpg")

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for (cached_rel_path,) in rows:

            full_file_path = kodi.join(textures_path, cached_rel_path)

            if kodi.exists(full_file_path):
                kodi.deleteFile(full_file_path)

    except sqlite3.Error as e:
        print(f"Error reading database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()



def dev():

    if kodi.setting('debug') == 'false':

        dwp = kodi.dialog.input(
            'I hope you know what you\'re doing!', type=kodi.password_input, option=kodi.verify
        )

        text = '1234'

        if text == dwp:

            kodi.setSetting('debug', 'true')

            reset_cache()

        else:

            kodi.infoDialog('Without proper password, debug/developer mode won\'t work', time=4000)
            kodi.execute('ActivateWindow(home)')

    elif kodi.setting('debug') == 'true':

        kodi.setSetting('debug', 'false')


def page_selector(query):

    pages = [kodi.i18n(30415).format(i) for i in list(range(1, int(query) + 1))]

    _choice = kodi.selectDialog(pages, heading=kodi.i18n(30416))

    if _choice != -1:

        kodi.setSetting('page', str(_choice))
        kodi.sleep(200)
        kodi.refresh()

        if kodi.setting('pagination_reset') == 'true':
            # wait a second in order to ensure container is first loaded then reset the page
            kodi.sleep(1000)
            kodi.setSetting('page', '0')


def page_menu(pages, reset=False):

    if not reset:
        index = str(int(kodi.setting('page')) + 1)
    else:
        index = '1'

    menu = {
        'title': kodi.i18n(30414).format(index),
        'action': 'page_selector',
        'query': str(pages),
        'icon': iconname('switcher'),
        'isFolder': 'False',
        'isPlayable': 'False'
    }

    return menu


@cache_function(cache_duration(60))
def yt_playlist(url):

    return list_playlist_videos(url)


@cache_function(cache_duration(480))
def yt_playlists(url):

    return list_playlists(url)
