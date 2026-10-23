"""Tests for the shared helper functions in utils."""

import os
import sys
import time
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import gettext

gettext.install("metamorphose3", "/nonexistent")

import utils


class SlicePositionTests(unittest.TestCase):
    def test_single_character_from_end(self):
        self.assertEqual(utils.calc_slice_pos(-1, 1), (-1, None))

    def test_multi_character_from_end_clamped(self):
        # a negative start whose end reaches zero is reported as open ended
        self.assertEqual(utils.calc_slice_pos(-2, 2), (-2, None))

    def test_multi_character_from_end_inside_string(self):
        self.assertEqual(utils.calc_slice_pos(-5, 2), (-5, -3))

    def test_inner_slice(self):
        self.assertEqual(utils.calc_slice_pos(2, 3), (2, 5))

    def test_slice_starting_at_zero(self):
        self.assertEqual(utils.calc_slice_pos(0, 4), (0, 4))


class DateFormattingTests(unittest.TestCase):
    def test_returns_text(self):
        value = utils.udate(None, "%Y-%m-%d", time.localtime(0))
        self.assertIsInstance(value, str)
        self.assertEqual(len(value), 10)

    def test_honours_format(self):
        stamp = time.localtime(0)
        self.assertEqual(utils.udate(None, "%Y", stamp), time.strftime("%Y", stamp))

    def test_accepts_non_ascii_format(self):
        value = utils.udate(None, "\u00e9 %H", time.localtime(0))
        self.assertIsInstance(value, str)
        self.assertTrue(value.startswith("\u00e9"))


class EncodingChoiceTests(unittest.TestCase):
    def test_system_default_is_a_usable_codec(self):
        import codecs

        choice = utils.get_encoding_choices("Use System Default")
        self.assertIsInstance(choice, tuple)
        self.assertTrue(choice)
        self.assertNotEqual(choice[0], "None")
        codecs.lookup(choice[0])

    def test_unicode_group_offers_utf8(self):
        choice = utils.get_encoding_choices("All Languages / Unicode")
        self.assertIn("utf_8", choice)

    def test_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            utils.get_encoding_choices("no such group")


if __name__ == "__main__":
    unittest.main()
