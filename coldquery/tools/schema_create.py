from typing import Literal, Optional
from coldquery.utils.security import sanitize_identifier

async def schema_create(
    target: Literal["table", "index", "view"],
    name: str,
    definition: str,
    schema: str = "public",
    session_id: Optional[str] = None,
    autocommit: bool = False,
    if_not_exists: bool = False
) -> str:
    """Create a database object (table, index, view)."""
    from coldquery.core.database import DatabaseManager
    from coldquery.core.session import session_manager

    if not session_id and not autocommit:
        raise ValueError("Safety Error: DDL requires 'session_id' or 'autocommit=True'.")

    safe_name = sanitize_identifier(name)
    safe_schema = sanitize_identifier(schema)
    full_name = f"{safe_schema}.{safe_name}"

    sql = ""
    if target == "table":
        ine = "IF NOT EXISTS " if if_not_exists else ""
        sql = f"CREATE TABLE {ine}{full_name} ({definition})"
    elif target == "index":
        # For index, name is the index name. definition is "table_name (columns)"
        sql = f"CREATE INDEX {safe_name} ON {safe_schema}.{definition}"
    elif target == "view":
        sql = f"CREATE VIEW {full_name} AS {definition}"
    else:
        raise ValueError(f"Unknown target: {target}")

    if session_id:
        conn = session_manager.get_session(session_id)
        if not conn: raise ValueError(f"Session {session_id} not found")
        await conn.execute(sql)
    else:
        db = DatabaseManager()
        conn = await db.get_connection()
        try:
            await conn.execute(sql)
        finally:
            await db.release_connection(conn)

    return f"Created {target} {full_name}"
