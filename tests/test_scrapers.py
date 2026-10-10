# -*- coding: utf-8 -*-
"""
Tests for scrapers and source makers across AliveGR:
- Live channels parser & schema (live.py)
- Greek-Movies root categories, movie detail, and episodes (source_makers.py, vod.py)
- Music playlists scrapers (music.py)
- Geo IP detection (utils.py)
"""

import unittest
import os
import tests.harness  # noqa: F401 bootstrap mock

from resources.lib.modules.source_makers import gm_source_maker
from resources.lib.indexers.live import Indexer as LiveIndexer
from resources.lib.indexers.vod import Indexer as VodIndexer
from resources.lib.indexers.music import Indexer as MusicIndexer
from resources.lib.modules.constants import GM_BASE, GM_MOVIES, GM_SPORTS, PLAYLIST_BASE
from resources.lib.modules.utils import geo_loc


class TestScrapers(unittest.TestCase):
    """Verifies live scraping functionality against real data sources."""

    def test_live_channels_indexer(self):
        """Scrapes and parses the primary live channels feed."""
        indexer = LiveIndexer()
        data = indexer.live()
        self.assertIsInstance(data, tuple)
        channels, updated = data
        self.assertIsInstance(channels, list)
        self.assertGreater(len(channels), 50)
        self.assertIsInstance(updated, str)

        # Inspect channel item schema
        sample = channels[0]
        self.assertIn('title', sample)
        self.assertIn('group', sample)
        self.assertTrue('url' in sample or 'streams' in sample)

    def test_greek_movies_source_maker_movie(self):
        """Tests scraping a movie page from greek-movies.com."""
        test_url = 'https://greek-movies.com/movies.php?m=6564'
        data = gm_source_maker(test_url)
        self.assertIsInstance(data, dict)
        self.assertIn('title', data)
        self.assertIn('links', data)
        self.assertGreater(len(data['links']), 0)
        # Verify host, url tuple structure
        host, link = data['links'][0]
        self.assertIsInstance(host, str)
        self.assertTrue(link.startswith('https://greek-movies.com/view.php'))

    def test_greek_movies_source_maker_view(self):
        """Tests scraping direct view redirect link on greek-movies.com."""
        test_view_url = 'https://greek-movies.com/view.php?v=MU6o20aQPsCAjGoLJUvJvQ'
        data = gm_source_maker(test_view_url)
        self.assertIsInstance(data, dict)
        self.assertIn('links', data)
        self.assertEqual(len(data['links']), 1)
        self.assertEqual(data['links'][0][1], test_view_url)

    def test_greek_movies_vod_genres(self):
        """Tests VOD root genre category parsing."""
        from resources.lib.indexers.vod import gm_root
        sports_idx = gm_root(GM_SPORTS)
        self.assertIsInstance(sports_idx, str)
        self.assertIn('sports', sports_idx.lower())

    def test_music_playlists_scraper(self):
        """Tests scraping the playlist.gr channel index."""
        from netclient import Net
        import re
        resp = Net().http_GET(PLAYLIST_BASE).content
        html = resp.decode('utf-8') if isinstance(resp, bytes) else resp
        options = re.compile(r'(<option\s+value=.+?</option>)', re.U).findall(html)
        self.assertGreater(len(options), 5)

    def test_geo_ip_detection(self):
        """Tests geo-ip detection resolvers with fallback."""
        country = geo_loc()
        self.assertIsInstance(country, str)
        self.assertGreater(len(country), 0)


if __name__ == '__main__':
    unittest.main()
