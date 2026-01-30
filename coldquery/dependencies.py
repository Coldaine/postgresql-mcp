"""Custom FastMCP dependencies for ColdQuery."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastmcp.dependencies import CurrentContext, Depends
from fastmcp.server.context import Context

if TYPE_CHECKING:
    from coldquery.core.context import ActionContext


def get_action_context(ctx: Context = CurrentContext()) -> ActionContext:
    """Get the ActionContext from server lifespan."""
    action_context = ctx.lifespan_context.get("action_context")
    if action_context is None:
        raise RuntimeError(
            "ActionContext not found in server lifespan. "
            "Ensure the lifespan context manager sets action_context."
        )
    return cast("ActionContext", action_context)


def CurrentActionContext() -> ActionContext:
    """Get the current ActionContext instance.

    This dependency provides access to the ActionContext which contains
    the database executor and session manager.

    Returns:
        A dependency that resolves to the active ActionContext instance

    Raises:
        RuntimeError: If no active ActionContext found

    Example:
        ```python
        from coldquery.dependencies import CurrentActionContext

        @mcp.tool()
        async def my_query(
            sql: str,
            ctx: ActionContext = CurrentActionContext()
        ) -> str:
            executor = ctx.executor
            result = await executor.execute(sql)
            return json.dumps(result.to_dict())
        ```
    """
    return Depends(get_action_context)
