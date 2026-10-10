# -*- coding: utf-8 -*-
"""
Kodi environment mock and harness for AliveGR standalone test suite.
"""

import os
import sys
import types
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Provide dummy tulip.init in sys.modules to prevent tulip from parsing runner's sys.argv
tulip_init = types.ModuleType('tulip.init')
tulip_init.syshandle = 1
tulip_init.sysaddon = 'plugin.video.alivegr'
tulip_init.params = {'action': None}
tulip_init.__all__ = ["syshandle", "sysaddon", "params"]
sys.modules['tulip.init'] = tulip_init

TEST_PROFILE = os.path.join(tempfile.gettempdir(), 'alivegr_test_profile')
os.makedirs(os.path.join(TEST_PROFILE, 'cache'), exist_ok=True)


def make_mod(name, **attrs):
    m = types.ModuleType(name)
    m.__all__ = list(attrs.keys())
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


class MockStat:
    def __init__(self, path):
        self.path = path

    def st_mtime(self):
        try:
            return os.path.getmtime(self.path)
        except Exception:
            return 0

    def st_size(self):
        try:
            return os.path.getsize(self.path)
        except Exception:
            return 0


class MockAddon:
    def __init__(self, id=None):
        self.id = id or 'plugin.video.alivegr'
        self._settings = {
            'do_not_use_cache': 'true',
            'debug': 'false',
            'history_size': '50',
            'wrap_labels': '0',
            'group': '0',
            'live_remote': '',
            'live_local': '',
            'local_remote': '2',
            'live_stream_fallback': 'true',
            'stream_preference': '0',
            'changelog_lang': '0',
        }

    def getAddonInfo(self, attr):
        if attr == 'version':
            return '3.0.0'
        if attr == 'name':
            return 'AliveGR'
        if attr == 'path':
            return REPO_ROOT
        if attr == 'profile':
            return TEST_PROFILE
        if attr == 'id':
            return self.id
        return '/tmp'

    def getSetting(self, key):
        return self._settings.get(key, '')

    def setSetting(self, key, value):
        self._settings[key] = str(value)

    def getLocalizedString(self, id):
        return f'str_{id}'


def _translate_special_path(p):
    if not isinstance(p, str):
        return p
    if p.startswith('special://temp'):
        return p.replace('special://temp', os.path.join(tempfile.gettempdir(), 'kodi_test_temp'), 1)
    if p.startswith('special://profile') or p.startswith('special://masterprofile'):
        return p.replace('special://profile', TEST_PROFILE, 1).replace('special://masterprofile', TEST_PROFILE, 1)
    if p.startswith('special://home'):
        return p.replace('special://home', os.path.dirname(REPO_ROOT), 1)
    if p.startswith('special://xbmc') or p.startswith('special://skin'):
        return p.replace('special://xbmc', REPO_ROOT, 1).replace('special://skin', REPO_ROOT, 1)
    return p


# Inject Kodi C/Python bindings
sys.modules['xbmc'] = make_mod(
    'xbmc',
    LOGINFO=1, LOGERROR=2, LOGWARNING=3, LOGNOTICE=4, LOGDEBUG=5,
    log=lambda *a, **k: None,
    translatePath=_translate_special_path,
    getInfoLabel=lambda l: '21.0' if l == 'System.BuildVersion' else ('Greek' if 'Language' in l else ''),
    getCondVisibility=lambda s: True,
    executeJSONRPC=lambda cmd: '{}',
    Keyboard=object,
    sleep=lambda ms: None,
    executebuiltin=lambda *a: None,
    getSkinDir=lambda: 'skin.estuary',
    Player=object,
    Monitor=lambda: make_mod('Monitor', waitForAbort=lambda s: False, abortRequested=lambda: False),
    getCleanMovieTitle=lambda t: t,
    getRegion=lambda r: '',
    VideoStreamDetail=object,
)

sys.modules['xbmcgui'] = make_mod(
    'xbmcgui',
    Dialog=lambda: make_mod('Dialog', notification=lambda *a, **k: None, ok=lambda *a, **k: None, select=lambda *a, **k: -1),
    DialogProgress=lambda: make_mod('DialogProgress'),
    DialogProgressBG=lambda: make_mod('DialogProgressBG'),
    Window=lambda id: make_mod('Window', getProperty=lambda k: '', setProperty=lambda k, v: None),
    WindowDialog=lambda: make_mod('WindowDialog'),
    ControlButton=object,
    ControlImage=object,
    INPUT_ALPHANUM=0,
    INPUT_PASSWORD=1,
    ALPHANUM_HIDE_INPUT=2,
    INPUT_DATE=3,
    INPUT_TIME=4,
    PASSWORD_VERIFY=1,
    ListItem=lambda *a, **k: make_mod('ListItem', setProperty=lambda *a: None, setInfo=lambda *a: None, setArt=lambda *a: None),
)

sys.modules['xbmcplugin'] = make_mod(
    'xbmcplugin',
    addDirectoryItem=lambda *a, **k: True,
    addDirectoryItems=lambda *a, **k: True,
    endOfDirectory=lambda *a, **k: True,
    setContent=lambda *a, **k: None,
    setProperty=lambda *a, **k: None,
    setPluginCategory=lambda *a, **k: None,
    setResolvedUrl=lambda *a, **k: None,
    addSortMethod=lambda *a, **k: None,
)

sys.modules['xbmcvfs'] = make_mod(
    'xbmcvfs',
    File=open,
    Stat=MockStat,
    mkdir=lambda p: os.makedirs(p, exist_ok=True),
    mkdirs=lambda p: os.makedirs(p, exist_ok=True),
    delete=lambda p: None,
    rmdir=lambda p: None,
    listdir=lambda p: ([], []),
    exists=os.path.exists,
    copy=lambda *a: True,
    rename=os.rename,
    makeLegalFilename=lambda f: f,
    translatePath=_translate_special_path,
)

sys.modules['xbmcaddon'] = make_mod('xbmcaddon', Addon=MockAddon)

# Add vendor & module dependencies from local Kodi addons
addon_paths = [
    '/home/twilight/.kodi/addons/script.module.six/lib',
    '/home/twilight/.kodi/addons/script.module.kodi-six/libs',
    '/home/twilight/.kodi/addons/script.module.certifi/lib',
    '/home/twilight/.kodi/addons/script.module.chardet/lib',
    '/home/twilight/.kodi/addons/script.module.idna/lib',
    '/home/twilight/.kodi/addons/script.module.urllib3/lib',
    '/home/twilight/.kodi/addons/script.module.requests/lib',
    '/home/twilight/.kodi/addons/script.module.parsers/resources/lib',
    '/home/twilight/.kodi/addons/script.module.unicache/resources/lib',
    '/home/twilight/.kodi/addons/script.common.plugin.cache/resources/lib/storage_server',
    '/home/twilight/.kodi/addons/script.module.netclient/resources/lib',
    '/home/twilight/.kodi/addons/script.module.scrapetube/resources/lib',
    '/home/twilight/.kodi/addons/script.module.fuzzywuzzy/resources/lib',
    '/home/twilight/.kodi/addons/script.module.tulip/resources/lib',
]

for p in addon_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)
