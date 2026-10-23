"""
Resilient caching layer for OSV.dev vulnerability queries and registry metadata.
Uses a fast, disk-backed SQLite store with TTL and auto-expiry to prevent API rate limits.
"""

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from scds.config import DEFAULT_CACHE_TTL


class CacheManager:
    """
    High-performance, rate-limit resistant key-value cache.
    Stores external API responses (OSV, PyPI, NPM) to guarantee sub-second scans.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            cache_dir = Path.home() / ".cache" / "scds"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(cache_dir / "scds_cache.db")
        else:
            self.db_path = db_path

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        # Enable WAL mode for high concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_store (
                    namespace TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    data TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    PRIMARY KEY (namespace, cache_key)
                )
            """)
            conn.commit()

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Retrieves a cached value if it exists and has not expired.
        """
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data, expires_at FROM cache_store WHERE namespace = ? AND cache_key = ?",
                (namespace, key)
            )
            row = cursor.fetchone()
            if not row:
                return None

            data_str, expires_at = row
            if now > expires_at:
                # Expired: remove lazily
                conn.execute(
                    "DELETE FROM cache_store WHERE namespace = ? AND cache_key = ?",
                    (namespace, key)
                )
                conn.commit()
                return None

            try:
                return json.loads(data_str)
            except Exception:
                return data_str

    def set(self, namespace: str, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL) -> None:
        """
        Saves a value to the cache with an expiration timestamp.
        """
        now = time.time()
        expires_at = now + ttl
        data_str = json.dumps(value) if not isinstance(value, str) else value

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_store (namespace, cache_key, data, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (namespace, key, data_str, expires_at)
            )
            conn.commit()

    def clear(self, namespace: Optional[str] = None) -> int:
        """
        Clears all items or items in a specific namespace.
        """
        with self._get_connection() as conn:
            if namespace:
                cursor = conn.execute("DELETE FROM cache_store WHERE namespace = ?", (namespace,))
            else:
                cursor = conn.execute("DELETE FROM cache_store")
            conn.commit()
            return cursor.rowcount


# Global singleton instance for easy import across modules
global_cache = CacheManager()
