from typing import Optional

async def query_write(sql: str, session_id: Optional[str] = None, autocommit: bool = False) -> str:
    """
    Execute a write SQL query (INSERT, UPDATE, DELETE, etc.).
    Requires either an active session_id OR autocommit=True.
    """
    from coldquery.core.session import session_manager
    from coldquery.core.database import DatabaseManager

    if not session_id and not autocommit:
        raise ValueError("Safety Error: Write operations require 'session_id' (safe transaction) or 'autocommit=True' (immediate execution).")

    if session_id:
        conn = session_manager.get_session(session_id)
        if not conn:
            raise ValueError(f"Session {session_id} not found or expired")
        return await conn.execute(sql)
    else:
        db = DatabaseManager()
        conn = await db.get_connection()
        try:
            return await conn.execute(sql)
        finally:
            await db.release_connection(conn)
