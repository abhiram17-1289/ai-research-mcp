"""AI Research & Knowledge Assistant — MCP server entry point."""

from fastmcp import FastMCP

mcp = FastMCP("ai-research-mcp")

@mcp.tool
def ping() -> str:
    """Health-check tool. Returns 'pong' to verify the server is alive."""
    return "pong"

def main() -> None:
    """Entry point invoked by `uv run ai-research-mcp`."""
    mcp.run()

if __name__ == "__main__":
    main()