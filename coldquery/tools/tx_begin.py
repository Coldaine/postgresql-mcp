from typing import Literal
from coldquery.core.session import session_manager

async def tx_begin(isolation_level: Literal["read_committed", "repeatable_read", "serializable"] = "read_committed") -> str:
    """
    Start a new database transaction.
    Returns a session_id that must be used for subsequent operations.
    """
    return await session_manager.create_session(isolation_level=isolation_level)
