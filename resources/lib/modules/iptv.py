# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

"""
IPTV Simple Client Bridge Module.
Generates an M3U playlist with stream fallbacks and proxy handling for pvr.iptvsimple,
configures the binary addon, and opens native Kodi PVR windows.
"""

import os
import re
import json
import base64
from urllib.parse import urlencode, parse_qsl, unquote
from xbmcaddon import Addon
from tulip import kodi
from tulip.log import log
from .constants import ALIVEGR_M3U, GREEK_EPG_XML, LIVE_GROUPS

IPTVSIMPLE_ID = 'pvr.iptvsimple'
PROXY_PORT = 50199
PLUGINSGR_ID = 'script.module.resolveurl.pluginsgr'

EPG_CHANNEL_MAP = {
    'ert 1': 'ert1',
    'ert 2 sports': 'ert2',
    'ert 2': 'ert2',
    'ert 3': 'ert3',
    'mega': 'mega',
    'mega news': 'meganews',
    'mega cosmos': 'megacosmos',
    'ant1': 'ant1',
    'ant1 comedy': 'Ant1 Comedy',
    'ant1 drama': 'Ant1 Drama',
    'ant1 europe': 'ant1europe',
    'ant1 pacific': 'ant1pacific',
    'ant1 satellite': 'ant1sat',
    'alpha': 'alpha',
    'alpha cyprus': 'alphacy',
    'alpha sat': 'alphasatusa',
    'star': 'star',
    'star international': 'starint',
    'star central greece': 'starke',
    'star k. ellados': 'starke',
    'star kentrikis ellados': 'starke',
    'open beyond': 'open',
    'open': 'open',
    'makedonia tv': 'mtv',
    'maktv': 'mtv',
    'mak tv': 'mtv',
    'm.tv': 'mtv',
    'vouli': 'vouli',
    'ert news': 'ertnews',
    'ert sports': 'ertsports',
    'ert sports 1': 'ertsports',
    'ert sports 2': 'ertsports2',
    'ert sports 3': 'ertsports3',
    'ert sports 4': 'ertsports4',
    'ert sports 5': 'ertsports5',
    'ert world': 'ertworld',
    'action 24': 'action24',
    'kontra': 'kontra',
    'kontra channel': 'kontra',
    'one channel': 'onetv',
    'one': 'onetv',
    'naftemporiki': 'Naftemporikitv',
    'naftemporiki tv': 'Naftemporikitv',
    'vergina': 'berginatv',
    'vergina tv': 'berginatv',
    'vergina cy': 'berginacy',
    'aeolos tv': 'aeolos',
    'aeolos': 'aeolos',
    'kriti tv': 'krititv1',
    'tile kriti': 'thlekriti',
    'nea tileorasi kritis': 'neatvcrete',
    'nea tv kritis': 'neatvcrete',
    'blue sky': 'bluesky',
    'alert': 'alert',
    'alert tv': 'alert',
    'attica tv': 'atticatv',
    'attica': 'atticatv',
    'best tv': 'besttv',
    'best': 'besttv',
    'center tv': 'centertv',
    'center': 'centertv',
    'dion tv': 'diontv',
    'dion': 'diontv',
    'ena channel': 'enachannel',
    'ena tv': 'enachannel',
    'epirus tv1': 'epirustv1',
    'ionian': 'ionian',
    'ionian tv': 'ionian',
    'lepanto': 'lepanto',
    'lepanto tv': 'lepanto',
    'lychnos': 'lychnos',
    'mad tv': 'madtv',
    'mad greekz': 'MAD GreekZ',
    'mad viral': 'MAD Viral HD',
    'mad viral hd': 'MAD Viral HD',
    'next tv': 'nexttv',
    'nickelodeon': 'nickelodeon',
    'nickelodeon plus': 'nickelodeonplus',
    'omega': 'omega',
    'omega tv': 'omega',
    'rik 1': 'rik1',
    'rik 2': 'rik2',
    'rik hd': 'rikhd',
    'rik sat': 'riksat',
    'rise tv': 'risetv',
    'rise': 'risetv',
    'sigma': 'sigma',
    'sigma tv': 'sigma',
    'smile': 'smile',
    'smile tv': 'smile',
    'smile tv cy': 'smile tv cy',
    'tv 100': 'tv100',
    'tv rodopi': 'tvrodopi',
    'achaia channel': 'achaiachannel',
    'alithia tv': 'alithiatv',
    'alfa tv': 'alfa',
    'anet': 'anet',
    'art': 'art',
    'art tv': 'arttv',
    'astra tv': 'astratv',
    'atlas tv': 'atlastv',
    'capital tv': 'capitaltv',
    'corfu tv': 'corfutv',
    'creta tv': 'creta',
    'creta': 'creta',
    'delta tv': 'deltatv',
    'diktyo tv': 'diktyotv',
    'diktyo 1': 'diktyo1',
    'epiloges tv': 'tileepiloges',
    'euro tv': 'eurotv',
    'extra channel': 'extrachannel',
    'flash tv': 'flashtv',
    'formediatv': 'formediatv',
    'gnomi tv': 'gnomitv',
    'high tv': 'hightv',
    'irida tv': 'iridatv',
    'itv': 'itv',
    'kosmos tv': 'kosmos',
    'kos tv': 'kostv',
    'krhth tv': 'krhthtv',
    'mesogeios tv': 'mesogeiostv',
    'notos tv': 'notostv',
    'orestiada tv': 'orestiadatv',
    'patra tv': 'patratv',
    'patrida tv': 'patridatv',
    'pella tv': 'pellatv',
    'plus tv': 'plustv',
    'pronews tv': 'pronews',
    'pronews': 'pronews',
    'rtp kentro': 'rtpkentro',
    'samia ki tv': 'samiakitv',
    'sitiatv': 'sitiatv',
    'super tv': 'super',
    'syros tv1': 'syrostv1',
    'tharri tv': 'tharri',
    'thessalia tv': 'thessaliatv',
    'thrakinet': 'thrakinet',
    'top channel': 'topchannel',
    'trt': 'trt',
    'vima tv': 'vimatv',
    'volcano tv': 'volcano',
    'west channel': 'westchannel',
    'discovery channel': 'Discoverychannel',
    'animal planet': 'AnimalPlanet',
    'disney channel': 'Disney Channel',
    'disney junior': 'Disney Junior',
    'cartoon network': 'Cartoon Network',
    'cartoonito': 'Cartoonito',
    'tlc': 'TLC',
    'cnn': 'CNN',
    'bbc news': 'BBC News',
    'dw': 'DW',
    'al jazeera': 'Al Jazeera',
    'euronews greek': 'Euronews Greek',
    'euronews': 'Euronews Greek',
}


