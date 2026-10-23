# -*- coding: utf-8 -*-
"""
Shorthand Pattern parser and compiler (PBRenamer style).
Converts human-friendly shorthand wildcards into robust regular expressions:
  {#} -> Digits: ([0-9]+)
  {L} -> Letters: ([^\\W\\d_]+)
  {C} -> Non-whitespace: ([\\S]+)
  {X} -> Any characters: ([\\S\\s]+)
  {@} -> Non-capturing wildcard: (?:.*)
"""

import re

SHORTHAND_TOKENS = {
    "{#}": r"([0-9]+)",
    "{L}": r"([^\W\d_]+)",
    "{C}": r"([\S]+)",
    "{X}": r"([\S\s]+)",
    "{@}": r"(?:.*)",
}


def is_shorthand_pattern(pattern):
    """Return True if pattern contains shorthand tokens."""
    if not pattern:
        return False
    return any(token in pattern for token in SHORTHAND_TOKENS)


def shorthand_to_regex(pattern):
    """Convert user pattern with shorthand tokens into standard regex."""
    if not pattern:
        return ""
    # Escape regex special characters except braces
    escaped = []
    i = 0
    while i < len(pattern):
        matched = False
        for token in SHORTHAND_TOKENS:
            if pattern.startswith(token, i):
                escaped.append(SHORTHAND_TOKENS[token])
                i += len(token)
                matched = True
                break
        if not matched:
            ch = pattern[i]
            if ch in r".^$*+?()[]\|":
                escaped.append("\\" + ch)
            else:
                escaped.append(ch)
            i += 1
    return "".join(escaped)
