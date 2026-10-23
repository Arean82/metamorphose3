"""Tests for the copy/move helpers used by the renaming engine."""

import os
import shutil
import sys
import tempfile
import time
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import shutil1


class CopyFileTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _write(self, name, text):
        path = os.path.join(self.root, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_copy2_copies_contents(self):
        src = self._write("a.txt", "hello")
        dst = os.path.join(self.root, "b.txt")
        shutil1.copy2(src, dst)
        with open(dst, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "hello")

    def test_copy2_preserves_mtime(self):
        src = self._write("a.txt", "hello")
        stamp = time.time() - 7200
        os.utime(src, (stamp, stamp))
        dst = os.path.join(self.root, "b.txt")
        shutil1.copy2(src, dst)
        self.assertAlmostEqual(os.stat(dst).st_mtime, stamp, delta=2)

    def test_copy2_into_directory(self):
        src = self._write("a.txt", "data")
        target = os.path.join(self.root, "nested")
        os.makedirs(target)
        shutil1.copy2(src, target)
        self.assertTrue(os.path.exists(os.path.join(target, "a.txt")))

    def test_copy_onto_itself_raises(self):
        src = self._write("a.txt", "data")
        with self.assertRaises(shutil1.Error):
            shutil1.copy2(src, src)

    def test_copyfileobj_round_trip(self):
        src = self._write("a.txt", "x" * 40000)
        dst = os.path.join(self.root, "b.txt")
        with open(src, "rb") as source, open(dst, "wb") as target:
            shutil1.copyfileobj(source, target)
        self.assertEqual(os.path.getsize(dst), 40000)


class TreeTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _tree(self):
        base = os.path.join(self.root, "tree")
        os.makedirs(os.path.join(base, "child"))
        with open(os.path.join(base, "one.txt"), "w", encoding="utf-8") as handle:
            handle.write("1")
        with open(os.path.join(base, "child", "two.txt"), "w", encoding="utf-8") as handle:
            handle.write("2")
        return base

    def test_copytree_is_recursive(self):
        base = self._tree()
        target = os.path.join(self.root, "copy")
        shutil1.copytree(base, target)
        self.assertTrue(os.path.exists(os.path.join(target, "one.txt")))
        self.assertTrue(os.path.exists(os.path.join(target, "child", "two.txt")))

    def test_rmtree_removes_tree(self):
        base = self._tree()
        shutil1.rmtree(base)
        self.assertFalse(os.path.exists(base))

    def test_move_renames_file(self):
        src = os.path.join(self.root, "move.txt")
        with open(src, "w", encoding="utf-8") as handle:
            handle.write("m")
        dst = os.path.join(self.root, "moved.txt")
        shutil1.move(src, dst)
        self.assertTrue(os.path.exists(dst))
        self.assertFalse(os.path.exists(src))

    def test_move_directory_into_itself_raises(self):
        base = self._tree()
        nested = os.path.join(base, "child", "deeper")
        with self.assertRaises(shutil1.Error):
            shutil1.move(base, nested)

    def test_destinsrc_detects_nesting(self):
        base = self._tree()
        self.assertTrue(shutil1.destinsrc(base, os.path.join(base, "child")))
        self.assertFalse(shutil1.destinsrc(base, os.path.join(self.root, "elsewhere")))


if __name__ == "__main__":
    unittest.main()
