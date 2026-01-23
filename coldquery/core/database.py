import asyncpg
import os
from typing import Optional

class DatabaseManager:
    _instance = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    async def connect(self, dsn: str = None):
        if self._pool is None:
            if dsn is None:
                dsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

            # Configure pool size to accommodate max sessions (10) + stateless operations (buffer)
            # Default asyncpg is min=10, max=10.
            # We set max=20 to prevent deadlock when sessions exhaust 10 slots.
            self._pool = await asyncpg.create_pool(dsn, min_size=5, max_size=20)

    async def get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            await self.connect()
        return self._pool

    async def get_connection(self) -> asyncpg.Connection:
        """Returns a new dedicated connection (not from pool) or from pool if preferred.
        For sessions, we usually want a dedicated connection to hold transaction state.
        asyncpg pool connections are reset when returned to pool.
        """
        pool = await self.get_pool()
        return await pool.acquire()

    async def release_connection(self, connection: asyncpg.Connection):
        if self._pool:
            await self._pool.release(connection)

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
