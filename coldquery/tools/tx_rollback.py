from coldquery.core.session import session_manager

async def tx_rollback(session_id: str) -> str:
    """
    Rollback an open transaction and close the session.
    """
    conn = session_manager.get_session(session_id)
    if not conn:
        raise ValueError(f"Session {session_id} not found or expired")

    await conn.execute("ROLLBACK")
    await session_manager.close_session(session_id)
    return "Transaction rolled back"
