"""AI Research & Knowledge Assistant — MCP server entry point.

This module is intentionally thin. It:
  1. Creates the FastMCP server instance.
  2. Initializes the database (ensures tables exist).
  3. Registers tools from each tools/* module.
  4. Starts the server.

Adding a new tool group is a 2-line change: import its register
function, call it. server.py never grows linearly with tool count.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ai_research_mcp import db
from ai_research_mcp.tools.notes import register_notes_tools


mcp = FastMCP("ai-research-mcp")


@mcp.tool
def ping() -> str:
    """Health-check tool. Returns 'pong' to verify the server is alive."""
    return "pong"


# Register tool groups.
register_notes_tools(mcp)


def main() -> None:
    """Entry point invoked by `uv run ai-research-mcp`."""
    db.init_db()
    mcp.run()


if __name__ == "__main__":
    main()