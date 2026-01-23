from typing import Optional

async def admin_vacuum(table: Optional[str] = None, full: bool = False, analyze: bool = False) -> str:
    """Run VACUUM on the database or specific table."""
    from coldquery.core.database import DatabaseManager
    from coldquery.utils.security import sanitize_identifier

    sql = "VACUUM"
    if full: sql += " FULL"
    if analyze: sql += " ANALYZE"
    if table:
        sql += f" {sanitize_identifier(table)}"

    db = DatabaseManager()
    conn = await db.get_connection()
    try:
        # VACUUM cannot run inside a transaction block.
        # Ensure we are not.
        await conn.execute(sql)
        return "Vacuum completed"
    finally:
        await db.release_connection(conn)
