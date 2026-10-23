"""Unit tests for new features: SQLite DB, Sanitizer, Bookmarks, and Shorthands."""

import os
import tempfile
import unittest

import db
import bookmarks
import sanitizer
from operations import shorthand


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = db.Database(":memory:")

    def test_settings_storage(self):
        self.db.set_setting("theme", "dark")
        self.assertEqual(self.db.get_setting("theme"), "dark")
        self.db.set_setting("theme", "light")
        self.assertEqual(self.db.get_setting("theme"), "light")
        self.assertEqual(self.db.get_setting("non_existent", "default"), "default")

    def test_many_settings(self):
        self.db.set_many_settings({"key1": "val1", "key2": 123})
        all_s = self.db.get_all_settings()
        self.assertEqual(all_s["key1"], "val1")
        self.assertEqual(all_s["key2"], "123")

    def test_bookmarks(self):
        self.db.add_bookmark("Photos", "/home/test/Photos")
        bms = self.db.get_bookmarks()
        self.assertEqual(bms, [("Photos", "/home/test/Photos")])
        self.db.remove_bookmark("/home/test/Photos")
        self.assertEqual(self.db.get_bookmarks(), [])

    def test_pattern_history(self):
        self.db.record_pattern("track_{#}", "search")
        self.db.record_pattern("photo_{#}", "search")
        hist = self.db.get_pattern_history("search")
        self.assertEqual(hist, ["photo_{#}", "track_{#}"])


class SanitizerTests(unittest.TestCase):
    def test_invalid_chars_detection(self):
        self.assertTrue(sanitizer.has_invalid_chars("AC/DC: Live *2024*"))
        self.assertEqual(sanitizer.has_invalid_chars("Clean Name"), [])

    def test_homoglyph_substitution(self):
        cleaned = sanitizer.sanitize_filename('AC/DC: Live *2024* ? <nice>')
        # Assert none of the forbidden characters remain
        for ch in r'/\:*?"<>|':
            self.assertNotIn(ch, cleaned)
        # Assert meaningful substitution occurred
        self.assertIn("AC", cleaned)
        self.assertIn("DC", cleaned)
        self.assertIn("2024", cleaned)


class BookmarkTests(unittest.TestCase):
    def test_standard_locations(self):
        locs = bookmarks.get_standard_locations()
        self.assertTrue(len(locs) >= 1)
        self.assertEqual(locs[0][0], "Home")


class ShorthandPatternTests(unittest.TestCase):
    def test_shorthand_detection(self):
        self.assertTrue(shorthand.is_shorthand_pattern("file_{#}"))
        self.assertTrue(shorthand.is_shorthand_pattern("{L}_{#}"))
        self.assertFalse(shorthand.is_shorthand_pattern("normal_file.txt"))

    def test_shorthand_conversion(self):
        converted = shorthand.shorthand_to_regex("track_{#}_{L}.mp3")
        import re
        m = re.match(converted, "track_05_song.mp3")
        self.assertIsNotNone(m)
        self.assertEqual(m.groups(), ("05", "song"))


if __name__ == "__main__":
    unittest.main()
