"""Manual smoke test for the database layer.

Run with:  uv run python tests/smoke_test_db.py

This is NOT a real unit test — we'll add pytest later. Right now we
just want a quick script that exercises every CRUD function and prints
the results, so we can eyeball that everything works.
"""

from __future__ import annotations

from ai_research_mcp import db


def main() -> None:
    print("Initializing database...")
    db.init_db()

    print("\nCreating notes...")
    n1 = db.create_note("First note", "Hello, MCP!", tags="intro,test")
    n2 = db.create_note("Second note", "SQLite is cozy.", tags="db")
    print(f"  Created: {n1}")
    print(f"  Created: {n2}")

    print("\nGetting note by ID...")
    fetched = db.get_note(n1["id"])
    print(f"  Got: {fetched}")
    assert fetched is not None
    assert fetched["title"] == "First note"

    print("\nListing all notes...")
    all_notes = db.list_notes()
    print(f"  Found {len(all_notes)} note(s)")
    for note in all_notes:
        print(f"    - [{note['id']}] {note['title']} (tags={note['tags']!r})")

    print("\nFiltering by tag 'db'...")
    filtered = db.list_notes(tag_filter="db")
    print(f"  Found {len(filtered)} matching note(s)")

    print("\nUpdating first note...")
    updated = db.update_note(n1["id"], content="Updated content!", tags="intro,test,edited")
    print(f"  Updated: {updated}")
    assert updated is not None
    assert updated["content"] == "Updated content!"

    print("\nDeleting second note...")
    deleted = db.delete_note(n2["id"])
    print(f"  Deleted: {deleted}")
    assert deleted is True

    print("\nVerifying deletion...")
    gone = db.get_note(n2["id"])
    print(f"  Re-fetched: {gone}")
    assert gone is None

    print("\nDeleting non-existent note (should return False)...")
    fake_delete = db.delete_note(99999)
    print(f"  Result: {fake_delete}")
    assert fake_delete is False

    print("\n✓ All smoke tests passed.")


if __name__ == "__main__":
    main()