def resolve_tvg_id(name):
    """Maps channel name to official Greek EPG XMLTV ID."""
    low = name.lower().strip()
    if low in EPG_CHANNEL_MAP:
        return EPG_CHANNEL_MAP[low]
    clean_punct = low.replace(' tv', '').replace(' channel', '').strip()
    if clean_punct in EPG_CHANNEL_MAP:
        return EPG_CHANNEL_MAP[clean_punct]
    clean = low.replace(' ', '').replace('-', '').replace('_', '')
    if clean in EPG_CHANNEL_MAP:
        return EPG_CHANNEL_MAP[clean]
    return name.strip()


def get_proxy_port():
    try:
        p = Addon(PLUGINSGR_ID).getSetting('proxy_port')
        if p and p.isdigit():
            return int(p)
    except Exception:
        pass
    return PROXY_PORT


def is_iptvsimple_installed():
    """Checks whether pvr.iptvsimple is present on the filesystem or registered in Kodi."""
    if kodi.conditional_visibility(f'System.HasAddon({IPTVSIMPLE_ID})'):
        return True

    xbmc_path = kodi.join('special://xbmc', 'addons', IPTVSIMPLE_ID)
    home_path = kodi.join('special://home', 'addons', IPTVSIMPLE_ID)
    try:
        if os.path.exists(kodi.transPath(xbmc_path)) or os.path.exists(kodi.transPath(home_path)):
            return True
    except Exception:
        pass

    return False


def is_iptvsimple_enabled():
    """Checks whether pvr.iptvsimple is enabled via json-rpc."""
    try:
        details = kodi.addon_details(IPTVSIMPLE_ID)
        return bool(details.get('enabled'))
    except Exception:
        return False


