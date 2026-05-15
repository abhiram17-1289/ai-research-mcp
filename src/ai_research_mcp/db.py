"""SQLite data access layer.

This module is the *only* place in the codebase that talks to SQLite.
Tools and resources call functions like `create_note(...)` rather than
writing SQL inline. This separation means:

  - We can swap SQLite for Postgres later by changing only this file.
  - SQL injection risk is contained to one module we audit carefully.
  - Tests can mock or use an in-memory DB without touching tool code.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .config import DATABASE_PATH

#Schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    tags        TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    description  TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'completed')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);
"""

@contextmanager
def get_connection(db_path : Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection, committing on success and closing always.

    Use as a context manager:

        with get_connection() as conn:
            conn.execute("INSERT ...")
            # auto-commits if no exception, auto-closes either way

    Rows come back as sqlite3.Row objects, accessible by column name
    (row["title"]) instead of just index (row[0]).
    """

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Create tables if they don't exist. Safe to call repeatedly."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)

#Notes CRUD
def create_note(title: str, content: str, tags: str = "") -> dict[str, Any]:
    """Insert a new note. Returns the created row as a dict."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags),
        )
        note_id = cursor.lastrowid
    # Re-fetch with the new ID so created_at/updated_at are populated.
    return get_note(note_id)  # type: ignore[return-value]

def get_note(note_id: int) -> dict[str, Any] | None:
    """Fetch a single note by ID. Returns None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    return dict(row) if row else None

def list_notes(limit: int = 50, tag_filter: str | None = None) -> list[dict[str, Any]]:
    """List notes ordered by most recently updated.

    Args:
        limit: Maximum number of notes to return.
        tag_filter: If provided, only return notes whose `tags` column
            contains this substring. (Simple LIKE match — fine for our
            comma-separated tag design.)
    """
    with get_connection() as conn:
        if tag_filter:
            rows = conn.execute(
                "SELECT * FROM notes WHERE tags LIKE ? "
                "ORDER BY updated_at DESC LIMIT ?",
                (f"%{tag_filter}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM notes ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(row) for row in rows]

def update_note(
    note_id: int,
    title: str | None = None,
    content: str | None = None,
    tags: str | None = None,
) -> dict[str, Any] | None:
    """Update a note's fields. Only provided fields are changed.

    Returns the updated row, or None if the note doesn't exist.
    """
    # Build SET clause dynamically based on which fields were provided.
    updates: list[str] = []
    params: list[Any] = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if tags is not None:
        updates.append("tags = ?")
        params.append(tags)

    if not updates:
        # Nothing to update — just return the current state.
        return get_note(note_id)

    # Always bump updated_at on any modification.
    updates.append("updated_at = datetime('now')")
    params.append(note_id)  # for the WHERE clause

    sql = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"

    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        if cursor.rowcount == 0:
            return None  # no row matched

    return get_note(note_id)


def delete_note(note_id: int) -> bool:
    """Delete a note. Returns True if a row was deleted, False otherwise."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cursor.rowcount > 0
    
