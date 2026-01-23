from typing import List, Dict, Any
from coldquery.core.session import session_manager

async def tx_list() -> List[Dict[str, Any]]:
    """
    List active database sessions.
    """
    return session_manager.list_sessions()
