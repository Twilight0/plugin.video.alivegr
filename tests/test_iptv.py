# -*- coding: utf-8 -*-
"""
Tests for IPTV Simple Client M3U playlist generation and formatting logic.
"""

import unittest
import os
import tempfile
import tests.harness  # noqa: F401 bootstrap mock

from resources.lib.modules.iptv import (
    resolve_tvg_id, format_stream_for_m3u, generate_m3u_playlist
)
from resources.lib.modules.constants import ALIVEGR_M3U


class TestIPTVGeneration(unittest.TestCase):
    """Verifies M3U generation, EPG mapping, and DRM stream formatting."""

    def test_resolve_tvg_id_known_channels(self):
        """Tests that common Greek channels map to proper EPG XMLTV IDs."""
        self.assertEqual(resolve_tvg_id('Mega'), 'mega')
        self.assertEqual(resolve_tvg_id('ANT1'), 'ant1')
        self.assertEqual(resolve_tvg_id('Alpha TV'), 'alpha')
        self.assertEqual(resolve_tvg_id('Star Channel'), 'star')
        self.assertEqual(resolve_tvg_id('ERT 1'), 'ert1')
        self.assertEqual(resolve_tvg_id('Open TV'), 'open')
        self.assertEqual(resolve_tvg_id('Discovery Channel'), 'Discoverychannel')

    def test_format_direct_hls_stream(self):
        """Tests format_stream_for_m3u with a plain HLS stream."""
        stream_entry = "https://example.com/live/stream.m3u8|User-Agent=AliveGR"
        final_url, kodi_props = format_stream_for_m3u(stream_entry, proxy_port=None)
        self.assertIn("https://example.com/live/stream.m3u8", final_url)
        self.assertTrue(any("inputstream.adaptive" in prop for prop in kodi_props))

    def test_format_dash_clearkey_stream(self):
        """Tests format_stream_for_m3u with MPD and ClearKey DRM dict."""
        stream_entry = {
            'url': 'https://example.com/live/manifest.mpd',
            'drm': ['org.w3.clearkey', {'0123456789abcdef0123456789abcdef': 'fedcba9876543210fedcba9876543210'}]
        }
        final_url, kodi_props = format_stream_for_m3u(stream_entry, proxy_port=None)
        self.assertIn("manifest.mpd", final_url)
        has_clearkey_prop = any("clearkey" in p.lower() or "drm" in p.lower() or "license_key" in p.lower() for p in kodi_props)
        self.assertTrue(has_clearkey_prop)

    def test_generate_m3u_playlist_output(self):
        """Tests generate_m3u_playlist writing valid #EXTM3U file."""
        mock_channels = [
            {
                'title': 'ERT 1',
                'group': 'Πανελλαδικά',
                'icon': 'https://example.com/ert1.png',
                'streams': ['https://ert.example.com/ert1.m3u8']
            },
            {
                'title': 'Mega',
                'group': 'Πανελλαδικά',
                'icon': 'https://example.com/mega.png',
                'streams': ['https://mega.example.com/live.m3u8']
            }
        ]

        result = generate_m3u_playlist(channels=mock_channels)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(ALIVEGR_M3U))

        with open(ALIVEGR_M3U, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertTrue(content.startswith('#EXTM3U'))
        self.assertIn('tvg-name="ERT 1"', content)
        self.assertIn('tvg-name="Mega"', content)
        self.assertIn('group-title="Πανελλαδικά"', content)
        self.assertIn('#EXTINF:-1', content)


if __name__ == '__main__':
    unittest.main()
