import uuid
import time
import asyncio
from typing import Dict, Optional
from .database import DatabaseManager
import asyncpg

class SessionData:
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection
        self.last_active = time.time()
        self.created_at = time.time()

class SessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_manager: DatabaseManager = None, ttl_seconds: int = 1800, max_sessions: int = 10):
        if hasattr(self, 'sessions'):
            return # Already initialized

        self.sessions: Dict[str, SessionData] = {}
        self.db_manager = db_manager or DatabaseManager()
        self.ttl_seconds = ttl_seconds
        self.max_sessions = max_sessions

    async def create_session(self, isolation_level: str = None) -> str:
        """Creates a new session with a dedicated database connection."""
        await self.cleanup_expired_async()

        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(f"Maximum session limit ({self.max_sessions}) reached.")

        session_id = f"tx_{uuid.uuid4().hex[:8]}" # Matches format in README: tx_abc123
        connection = await self.db_manager.get_connection()

        # Start transaction
        try:
            iso_clause = ""
            if isolation_level:
                # Basic sanitation, though usually provided by enum in tool
                valid_levels = {"SERIALIZABLE", "REPEATABLE READ", "READ COMMITTED", "READ UNCOMMITTED"}
                normalized = isolation_level.upper().replace("_", " ")
                if normalized in valid_levels:
                    iso_clause = f" ISOLATION LEVEL {normalized}"

            await connection.execute(f"BEGIN{iso_clause}")
        except Exception:
            await self.db_manager.release_connection(connection)
            raise

        self.sessions[session_id] = SessionData(connection)
        return session_id

    def get_session(self, session_id: str) -> Optional[asyncpg.Connection]:
        """Retrieves the connection for a session and updates last_active."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check expiry
        if time.time() - session.last_active > self.ttl_seconds:
            # We cannot async close here because this method is sync.
            # We return None to indicate invalid/expired.
            # Cleanup will happen on next create_session or if we add a background task.
            return None

        session.last_active = time.time()
        return session.connection

    async def close_session(self, session_id: str):
        """Closes a session and releases the connection."""
        session = self.sessions.pop(session_id, None)
        if session:
            await self.db_manager.release_connection(session.connection)

    async def cleanup_expired_async(self):
        """Removes expired sessions and closes their connections."""
        now = time.time()
        expired_ids = [
            sid for sid, data in self.sessions.items()
            if now - data.last_active > self.ttl_seconds
        ]
        for sid in expired_ids:
            await self.close_session(sid)

    def list_sessions(self):
        now = time.time()
        return [
            {
                "id": sid,
                "idle_time": f"{int(now - data.last_active)}s",
                "expires_in": f"{int((data.last_active + self.ttl_seconds - now) / 60)}m"
            }
            for sid, data in self.sessions.items()
        ]

# Global instance
session_manager = SessionManager()
