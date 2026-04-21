"""SQLite database layer."""
import sqlite3
import os
from typing import Optional
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "urls.db")


def _ensure_dir():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)


@contextmanager
def get_conn():
    _ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                code        TEXT PRIMARY KEY,
                long_url    TEXT NOT NULL,
                alias       TEXT,
                clicks      INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now')),
                last_click  TEXT,
                expires_at  TEXT
            )
        """)
        # Migration: add expires_at if upgrading from old DB
        try:
            conn.execute("ALTER TABLE urls ADD COLUMN expires_at TEXT")
        except sqlite3.OperationalError:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS click_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code        TEXT NOT NULL,
                clicked_at  TEXT DEFAULT (datetime('now')),
                referrer    TEXT
            )
        """)


def insert(code: str, long_url: str, alias: Optional[str] = None,
           expires_at: Optional[str] = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO urls (code, long_url, alias, expires_at) VALUES (?, ?, ?, ?)",
            (code, long_url, alias, expires_at),
        )


def get_by_code(code: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM urls WHERE code = ?", (code,)).fetchone()


def code_exists(code: str) -> bool:
    return get_by_code(code) is not None


def increment_clicks(code: str, referrer: Optional[str] = None):
    with get_conn() as conn:
        conn.execute(
            "UPDATE urls SET clicks = clicks + 1, last_click = datetime('now') WHERE code = ?",
            (code,),
        )
        conn.execute(
            "INSERT INTO click_log (code, referrer) VALUES (?, ?)",
            (code, referrer),
        )


def delete(code: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM urls WHERE code = ?", (code,))
        conn.execute("DELETE FROM click_log WHERE code = ?", (code,))
        return cur.rowcount > 0


def list_all() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()


def clicks_per_day(code: str, days: int = 7) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT date(clicked_at) as day, COUNT(*) as cnt
            FROM click_log
            WHERE code = ? AND clicked_at >= datetime('now', ?)
            GROUP BY day ORDER BY day
        """, (code, f"-{days} days")).fetchall()
        return [{"day": r["day"], "clicks": r["cnt"]} for r in rows]


def top_urls(limit: int = 5) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM urls ORDER BY clicks DESC LIMIT ?", (limit,)
        ).fetchall()


def update_url(code: str, new_long_url: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("UPDATE urls SET long_url = ? WHERE code = ?", (new_long_url, code))
        return cur.rowcount > 0


def stats() -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as total, SUM(clicks) as total_clicks FROM urls"
        ).fetchone()
        active = conn.execute(
            "SELECT COUNT(*) FROM urls WHERE expires_at IS NULL OR expires_at > datetime('now')"
        ).fetchone()[0]
        return {
            "total_urls":    row["total"],
            "total_clicks":  row["total_clicks"] or 0,
            "active_urls":   active,
        }
