# -*- coding: utf-8 -*-
"""
Tests for stream preferences, plain-text storage, and channel schema logic.
"""

import unittest
import os
import tempfile
import tests.harness  # noqa: F401 bootstrap mock

from resources.lib.modules.storage import TextListStorage
from resources.lib.modules.utils import get_stream_pref, set_stream_pref, get_all_stream_prefs


class TestPreferencesAndStorage(unittest.TestCase):
    """Verifies storage persistence and stream preferences matching."""

    def test_text_list_storage_lifecycle(self):
        """Tests add, duplicate prevention, FIFO trimming, and remove."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tf:
            fpath = tf.name

        try:
            store = TextListStorage(fpath, max_items=3)
            self.assertEqual(store.get_all(), [])

            store.add('entry 1')
            store.add('entry 2')
            store.add('entry 3')
            self.assertEqual(store.get_all(), ['entry 1', 'entry 2', 'entry 3'])
            self.assertEqual(store.get_reversed(), ['entry 3', 'entry 2', 'entry 1'])

            # Ignore duplicate
            store.add('entry 2')
            self.assertEqual(store.get_all(), ['entry 1', 'entry 2', 'entry 3'])

            # Trim on overflow
            store.add('entry 4')
            self.assertEqual(store.get_all(), ['entry 2', 'entry 3', 'entry 4'])

            # Replace
            store.replace('entry 3', 'entry 3_updated')
            self.assertEqual(store.get_all(), ['entry 2', 'entry 3_updated', 'entry 4'])

            # Remove
            store.remove('entry 2')
            self.assertEqual(store.get_all(), ['entry 3_updated', 'entry 4'])

            # Clear
            store.clear()
            self.assertEqual(store.get_all(), [])
        finally:
            if os.path.exists(fpath):
                os.remove(fpath)

    def test_stream_preference_matching(self):
        """Tests fuzzy and normalized channel title preference matching."""
        prefs = {
            'Mega': 1,
            'ERT 1': 2,
            'Cosmote Sport 1': 0
        }

        # Exact match
        self.assertEqual(get_stream_pref('Mega', prefs), 1)
        # Case insensitive match
        self.assertEqual(get_stream_pref('mega', prefs), 1)
        self.assertEqual(get_stream_pref('ert 1', prefs), 2)
        # Not found fallback
        self.assertIsNone(get_stream_pref('NonExistentChannel', prefs))


if __name__ == '__main__':
    unittest.main()
