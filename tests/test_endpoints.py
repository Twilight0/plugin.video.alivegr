# -*- coding: utf-8 -*-
"""
Tests for endpoints, URLs, and network connectivity in AliveGR.
"""

import unittest
import urllib.request
import json
import base64

import tests.harness  # noqa: F401 bootstrap Kodi mock

from resources.lib.modules.constants import (
    ALIVEGR, M3U_LINK, GM_BASE, PLAYLIST_BASE, GREEK_EPG_XML,
    WEBSITE, ALIVEGR_WEB, PATREON, KOFI, PAYPAL
)
from resources.lib.modules.utils import thgiliwt


class TestEndpoints(unittest.TestCase):
    """Verifies that all primary external URLs and endpoints defined in constants are valid."""

    def _check_url(self, url, timeout=10, min_bytes=10):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (AliveGR TestSuite)'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            self.assertEqual(resp.status, 200, f"URL {url} returned non-200 status: {resp.status}")
            data = resp.read()
            self.assertGreaterEqual(len(data), min_bytes, f"URL {url} returned insufficient data")
            return data

    def test_live_json_endpoint(self):
        """Test the remote Live Channels JSON gist."""
        raw_url = thgiliwt('=' + ALIVEGR)
        live_json_url = raw_url.decode('utf-8') if isinstance(raw_url, bytes) else raw_url
        self.assertTrue(live_json_url.startswith('https://'))
        raw_data = self._check_url(live_json_url, min_bytes=50000)
        parsed = json.loads(raw_data.decode('utf-8'))
        self.assertIn('channels', parsed)
        self.assertGreater(len(parsed['channels']), 50)
        self.assertIn('updated', parsed)

    def test_greekstreamtv_m3u(self):
        """Test the fallback Greekstreamtv M3U endpoint."""
        raw = self._check_url(M3U_LINK, min_bytes=5000)
        text = raw.decode('utf-8', errors='ignore')
        self.assertTrue(text.startswith('#EXTM3U'))

    def test_epg_xml(self):
        """Test the remote Greek EPG XML archive."""
        raw = self._check_url(GREEK_EPG_XML, min_bytes=100000)
        self.assertGreater(len(raw), 100000)

    def test_greek_movies_base(self):
        """Test greek-movies.com base reachability."""
        self._check_url(GM_BASE, min_bytes=1000)

    def test_playlist_gr_base(self):
        """Test playlist.gr base reachability."""
        self._check_url(PLAYLIST_BASE, min_bytes=1000)

    def test_metadata_links(self):
        """Test project info and patron URLs."""
        for name, url in [('AliveGR Web', ALIVEGR_WEB), ('GitHub Repo', WEBSITE)]:
            with self.subTest(name=name, url=url):
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    self.assertIn(resp.status, (200, 301, 302))


if __name__ == '__main__':
    unittest.main()
