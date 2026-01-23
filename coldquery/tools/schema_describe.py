from typing import Literal, Dict, Any

async def schema_describe(target: Literal["table"], name: str, schema: str = "public") -> Dict[str, Any]:
    """Get detailed structure of a database object."""
    from coldquery.core.database import DatabaseManager

    if target != "table":
        raise NotImplementedError(f"Describe target {target} not implemented yet")

    db = DatabaseManager()
    conn = await db.get_connection()
    try:
        # Get columns
        columns_sql = """
            SELECT
                column_name as name,
                data_type as type,
                is_nullable as nullable,
                column_default as default_value
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position;
        """
        columns = await conn.fetch(columns_sql, schema, name)

        # Get indexes
        indexes_sql = """
            SELECT indexname as name, indexdef as definition
            FROM pg_indexes
            WHERE schemaname = $1 AND tablename = $2;
        """
        indexes = await conn.fetch(indexes_sql, schema, name)

        return {
            "name": name,
            "schema": schema,
            "columns": [dict(r) for r in columns],
            "indexes": [dict(r) for r in indexes],
        }
    finally:
        await db.release_connection(conn)
