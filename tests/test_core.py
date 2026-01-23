import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from coldquery.core.session import SessionManager
from coldquery.core.database import DatabaseManager

@pytest.fixture
def mock_db_manager():
    manager = MagicMock(spec=DatabaseManager)
    manager.get_connection = AsyncMock(return_value=AsyncMock())
    return manager

@pytest.fixture(autouse=True)
def reset_singletons():
    SessionManager._instance = None
    DatabaseManager._instance = None
    yield
    SessionManager._instance = None
    DatabaseManager._instance = None

@pytest.mark.asyncio
async def test_session_manager_create_session(mock_db_manager):
    session_manager = SessionManager(db_manager=mock_db_manager)
    session_id = await session_manager.create_session()

    assert session_id is not None
    assert isinstance(session_id, str)
    assert session_manager.get_session(session_id) is not None
    mock_db_manager.get_connection.assert_called_once()

@pytest.mark.asyncio
async def test_session_manager_close_session(mock_db_manager):
    session_manager = SessionManager(db_manager=mock_db_manager)
    session_id = await session_manager.create_session()

    conn = session_manager.get_session(session_id)
    assert conn is not None

    await session_manager.close_session(session_id)
    assert session_manager.get_session(session_id) is None

    # Verify connection was released
    mock_db_manager.release_connection.assert_called_once_with(conn)

@pytest.mark.asyncio
async def test_session_manager_ttl_cleanup(mock_db_manager):
    session_manager = SessionManager(db_manager=mock_db_manager, ttl_seconds=0.1)
    session_id = await session_manager.create_session()

    conn = session_manager.get_session(session_id)
    assert conn is not None

    # Wait for TTL
    await asyncio.sleep(0.2)

    # Force cleanup call (since it runs on access/create usually)
    # The actual implementation calls it on create_session.
    # We can call it directly for test
    await session_manager.cleanup_expired_async()

    assert session_manager.get_session(session_id) is None
    mock_db_manager.release_connection.assert_called_with(conn)