def enable_iptvsimple():
    """Enables pvr.iptvsimple via json-rpc."""
    try:
        kodi.enable_addon(IPTVSIMPLE_ID, True)
        return True
    except Exception as e:
        log(f'Failed to enable {IPTVSIMPLE_ID}: {e}')
        return False


def install_or_prompt_iptvsimple():
    """
    Attempts to install or guides the user on installing pvr.iptvsimple.
    Returns:
        True if installed and available, False otherwise.
    """
    if is_iptvsimple_installed():
        if not is_iptvsimple_enabled():
            enable_iptvsimple()
        return True

    # Linux distributions (Garuda/Arch/Debian/Ubuntu/Fedora etc.) need package manager installation
    is_linux = False
    if not kodi.conditional_visibility('System.Platform.Android'):
        if kodi.conditional_visibility('System.Platform.Linux'):
            is_linux = True
        elif os.path.exists('/etc/os-release'):
            is_linux = True

    if is_linux:
        # Check if LibreELEC / CoreELEC (which can install binary addons via Kodi repository)
        is_elec = False
        if os.path.exists('/etc/os-release'):
            try:
                with open('/etc/os-release', 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(dist in content for dist in ['libreelec', 'coreelec']):
                        is_elec = True
            except Exception:
                pass

        if not is_elec:
            msg = kodi.i18n(30323)
            # Add specific package suggestion
            pkg_hint = "\n\nArch/Garuda: sudo pacman -S kodi-addon-pvr-iptvsimple\nDebian/Ubuntu: sudo apt install kodi-pvr-iptvsimple"
            kodi.okDialog(heading=kodi.name(), line1=msg + pkg_hint)
            return False

    # Try Kodi GUI install for Android / Windows / LibreELEC
    kodi.execute(f'InstallAddon({IPTVSIMPLE_ID})')
    kodi.sleep(1500)

    if is_iptvsimple_installed():
        if not is_iptvsimple_enabled():
            enable_iptvsimple()
        return True

    return False


def format_stream_for_m3u(stream_entry, proxy_port):
    """
    Analyzes a channel stream string or dict and generates:
    1. KODIPROP headers (#KODIPROP:...)
    2. Playable Stream URL (direct or proxied through PluginsGR localhost HTTP proxy)
    """
    props = []
    stream_url = ''
    headers = {}
    drm = None

    if isinstance(stream_entry, dict):
        stream_url = stream_entry.get('url', '')
        headers = dict(stream_entry.get('headers') or {})
        drm = stream_entry.get('drm')
    elif isinstance(stream_entry, str):
        if '|' in stream_entry:
            parts = stream_entry.split('|', 1)
            stream_url = parts[0]
            try:
                for k, v in parse_qsl(parts[1]):
                    if k == 'DRM':
                        try:
                            drm = json.loads(v)
                        except Exception:
                            pass
                    else:
                        headers[k] = v
            except Exception:
                pass
        else:
            stream_url = stream_entry

    if not stream_url:
        return None, []

    # Case 1: ClearKey DRM
    if drm:
        props.append('#KODIPROP:inputstream=inputstream.adaptive')
        props.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
        props.append('#KODIPROP:inputstream.adaptive.mimetype=application/dash+xml')
        try:
            lic_type = drm[0]
            lic_key = drm[1] if isinstance(drm[1], str) else json.dumps(drm[1])
            props.append(f'#KODIPROP:inputstream.adaptive.license_type={lic_type}')
            props.append(f'#KODIPROP:inputstream.adaptive.license_key={lic_key}')
        except Exception:
            pass
        return stream_url, props

    # Case 2: Custom HTTP Headers (Referer, User-Agent, Roku tokens, etc.)
    # Pass headers directly to inputstream.adaptive so both manifest and all TS segments receive them
    if headers:
        props.append('#KODIPROP:inputstream=inputstream.adaptive')
        if '.mpd' in stream_url:
            props.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
            props.append('#KODIPROP:inputstream.adaptive.mimetype=application/dash+xml')
        else:
            props.append('#KODIPROP:inputstream.adaptive.manifest_type=hls')
            props.append('#KODIPROP:inputstream.adaptive.mimetype=application/vnd.apple.mpegurl')

        h_str = urlencode(headers)
        props.append(f'#KODIPROP:inputstream.adaptive.manifest_headers={h_str}')
        props.append(f'#KODIPROP:inputstream.adaptive.stream_headers={h_str}')
        return stream_url, props

    # Case 3: Direct DASH (.mpd)
    if '.mpd' in stream_url:
        props.append('#KODIPROP:inputstream=inputstream.adaptive')
        props.append('#KODIPROP:inputstream.adaptive.manifest_type=mpd')
        props.append('#KODIPROP:inputstream.adaptive.mimetype=application/dash+xml')
        return stream_url, props

    # Case 4: Direct HLS (.m3u8)
    if '.m3u8' in stream_url:
        props.append('#KODIPROP:inputstream=inputstream.adaptive')
        props.append('#KODIPROP:inputstream.adaptive.manifest_type=hls')
        props.append('#KODIPROP:inputstream.adaptive.mimetype=application/vnd.apple.mpegurl')
        return stream_url, props

    # Case 5: Other direct playable URLs (HTTP streams, MP4, FLV)
    return stream_url, props


def generate_m3u_playlist(channels=None):
    """
    Builds the full alivegr.m3u playlist file from current live channel data.
    """
    if channels is None:
        from ..indexers.live import Indexer as LiveIndexer
        channels, _ = LiveIndexer().live()

    if not channels:
        log('IPTV Simple Bridge: No channels available to generate M3U.')
        return False

    proxy_port = get_proxy_port()
    from .utils import get_all_stream_prefs, get_stream_pref
    stream_prefs = get_all_stream_prefs()

    # Invert LIVE_GROUPS mapping for clean Greek/English group title lookup
    group_map = {}
    for eng_k, str_id in LIVE_GROUPS.items():
        try:
            group_map[str(str_id)] = kodi.i18n(str_id)
        except Exception:
            group_map[str(str_id)] = eng_k

    lines = [
        f'#EXTM3U x-tvg-url="{GREEK_EPG_XML}"'
    ]

    for ch in channels:
        name = ch.get('name') or ch.get('title') or 'Unknown'
        logo = ch.get('logo') or ch.get('image') or ''
        raw_group = str(ch.get('group', ''))
        group_title = group_map.get(raw_group, raw_group or 'General')

        streams = ch.get('streams') or []
        if isinstance(streams, str):
            try:
                streams = json.loads(streams)
            except Exception:
                streams = [streams] if streams else []

        if not streams and ch.get('url'):
            streams = [ch['url']]

        if not streams:
            continue

        # Choose the user-preferred stream if selected in Live TV section, otherwise default to first
        pref_idx = get_stream_pref(name, stream_prefs)
        if pref_idx is not None and isinstance(pref_idx, int) and 0 <= pref_idx < len(streams):
            stream_entry = streams[pref_idx]
        else:
            stream_entry = streams[0]

        final_url, props = format_stream_for_m3u(stream_entry, proxy_port)

        if not final_url:
            continue

        # tvg-id matching: use mapped XMLTV channel ID for Greek EPG
        tvg_id = resolve_tvg_id(name)

        extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group_title}",{name}'
        lines.append(extinf)
        for p in props:
            lines.append(p)
        lines.append(final_url)

    m3u_path = kodi.transPath(ALIVEGR_M3U)
    m3u_dir = os.path.dirname(m3u_path)
    if not os.path.exists(m3u_dir):
        os.makedirs(m3u_dir, exist_ok=True)

    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    log(f'IPTV Simple Bridge: Wrote {len(channels)} channels to {m3u_path}')
    return True


