# -*- coding: utf-8 -*-
"""
Database storage layer using SQLite.
Stores user settings, directory bookmarks, and search/pattern history.
"""

import os
import sqlite3
import time

import utils


def get_db_path():
    """Return path to the application SQLite database."""
    return utils.get_user_path("metamorphose3.db")


class Database:
    """Manages SQLite storage for settings, bookmarks, and history."""

    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        if self.db_path != ':memory:':
            self._conn = None
            try:
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            except OSError:
                pass
        else:
            self._conn = sqlite3.connect(':memory:')
            self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _get_connection(self):
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Settings table (key-value)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            # Bookmarks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    created_at REAL NOT NULL
                )
            """)
            # Pattern / Regex search & replace history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pattern_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    kind TEXT NOT NULL DEFAULT 'search',
                    last_used REAL NOT NULL
                )
            """)
            # Presets table (unified preset storage)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    xml_content TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            # Active in-flight rename journal (crash-safe recovery)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rename_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    original_path TEXT NOT NULL,
                    renamed_path TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    # --- Settings API ---

    def set_setting(self, key, value):
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, str(value), time.time())
            )
            conn.commit()

    def get_setting(self, key, default=None):
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def get_all_settings(self):
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT key, value FROM settings").fetchall()
            return {r["key"]: r["value"] for r in rows}

    def set_many_settings(self, mapping):
        now = time.time()
        with self._get_connection() as conn:
            conn.cursor().executemany(
                "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                [(k, str(v), now) for k, v in mapping.items()]
            )
            conn.commit()

    # --- Bookmarks API ---

    def add_bookmark(self, name, path):
        path = os.path.abspath(path)
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO bookmarks (name, path, created_at) VALUES (?, ?, ?) "
                "ON CONFLICT(path) DO UPDATE SET name=excluded.name",
                (name, path, time.time())
            )
            conn.commit()

    def remove_bookmark(self, path):
        path = os.path.abspath(path)
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM bookmarks WHERE path = ?", (path,))
            conn.commit()

    def get_bookmarks(self):
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT name, path FROM bookmarks ORDER BY name COLLATE NOCASE ASC").fetchall()
            return [(r["name"], r["path"]) for r in rows]

    # --- Presets API ---

    def save_preset(self, name, xml_content):
        now = time.time()
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO presets (name, xml_content, created_at, updated_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(name) DO UPDATE SET xml_content=excluded.xml_content, updated_at=excluded.updated_at",
                (name, xml_content, now, now)
            )
            conn.commit()

    def get_preset(self, name):
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT xml_content FROM presets WHERE name = ?", (name,)).fetchone()
            return row["xml_content"] if row else None

    def list_presets(self):
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT name FROM presets ORDER BY name COLLATE NOCASE ASC").fetchall()
            return [r["name"] for r in rows]

    def delete_preset(self, name):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM presets WHERE name = ?", (name,))
            conn.commit()

    # --- Crash-Safe Journal API ---

    def start_batch_journal(self, batch_id, item_pairs):
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rename_journal WHERE status = 'completed'")
            cursor.executemany(
                "INSERT INTO rename_journal (batch_id, original_path, renamed_path, status, timestamp) "
                "VALUES (?, ?, ?, 'pending', ?)",
                [(batch_id, orig, ren, now) for orig, ren in item_pairs]
            )
            conn.commit()

    def mark_journal_item_done(self, batch_id, original_path):
        with self._get_connection() as conn:
            conn.cursor().execute(
                "UPDATE rename_journal SET status = 'completed' WHERE batch_id = ? AND original_path = ?",
                (batch_id, original_path)
            )
            conn.commit()

    def clear_journal_batch(self, batch_id):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM rename_journal WHERE batch_id = ?", (batch_id,))
            conn.commit()

    def get_incomplete_journal_items(self):
        with self._get_connection() as conn:
            rows = conn.cursor().execute(
                "SELECT batch_id, original_path, renamed_path, status FROM rename_journal WHERE status = 'pending' ORDER BY id ASC"
            ).fetchall()
            return [(r["batch_id"], r["original_path"], r["renamed_path"], r["status"]) for r in rows]

    # --- History API ---

    def record_pattern(self, pattern, kind="search"):
        if not pattern or not pattern.strip():
            return
        pattern = pattern.strip()
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pattern_history WHERE pattern = ? AND kind = ?", (pattern, kind))
            cursor.execute(
                "INSERT INTO pattern_history (pattern, kind, last_used) VALUES (?, ?, ?)",
                (pattern, kind, now)
            )
            # Retain only last 50 entries per kind
            cursor.execute("""
                DELETE FROM pattern_history WHERE id NOT IN (
                    SELECT id FROM pattern_history WHERE kind = ? ORDER BY last_used DESC LIMIT 50
                ) AND kind = ?
            """, (kind, kind))
            conn.commit()

    def get_pattern_history(self, kind="search", limit=15):
        with self._get_connection() as conn:
            rows = conn.cursor().execute(
                "SELECT pattern FROM pattern_history WHERE kind = ? ORDER BY last_used DESC LIMIT ?",
                (kind, limit)
            ).fetchall()
            return [r["pattern"] for r in rows]


_db_instance = None


def get_db():
    """Return singleton Database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
