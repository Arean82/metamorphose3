"""Tests for renaming a single item through the renamer engine."""

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

# renamer/__init__.py builds wx widgets at import time, which needs a running
# wx.App. Load the engine module directly so it can be tested headless.
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "engine", os.path.join(SRC, "renamer", "engine.py")
)
engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(engine)


class _FakeDisplay:
    def __init__(self):
        self.visible = None
        self.refreshed = 0

    def EnsureVisible(self, index):
        self.visible = index

    def Refresh(self):
        self.refreshed += 1


class _FakeBottomWindow:
    def __init__(self):
        self.display = _FakeDisplay()


class _FakeMainWindow:
    """Only the surface Core touches while renaming one item."""

    def __init__(self):
        self.toRename = []
        self.bottomWindow = _FakeBottomWindow()
        self.updates = 0
        self.status = []

    def Update(self):
        self.updates += 1

    def set_status_msg(self, message, kind=None):
        self.status.append((message, kind))


class RenameItemTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.main = _FakeMainWindow()
        self.core = engine.Core(self.main)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _item(self, source):
        # Mirrors the engine's expectation: item[1][1] holds the rename result.
        return [(source,), [None, None]]

    def _touch(self, name, text="x"):
        path = os.path.join(self.root, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_renames_file(self):
        source = self._touch("before.txt")
        target = os.path.join(self.root, "after.txt")
        self.main.toRename = [self._item(source)]
        self.assertEqual(self.core._rename_item(0, (source,), (target,), 25), False)
        self.assertTrue(os.path.exists(target))
        self.assertFalse(os.path.exists(source))
        self.assertIs(self.main.toRename[0][1][1], True)

    def test_moves_into_existing_directory(self):
        source = self._touch("file.txt")
        target_dir = os.path.join(self.root, "sub")
        os.makedirs(target_dir)
        target = os.path.join(target_dir, "file.txt")
        self.main.toRename = [self._item(source)]
        self.assertEqual(self.core._rename_item(0, (source,), (target,), 25), False)
        self.assertTrue(os.path.exists(target))

    def test_creates_missing_parent_directory(self):
        source = self._touch("file.txt")
        target = os.path.join(self.root, "deep", "nested", "file.txt")
        self.main.toRename = [self._item(source)]
        self.assertEqual(self.core._rename_item(0, (source,), (target,), 25), False)
        self.assertTrue(os.path.exists(target))

    def test_refreshes_display_on_interval(self):
        source = self._touch("a.txt")
        target = os.path.join(self.root, "b.txt")
        self.main.toRename = [self._item(source)]
        self.core._rename_item(0, (source,), (target,), 1)
        self.assertEqual(self.main.bottomWindow.display.visible, 0)
        self.assertGreaterEqual(self.main.bottomWindow.display.refreshed, 1)
        self.assertGreaterEqual(self.main.updates, 1)

    def test_skips_refresh_off_interval(self):
        first = self._touch("a.txt")
        second = self._touch("b.txt")
        target = os.path.join(self.root, "c.txt")
        # index 0 always refreshes because 0 % n == 0, so use index 1
        self.main.toRename = [self._item(first), self._item(second)]
        self.core._rename_item(1, (second,), (target,), 25)
        self.assertIsNone(self.main.bottomWindow.display.visible)

    def test_renames_unicode_name(self):
        source = self._touch("\u00e9\u00e8\u4e2d\u6587.txt")
        target = os.path.join(self.root, "\u4e2d\u6587-\u00e9.txt")
        self.main.toRename = [self._item(source)]
        self.assertEqual(self.core._rename_item(0, (source,), (target,), 25), False)
        self.assertTrue(os.path.exists(target))
        self.assertIn("\u4e2d\u6587-\u00e9.txt", os.listdir(self.root))


if __name__ == "__main__":
    unittest.main()
