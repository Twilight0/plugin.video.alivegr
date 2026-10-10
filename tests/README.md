# AliveGR Test Suite

This test suite provides automated unit and integration tests for **AliveGR** (`plugin.video.alivegr`) running standalone in standard Python outside of a live Kodi instance.

---

## Architecture & Mock Harness

The tests run with `unittest` and utilize [tests/harness.py](file:///home/twilight/Development/repository.twilight0/addons_dir/plugin.video.alivegr/tests/harness.py) to mock the Kodi C/Python bindings (`xbmc`, `xbmcgui`, `xbmcplugin`, `xbmcvfs`, `xbmcaddon`) and `tulip.init`.

Dependencies from local Kodi modules (`script.module.tulip`, `script.module.netclient`, `script.module.parsers`, `script.module.unicache`, `script.common.plugin.cache`) are discovered and dynamically added to `sys.path`.

---

## Test Coverage

| Test Module | Coverage Description |
| :--- | :--- |
| [`test_endpoints.py`](file:///home/twilight/Development/repository.twilight0/addons_dir/plugin.video.alivegr/tests/test_endpoints.py) | Verifies reachability, HTTP status, and payload formats for all primary endpoints: Remote Live Channels JSON gist, Greekstreamtv fallback M3U, Greek EPG XML archive, Greek-Movies base, Playlist.gr base, and project URLs. |
| [`test_scrapers.py`](file:///home/twilight/Development/repository.twilight0/addons_dir/plugin.video.alivegr/tests/test_scrapers.py) | Verifies active web scrapers: `live.Indexer.live()` channels list, `gm_source_maker` movie detail & view redirect scrapers, `gm_root` VOD genres, playlist options extraction from `playlist.gr`, and `geo_loc()` IP geolocation fallback. |
| [`test_iptv.py`](file:///home/twilight/Development/repository.twilight0/addons_dir/plugin.video.alivegr/tests/test_iptv.py) | Verifies IPTV Simple Client integration: channel name to XMLTV ID mapping (`resolve_tvg_id`), stream formatting (`format_stream_for_m3u`) with `#KODIPROP` directives for direct HLS and ClearKey DRM MPD, and `generate_m3u_playlist`. |
| [`test_storage_prefs.py`](file:///home/twilight/Development/repository.twilight0/addons_dir/plugin.video.alivegr/tests/test_storage_prefs.py) | Tests plain-text line-based storage helper (`TextListStorage` in `storage.py`), CRUD operations, FIFO item trimming, and stream preference matching (`get_stream_pref`). |
| [`test_strings_settings.py`](file:///home/twilight/Development/repository.twilight0/addons_dir/plugin.video.alivegr/tests/test_strings_settings.py) | Verifies catalog integrity: ensures both `el_GR` and `en_GB` `strings.po` files exist, contain matching string IDs, and that all numeric labels/headings in `settings.xml` exist in `strings.po`. |

---

## How to Run

### Run All Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### Run Individual Test Modules
```bash
# Endpoints and URL reachability:
python3 -m unittest tests/test_endpoints.py

# Live TV, Greek-Movies & music scrapers:
python3 -m unittest tests/test_scrapers.py

# IPTV Simple Client M3U generator & EPG mappings:
python3 -m unittest tests/test_iptv.py

# Plain-text storage and stream preference matching:
python3 -m unittest tests/test_storage_prefs.py

# strings.po catalogs and settings.xml integrity:
python3 -m unittest tests/test_strings_settings.py
```
