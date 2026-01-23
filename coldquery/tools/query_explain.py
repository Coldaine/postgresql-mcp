from typing import List, Dict, Any

async def query_explain(sql: str, analyze: bool = False) -> List[Dict[str, Any]]:
    """
    Analyze query execution plan (supports EXPLAIN ANALYZE).
    """
    from coldquery.core.database import DatabaseManager

    prefix = "EXPLAIN (ANALYZE, FORMAT JSON) " if analyze else "EXPLAIN (FORMAT JSON) "
    full_sql = prefix + sql

    db = DatabaseManager()
    conn = await db.get_connection()
    try:
        records = await conn.fetch(full_sql)
        return [dict(r) for r in records]
    finally:
        await db.release_connection(conn)
