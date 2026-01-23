from typing import List, Dict, Any
from coldquery.core.database import DatabaseManager

async def monitor_activity() -> List[Dict[str, Any]]:
    """Show current database activity (active queries)."""
    sql = "SELECT * FROM pg_stat_activity WHERE state != 'idle'"

    db = DatabaseManager()
    conn = await db.get_connection()
    try:
        records = await conn.fetch(sql)
        # Convert datetime/etc to string if needed, but fastmcp might handle it.
        # asyncpg returns datetime objects.
        return [dict(r) for r in records]
    finally:
        await db.release_connection(conn)
