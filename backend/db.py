import sqlite3
from datetime import datetime, timezone
import os

DB_PATH = os.environ.get("DB_PATH", "data.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER NOT NULL REFERENCES monitors(id),
            status_code INTEGER,
            response_time_ms INTEGER,
            is_up INTEGER NOT NULL,
            checked_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def create_monitor(url: str):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO monitors (url, created_at) VALUES (?, ?)", (url, now_iso())
    )
    conn.commit()
    monitor_id = cur.lastrowid
    conn.close()
    return monitor_id


def list_monitors():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT m.id, m.url, m.created_at,
               c.status_code, c.response_time_ms, c.is_up, c.checked_at
        FROM monitors m
        LEFT JOIN checks c ON c.id = (
            SELECT id FROM checks WHERE monitor_id = m.id ORDER BY id DESC LIMIT 1
        )
        ORDER BY m.id
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_monitor_urls():
    conn = get_conn()
    rows = conn.execute("SELECT id, url FROM monitors").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_checks(monitor_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT status_code, response_time_ms, is_up, checked_at FROM checks WHERE monitor_id = ? ORDER BY id DESC",
        (monitor_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_check(monitor_id: int, status_code, response_time_ms, is_up: bool):
    conn = get_conn()
    conn.execute(
        "INSERT INTO checks (monitor_id, status_code, response_time_ms, is_up, checked_at) VALUES (?, ?, ?, ?, ?)",
        (monitor_id, status_code, response_time_ms, int(is_up), now_iso()),
    )
    conn.commit()
    conn.close()


def delete_monitor(monitor_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM checks WHERE monitor_id = ?", (monitor_id,))
    conn.execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
    conn.commit()
    conn.close()
