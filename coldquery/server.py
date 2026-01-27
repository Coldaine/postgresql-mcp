import os
import sys

from fastmcp import FastMCP

from coldquery.core.context import ActionContext
from coldquery.core.executor import db_executor
from coldquery.core.session import session_manager
from coldquery.tools.pg_query import pg_query

mcp = FastMCP(
    name="coldquery",
    version="1.0.0",
    instructions=(
        "ColdQuery PostgreSQL MCP Server - Execute SQL queries safely with session"
        " management and transaction support."
    ),
)


# Dependency injection for tools
@mcp.context_provider
async def context_provider() -> ActionContext:
    """Provides the action context to tools."""
    return ActionContext(executor=db_executor, session_manager=session_manager)


# Register pg_query tool
mcp.register(pg_query)


# Health endpoint
@mcp.custom_route("/health")
async def health():
    """Returns the health status of the server."""
    return {"status": "ok"}


if __name__ == "__main__":
    transport = (
        "http" if "--transport" in sys.argv and "http" in sys.argv else "stdio"
    )

    if transport == "http":
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", "3000"))
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()
