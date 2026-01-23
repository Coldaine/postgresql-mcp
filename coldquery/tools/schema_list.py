from typing import Literal, Optional, List, Dict, Any

async def schema_list(
    target: Literal["schema", "table", "view"],
    schema: str = "public",
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """List database objects."""
    from coldquery.core.database import DatabaseManager

    sql = ""
    args = []

    if target == "schema":
        sql = "SELECT nspname as name FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname != 'information_schema' ORDER BY nspname"
    elif target == "table":
        sql = """
        SELECT schemaname as schema, tablename as name, tableowner as owner, hasindexes as has_indexes
        FROM pg_tables WHERE schemaname = $1 ORDER BY tablename
        """
        args = [schema]
    elif target == "view":
        sql = """
        SELECT n.nspname as schema, c.relname as name,
        CASE c.relkind WHEN 'v' THEN 'view' WHEN 'm' THEN 'materialized_view' END as type
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('v', 'm') AND n.nspname = $1
        ORDER BY n.nspname, c.relname
        """
        args = [schema]
    else:
         raise NotImplementedError(f"Target {target} not fully ported yet")

    # Simple query builder for pagination
    # Note: ORDER BY is already in SQL strings.
    sql += f" LIMIT {limit} OFFSET {offset}"

    db = DatabaseManager()
    conn = await db.get_connection()
    try:
        records = await conn.fetch(sql, *args)
        return [dict(r) for r in records]
    finally:
        await db.release_connection(conn)
