"""
Reads browsing history from Chromium-based browsers (Chrome, Edge, Brave).

Chrome/Edge store history in an SQLite file that is locked while the browser
is open. We work around this by copying the file to a temp location before
querying — the copy is always safe to read.
"""

import os
import shutil
import sqlite3
import tempfile
import platform
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

CHROMIUM_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)


def _chromium_ts_to_datetime(microseconds: int) -> datetime:
    """Convert Chrome's microseconds-since-1601 to a timezone-aware datetime."""
    return CHROMIUM_EPOCH + timedelta(microseconds=microseconds)


def _get_history_paths() -> list[str]:
    """Return candidate history file paths for common Chromium browsers."""
    home = os.path.expanduser("~")
    system = platform.system()

    if system == "Windows":
        local_app = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
        roaming_app = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        candidates = [
            os.path.join(local_app, "Google", "Chrome", "User Data", "Default", "History"),
            os.path.join(local_app, "Microsoft", "Edge", "User Data", "Default", "History"),
            os.path.join(local_app, "BraveSoftware", "Brave-Browser", "User Data", "Default", "History"),
            os.path.join(roaming_app, "Opera Software", "Opera Stable", "History"),
        ]
    elif system == "Darwin":
        candidates = [
            os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "History"),
            os.path.join(home, "Library", "Application Support", "Microsoft Edge", "Default", "History"),
        ]
    else:  # Linux
        candidates = [
            os.path.join(home, ".config", "google-chrome", "Default", "History"),
            os.path.join(home, ".config", "microsoft-edge", "Default", "History"),
            os.path.join(home, ".config", "chromium", "Default", "History"),
        ]

    return [p for p in candidates if os.path.exists(p)]


def read_browser_history(limit: int = 500, days_back: int = 7) -> list[dict]:
    """
    Return up to `limit` history entries from the last `days_back` days.
    Each entry is a dict: {url, title, visited_at (datetime), domain, source}.

    Falls back to an empty list if no history file is found or readable.
    """
    paths = _get_history_paths()
    if not paths:
        return []

    cutoff_microseconds = _datetime_to_chromium_ts(
        datetime.now(timezone.utc) - timedelta(days=days_back)
    )

    entries: list[dict] = []

    for path in paths:
        tmp_path = None
        try:
            # Copy to temp so we can read even while browser is open
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".db", prefix="habits_history_")
            os.close(tmp_fd)
            shutil.copy2(path, tmp_path)

            conn = sqlite3.connect(tmp_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT v.url, v.title, v.last_visit_time
                FROM visits vi
                JOIN urls v ON vi.url = v.id
                WHERE vi.visit_time >= ?
                ORDER BY vi.visit_time DESC
                LIMIT ?
                """,
                (cutoff_microseconds, limit),
            )
            rows = cur.fetchall()
            conn.close()

            for row in rows:
                visited_at = _chromium_ts_to_datetime(row["last_visit_time"])
                domain = _extract_domain(row["url"])
                if not domain:
                    continue
                entries.append({
                    "url": row["url"],
                    "title": row["title"] or "",
                    "visited_at": visited_at,
                    "domain": domain,
                    "source": "browser",
                })

        except Exception:
            # History file may be locked, corrupted, or inaccessible — skip silently
            pass
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    # Deduplicate by (url, minute-level timestamp) — same page reloaded quickly
    seen: set[tuple] = set()
    unique: list[dict] = []
    for entry in entries:
        key = (entry["url"], entry["visited_at"].replace(second=0, microsecond=0))
        if key not in seen:
            seen.add(key)
            unique.append(entry)

    return unique[:limit]


def _datetime_to_chromium_ts(dt: datetime) -> int:
    delta = dt.replace(tzinfo=timezone.utc) - CHROMIUM_EPOCH
    return int(delta.total_seconds() * 1_000_000)


def _extract_domain(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        # Strip port and leading "www."
        host = host.split(":")[0]
        if host.startswith("www."):
            host = host[4:]
        return host if host else None
    except Exception:
        return None
