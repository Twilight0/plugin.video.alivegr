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


    def test_frontpages_parser(self):
        """Verifies parsing of frontpages.gr HTML structure."""
        from domparsers import parseDOM
        from urllib.parse import urljoin

        sample_html = '''
        <div id="General" class="tabbertab">
            <div class="thumber" style="display:inline-block;">
                <div class="paperInfo"><span>Sample Headline</span></div>
                <div class="paperName"><a href="/protoselida/1/Sample">Sample Paper</a></div>
                <a class="coverPageLink" href="/protoselida/20261012/1/Sample">
                    <img src="/data/2026/20261012/Sample300.jpg" alt="Sample Alt" />
                </a>
                <button class="coverZoomButton" data-full-src="/data/2026/20261012/SampleI.jpg"></button>
            </div>
        </div>
        <div id="Magazines" class="tabbertab">
            <div class="thumber">
                <div class="paperName">Magazine One</div>
                <img src="/data/2026/20261012/Mag300.jpg" alt="Mag One" />
            </div>
        </div>
        '''

        fp_link = 'https://www.frontpages.gr'
        groups = parseDOM(sample_html, 'div', attrs={'class': 'tabbertab'})
        self.assertEqual(len(groups), 2)

        items = []
        for group, papers in enumerate(groups):
            thumbers = parseDOM(papers, 'div', attrs={'class': 'thumber'})
            for i in thumbers:
                btn = parseDOM(i, 'button', attrs={'class': 'coverZoomButton'}, ret='data-full-src')
                imgs = parseDOM(i, 'img', ret='src')
                self.assertTrue(bool(imgs))
                image = urljoin(fp_link, imgs[0])
                if btn and btn[0]:
                    link = urljoin(fp_link, btn[0])
                else:
                    link = image.replace('300.jpg', 'I.jpg')

                paper_names = parseDOM(i, 'div', attrs={'class': 'paperName'})
                if paper_names:
                    links = parseDOM(paper_names[0], 'a')
                    title = links[0] if links else paper_names[0]
                else:
                    title = 'Fallback'
                items.append({'title': title, 'image': image, 'url': link, 'group': group})

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['title'], 'Sample Paper')
        self.assertEqual(items[0]['url'], 'https://www.frontpages.gr/data/2026/20261012/SampleI.jpg')
        self.assertEqual(items[0]['group'], 0)
        self.assertEqual(items[1]['title'], 'Magazine One')
        self.assertEqual(items[1]['url'], 'https://www.frontpages.gr/data/2026/20261012/MagI.jpg')
        self.assertEqual(items[1]['group'], 1)


if __name__ == '__main__':
    unittest.main()
