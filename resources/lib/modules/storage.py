# -*- coding: utf-8 -*-

# AliveGR Addon
# Author Twilight0
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSES/GPL-3.0-only for more information.

from os import path
from tulip import kodi


class TextListStorage:
    """
    Encapsulates line-based plain-text storage (e.g. pinned items, history).
    Ensures safe creation, UTF-8 reading/writing, and list trimming.
    """

    def __init__(self, filepath, max_items=None):
        self.filepath = filepath
        self.max_items = max_items

    def _ensure_dir(self):
        dir_path = path.dirname(self.filepath)
        if dir_path and not kodi.exists(dir_path):
            kodi.makeFiles(dir_path)

    def get_all(self):
        """
        Reads all non-empty lines from the file in chronological order (as written).
        :return: list of strings
        """
        if not kodi.exists(self.filepath):
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return [line.rstrip('\r\n') for line in f if line.rstrip('\r\n')]
        except Exception:
            return []

    def get_reversed(self):
        """
        Reads all items reversed (newest first), matching the historical
        behavior of read_from_file and pinned_from_file.
        :return: list of strings
        """
        return self.get_all()[::-1]

    def add(self, item, trim=True):
        """
        Appends an item to the list if not already present.
        :param item: string
        :param trim: bool, whether to apply max_items limit
        """
        if not item:
            return

        items = self.get_all()
        if item in items:
            return

        items.append(item)
        self._write(items, trim=trim)

    def remove(self, item):
        """
        Removes an item from the file if present.
        :param item: string
        """
        items = self.get_all()
        if item in items:
            items.remove(item)
            self._write(items, trim=False)

    def replace(self, old_item, new_item):
        """
        Replaces old_item with new_item in place, preserving order.
        """
        if not old_item or not new_item:
            return False

        items = self.get_all()
        if old_item in items:
            idx = items.index(old_item)
            items[idx] = new_item
            self._write(items, trim=False)
            return True
        return False

    def clear(self):
        """Clears all entries in the storage file."""
        self._write([], trim=False)

    def trim(self):
        """Trims file to max_items if configured."""
        if self.max_items:
            items = self.get_all()
            if len(items) > self.max_items:
                self._write(items, trim=True)

    def _write(self, items, trim=True):
        self._ensure_dir()
        if trim and self.max_items and len(items) > self.max_items:
            items = items[-self.max_items:]

        with open(self.filepath, 'w', encoding='utf-8') as f:
            if items:
                f.write('\n'.join(items) + '\n')
            else:
                f.write('')
