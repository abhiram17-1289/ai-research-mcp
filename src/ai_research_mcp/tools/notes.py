"""MCP tools for note CRUD operations.

Each function decorated with `@register` is exposed to MCP clients
as a callable tool. The decorator is just a tiny indirection — at
import time, the tools are registered onto the FastMCP server
instance passed to `register_notes_tools(mcp)`.

This pattern (a `register_*` function per module) lets server.py
stay tiny: it just imports each module's registrar and calls it.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ai_research_mcp import db

def register_notes_tools(mcp : FastMCP) -> None :
    """Register all note-related tools onto the given FastMCP server."""

    @mcp.tool
    def add_note(title: str, content: str, tags: str = "") -> dict[str, Any]:
        """Create a new note.

        Args:
            title: Short title for the note.
            content: Body text of the note.
            tags: Optional comma-separated tags (e.g. 'research,arxiv').

        Returns:
            The created note as a dict with id, title, content, tags,
            created_at, and updated_at.
        """
        return db.create_note(title=title, content=content, tags=tags)

    @mcp.tool
    def get_note(note_id: int) -> dict[str, Any]:
        """Retrieve a single note by its ID.

        Args:
            note_id: The numeric ID of the note to fetch.

        Returns:
            The note as a dict. Raises an error if the note doesn't exist.
        """
        note = db.get_note(note_id)
        if note is None:
            raise ValueError(f"No note found with id={note_id}")
        return note

    @mcp.tool
    def list_notes(
        limit: int = 50,
        tag_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """List notes, most recently updated first.

        Args:
            limit: Maximum number of notes to return (default 50).
            tag_filter: Optional substring to filter notes by tag.

        Returns:
            A list of note dicts. Empty list if no notes match.
        """
        return db.list_notes(limit=limit, tag_filter=tag_filter)

    @mcp.tool
    def update_note(
        note_id: int,
        title: str | None = None,
        content: str | None = None,
        tags: str | None = None,
    ) -> dict[str, Any]:
        """Update one or more fields of an existing note.

        Only fields you pass are changed. Omitted fields are left as-is.

        Args:
            note_id: The numeric ID of the note to update.
            title: New title (optional).
            content: New body content (optional).
            tags: New comma-separated tags (optional).

        Returns:
            The updated note. Raises an error if the note doesn't exist.
        """
        updated = db.update_note(
            note_id=note_id, title=title, content=content, tags=tags
        )
        if updated is None:
            raise ValueError(f"No note found with id={note_id}")
        return updated

    @mcp.tool
    def delete_note(note_id: int) -> dict[str, Any]:
        """Delete a note by ID.

        Args:
            note_id: The numeric ID of the note to delete.

        Returns:
            A dict with `deleted=True` on success.
            Raises an error if the note doesn't exist.
        """
        if not db.delete_note(note_id):
            raise ValueError(f"No note found with id={note_id}")
        return {"deleted": True, "note_id": note_id}