def configure_iptvsimple_settings():
    """Configures pvr.iptvsimple settings to consume AliveGR's generated M3U & EPG.
    Supports both legacy global settings.xml and modern multi-instance configurations (instance-settings-*.xml).
    """
    m3u_path = kodi.transPath(ALIVEGR_M3U)
    configured = False

    # 1. Update instance configuration files (Kodi 20+ multi-instance presets)
    instance_dir = kodi.transPath(f'special://userdata/addon_data/{IPTVSIMPLE_ID}')
    if os.path.exists(instance_dir):
        import glob
        import xml.etree.ElementTree as ET

        instance_files = glob.glob(os.path.join(instance_dir, 'instance-settings-*.xml'))
        if not instance_files:
            # If no instance file exists yet, create instance-settings-1.xml as default instance
            default_inst = os.path.join(instance_dir, 'instance-settings-1.xml')
            initial_content = (
                '<settings version="2">\n'
                '    <setting id="kodi_addon_instance_name">AliveGR IPTV</setting>\n'
                '    <setting id="kodi_addon_instance_enabled">true</setting>\n'
                f'    <setting id="m3uPathType">0</setting>\n'
                f'    <setting id="m3uPath">{m3u_path}</setting>\n'
                '    <setting id="m3uCache">true</setting>\n'
                '    <setting id="epgPathType">1</setting>\n'
                f'    <setting id="epgUrl">{GREEK_EPG_XML}</setting>\n'
                '    <setting id="epgCache">true</setting>\n'
                '</settings>\n'
            )
            try:
                with open(default_inst, 'w', encoding='utf-8') as f:
                    f.write(initial_content)
                instance_files = [default_inst]
                configured = True
            except Exception as e:
                log(f'Failed to create default instance settings file: {e}')

        for inst_file in instance_files:
            try:
                tree = ET.parse(inst_file)
                root = tree.getroot()
                updates = {
                    'kodi_addon_instance_name': 'AliveGR IPTV',
                    'm3uPathType': '0',
                    'm3uPath': m3u_path,
                    'epgPathType': '1',
                    'epgUrl': GREEK_EPG_XML,
                    'm3uCache': 'true',
                    'epgCache': 'true',
                    'kodi_addon_instance_enabled': 'true'
                }
                found_keys = set()
                for s in root.findall('setting'):
                    sid = s.get('id')
                    if sid in updates:
                        s.text = updates[sid]
                        if 'default' in s.attrib:
                            del s.attrib['default']
                        found_keys.add(sid)

                # Add missing keys if not present
                for sid, val in updates.items():
                    if sid not in found_keys:
                        new_elem = ET.SubElement(root, 'setting', {'id': sid})
                        new_elem.text = val

                ET.indent(tree, space='    ')
                tree.write(inst_file, encoding='utf-8', xml_declaration=False)
                configured = True
            except Exception as e:
                log(f'Failed updating instance settings {inst_file}: {e}')

    # 2. Also write via Addon API for global/legacy compatibility
    try:
        iptv_addon = Addon(IPTVSIMPLE_ID)
        # 0 = Local path
        iptv_addon.setSetting('m3uPathType', '0')
        iptv_addon.setSetting('m3uPath', m3u_path)

        # 1 = Remote URL for EPG
        iptv_addon.setSetting('epgPathType', '1')
        iptv_addon.setSetting('epgUrl', GREEK_EPG_XML)

        try:
            iptv_addon.setSetting('m3uCache', 'true')
            iptv_addon.setSetting('epgCache', 'true')
        except Exception:
            pass

        configured = True
    except Exception as e:
        log(f'Writing to {IPTVSIMPLE_ID} via Addon API: {e}')

    return configured


