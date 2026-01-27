from typing import Any, List, Literal, Optional

from coldquery.actions.query.explain import explain_handler
from coldquery.actions.query.read import read_handler
from coldquery.actions.query.transaction import transaction_handler
from coldquery.actions.query.write import write_handler
from coldquery.core.context import ActionContext

QUERY_ACTIONS = {
    "read": read_handler,
    "write": write_handler,
    "explain": explain_handler,
    "transaction": transaction_handler,
}


async def pg_query(
    action: Literal["read", "write", "explain", "transaction"],
    sql: Optional[str] = None,
    params: Optional[List[Any]] = None,
    analyze: Optional[bool] = None,
    operations: Optional[List[dict]] = None,
    session_id: Optional[str] = None,
    autocommit: Optional[bool] = None,
    mcp_context: Optional[ActionContext] = None,
) -> str:
    """Execute SQL queries with safety controls."""
    handler = QUERY_ACTIONS.get(action)
    if not handler:
        raise ValueError(f"Unknown action: {action}")

    # Prepare params for the handler
    handler_params = {
        "sql": sql,
        "params": params,
        "analyze": analyze,
        "operations": operations,
        "session_id": session_id,
        "autocommit": autocommit,
    }

    if not mcp_context:
        raise ValueError("mcp_context is not set")

    return await handler(handler_params, mcp_context)
