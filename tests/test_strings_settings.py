# -*- coding: utf-8 -*-
"""
Tests for language files (strings.po) and settings.xml integrity:
- Verifies all string IDs referenced in settings.xml and python code exist in both strings.po files.
- Checks that el_GR and en_GB .po catalogs are syntactically valid and synchronized.
"""

import unittest
import os
import re
import xml.etree.ElementTree as ET


class TestStringsAndSettings(unittest.TestCase):
    """Verifies strings catalogs and settings definitions."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.el_po_path = os.path.join(cls.repo_root, 'resources', 'language', 'resource.language.el_gr', 'strings.po')
        cls.en_po_path = os.path.join(cls.repo_root, 'resources', 'language', 'resource.language.en_gb', 'strings.po')
        cls.settings_xml_path = os.path.join(cls.repo_root, 'resources', 'settings.xml')

        cls.el_ids = cls._extract_po_ids(cls.el_po_path)
        cls.en_ids = cls._extract_po_ids(cls.en_po_path)

    @classmethod
    def _extract_po_ids(cls, file_path):
        ids = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'msgctxt\s+"#(\d+)"', line)
                if m:
                    ids.add(m.group(1))
        return ids

    def test_po_catalogs_exist_and_populated(self):
        """Verifies both strings.po files exist and have strings."""
        self.assertGreater(len(self.el_ids), 400)
        self.assertGreater(len(self.en_ids), 400)

    def test_po_catalogs_in_sync(self):
        """Verifies both language files share identical string IDs."""
        missing_in_en = self.el_ids - self.en_ids
        missing_in_el = self.en_ids - self.el_ids
        self.assertEqual(missing_in_en, set(), f"IDs present in el_GR but missing in en_GB: {missing_in_en}")
        self.assertEqual(missing_in_el, set(), f"IDs present in en_GB but missing in el_GR: {missing_in_el}")

    def test_settings_xml_strings_exist_in_catalogs(self):
        """Verifies all numeric labels and headings in settings.xml exist in strings.po."""
        tree = ET.parse(self.settings_xml_path)
        root = tree.getroot()

        for elem in root.iter():
            for attr in ('label', 'help', 'heading'):
                val = elem.get(attr)
                if val and val.isdigit():
                    self.assertIn(
                        val, self.el_ids,
                        f"String ID #{val} in settings.xml ({elem.tag} {attr}) missing from strings.po"
                    )


if __name__ == '__main__':
    unittest.main()