def restart_pvr_manager():
    """Triggers Kodi to reload PVR channels and restart the PVR manager."""
    try:
        kodi.execute('StartPVRManager')
        kodi.execute('PVR.Restart')
    except Exception:
        pass


def setup_iptv(notify=True):
    """
    Main setup wizard for IPTV Simple Client bridge.
    1. Installs/verifies pvr.iptvsimple
    2. Generates alivegr.m3u with proxied headers & DRM
    3. Configures pvr.iptvsimple settings & multi-instance presets
    4. Enables show_pvr in AliveGR settings
    5. Restarts PVR manager
    """
    installed = install_or_prompt_iptvsimple()
    if not installed:
        return False

    with kodi.WorkingDialog():
        generated = generate_m3u_playlist()
        if not generated:
            kodi.infoDialog('Failed to generate M3U playlist', heading=kodi.name(), time=3000)
            return False

        configured = configure_iptvsimple_settings()
        if not configured:
            kodi.infoDialog('Failed to configure IPTV Simple settings', heading=kodi.name(), time=3000)
            return False

        # Enable show_pvr shortcut in AliveGR settings
        kodi.setSetting('show_pvr', 'true')

        restart_pvr_manager()

    if notify:
        kodi.infoDialog(kodi.i18n(30402), heading=kodi.name(), time=3000)
        kodi.refresh()

    return True


def launch_or_setup():
    """
    Handles clicking the 'IPTV Simple Client' menu item in AliveGR:
    Directly opens Kodi's native Live TV / Channels window.
    """
    kodi.execute('ActivateWindow(tvchannels)')

