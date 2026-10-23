# -*- coding: utf-8 -*-
"""
System and User Directory Bookmarks helper.
Discovers native OS file manager bookmarks (GTK, user favorites, standard locations).
"""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse
import db


def get_gtk_bookmarks():
    """Read Linux GTK / Nautilus bookmarks."""
    candidates = [
        Path.home() / ".config" / "gtk-3.0" / "bookmarks",
        Path.home() / ".gtk-bookmarks",
    ]
    bookmarks = []
    for cand in candidates:
        if cand.exists():
            try:
                for line in cand.read_text(encoding="utf-8", errors="replace").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(None, 1)
                    parsed = urlparse(parts[0])
                    if parsed.scheme == "file":
                        dir_path = unquote(parsed.path)
                    elif parts[0].startswith("/"):
                        dir_path = parts[0]
                    else:
                        continue
                    if os.path.isdir(dir_path):
                        name = parts[1] if len(parts) > 1 else os.path.basename(dir_path) or dir_path
                        bookmarks.append((name, dir_path))
            except Exception:
                pass
            break
    return bookmarks


def get_standard_locations():
    """Return standard user locations (Home, Documents, Downloads, etc.)."""
    home = str(Path.home())
    locs = [
        ("Home", home),
    ]
    for sub in ("Desktop", "Documents", "Downloads", "Music", "Pictures", "Videos"):
        p = os.path.join(home, sub)
        if os.path.isdir(p):
            locs.append((sub, p))
    return locs


def get_user_bookmarks():
    """Return user-saved bookmarks from SQLite database."""
    try:
        return db.get_db().get_bookmarks()
    except Exception:
        return []


def add_user_bookmark(name, path):
    """Save a user bookmark to the SQLite database."""
    try:
        db.get_db().add_bookmark(name, path)
    except Exception:
        pass


def remove_user_bookmark(path):
    """Remove a user bookmark from the SQLite database."""
    try:
        db.get_db().remove_bookmark(path)
    except Exception:
        pass
