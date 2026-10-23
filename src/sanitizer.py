# -*- coding: utf-8 -*-
"""
Sanitizer for invalid filesystem characters.
Maps forbidden characters on Windows and other OSes to visually identical Unicode homoglyphs.
"""

# Windows forbidden characters and their corresponding clean Unicode homoglyphs
HOMOGLYPH_MAP = {
    '/': '\u2044',   # ⁄ Fraction Slash
    '\\': '\ufe68',  # ﹨ Small Reverse Solidus
    ':': '\u02f8',   # ˸ Modifier Letter Raised Colon
    '*': '\uff0a',   # ＊ Fullwidth Asterisk
    '?': '\uff1f',   # ？ Fullwidth Question Mark
    '"': '\u201c',   # “ Left Double Quotation Mark
    '<': '\uff1c',   # ＜ Fullwidth Less-Than Sign
    '>': '\uff1e',   # ＞ Fullwidth Greater-Than Sign
    '|': '\u00a6',   # ¦ Broken Bar
}


def sanitize_filename(name, replace_homoglyphs=True):
    """
    Replace illegal filesystem characters with Unicode homoglyphs,
    or strip them if replace_homoglyphs is False.
    """
    if not name:
        return name
    result = []
    for ch in name:
        if ch in HOMOGLYPH_MAP:
            if replace_homoglyphs:
                result.append(HOMOGLYPH_MAP[ch])
        else:
            result.append(ch)
    return "".join(result)


def has_invalid_chars(name):
    """Return list of invalid filesystem characters found in name."""
    if not name:
        return []
    return [ch for ch in HOMOGLYPH_MAP if ch in name]
