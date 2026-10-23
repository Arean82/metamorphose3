"""Tests for filesystem names and text file handling with non-ASCII content."""

import os
import shutil
import sys
import tempfile
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import gettext

gettext.install("metamorphose3", "/nonexistent")

import utils

ACCENTED = "\u00e9\u00e8\u00ea.txt"
CJK = "\u4e2d\u6587\u540d\u79f0.txt"
MIXED = "\u00e9l\u00e8ve-\u4e2d\u6587-\u00df.txt"


class UnicodeNameTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _names_round_trip(self, name):
        path = os.path.join(self.root, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("content")
        listed = os.listdir(self.root)
        self.assertIn(name, listed)
        self.assertIsInstance(name, str)
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "content")
        os.remove(path)

    def test_accented_name(self):
        self._names_round_trip(ACCENTED)

    def test_cjk_name(self):
        self._names_round_trip(CJK)

    def test_mixed_name(self):
        self._names_round_trip(MIXED)

    def test_join_and_split_preserve_name(self):
        path = os.path.join(self.root, CJK)
        self.assertEqual(os.path.basename(path), CJK)
        self.assertEqual(os.path.dirname(path), self.root)


class TextFileTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_write_file_round_trip(self):
        target = os.path.join(self.root, "out", "data.txt")
        utils.write_file(target, "\u00e9\u00e8 \u4e2d\u6587")
        with open(target, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "\u00e9\u00e8 \u4e2d\u6587")

    def test_write_file_creates_parent(self):
        target = os.path.join(self.root, "a", "b", "c.txt")
        utils.write_file(target, "x")
        self.assertTrue(os.path.isfile(target))

    def test_undo_file_format_round_trip(self):
        # The engine writes one path per line as UTF-8; reading must give it back.
        target = os.path.join(self.root, "undo.bak")
        names = [ACCENTED, CJK, MIXED]
        with open(target, "w", encoding="utf-8", newline="") as handle:
            for name in names:
                handle.write(os.path.join(self.root, name) + "\n")
        with open(target, encoding="utf-8", newline="") as handle:
            restored = [line.rstrip("\n") for line in handle]
        self.assertEqual(restored, [os.path.join(self.root, n) for n in names])

    def test_safe_makedir_is_idempotent(self):
        target = os.path.join(self.root, "created")
        utils.safe_makedir(target)
        self.assertTrue(os.path.isdir(target))
        utils.safe_makedir(target)
        self.assertTrue(os.path.isdir(target))

    def test_is_pil_loaded(self):
        self.assertTrue(utils.is_pil_loaded())


if __name__ == "__main__":
    unittest.main()
