from typing import Optional, List, Dict, Any

async def query_read(sql: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Execute a read-only SQL query (SELECT).
    """
    from coldquery.core.session import session_manager
    from coldquery.core.database import DatabaseManager

    if session_id:
        conn = session_manager.get_session(session_id)
        if not conn:
            raise ValueError(f"Session {session_id} not found or expired")
        records = await conn.fetch(sql)
        return [dict(r) for r in records]
    else:
        db = DatabaseManager()
        conn = await db.get_connection()
        try:
            records = await conn.fetch(sql)
            return [dict(r) for r in records]
        finally:
            await db.release_connection(conn)
