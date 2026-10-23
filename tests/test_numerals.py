"""Tests for the numeral conversion helpers."""

import os
import sys
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import gettext

gettext.install("metamorphose3", "/nonexistent")

from operations import greekNumb
from operations import roman


class RomanTests(unittest.TestCase):
    def test_known_values(self):
        cases = {
            1: "I",
            4: "IV",
            9: "IX",
            14: "XIV",
            40: "XL",
            90: "XC",
            400: "CD",
            900: "CM",
            1994: "MCMXCIV",
            2026: "MMXXVI",
            3999: "MMMCMXCIX",
        }
        for number, expected in cases.items():
            self.assertEqual(roman.toRoman(number), expected)

    def test_zero_is_out_of_range(self):
        with self.assertRaises(roman.OutOfRangeError):
            roman.toRoman(0)

    def test_negative_is_out_of_range(self):
        with self.assertRaises(roman.OutOfRangeError):
            roman.toRoman(-5)

    def test_too_large_is_out_of_range(self):
        with self.assertRaises(roman.OutOfRangeError):
            roman.toRoman(roman.MAX_ROMAN_NUMERAL + 1)

    def test_fraction_is_not_integer(self):
        with self.assertRaises(roman.NotIntegerError):
            roman.toRoman(1.5)


class GreekTests(unittest.TestCase):
    def test_returns_text(self):
        value = greekNumb.int2greek(1234)
        self.assertIsInstance(value, str)
        self.assertTrue(value)

    def test_handles_each_digit(self):
        for number in (1, 7, 10, 99, 500, 999, 1000, 2026):
            with self.subTest(number=number):
                self.assertIsInstance(greekNumb.int2greek(number), str)

    def test_negative_sign_is_stripped(self):
        self.assertEqual(greekNumb.int2greek(-12), greekNumb.int2greek(12))

    def test_rejects_non_numeric_input(self):
        with self.assertRaises(greekNumb.Error):
            greekNumb.int2greek("abc")

    def test_digit_table_is_indexable(self):
        # The table used to be a map() iterator, which cannot be subscripted.
        self.assertIsInstance(greekNumb.greek_digits, list)
        self.assertEqual(len(greekNumb.greek_digits), 3)
        self.assertEqual(greekNumb.greek_digits[0][1], "α")


if __name__ == "__main__":
    unittest.main()
