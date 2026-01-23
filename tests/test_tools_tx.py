import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from coldquery.core.session import SessionManager

@pytest.fixture
def mock_session_manager():
    with patch("coldquery.core.session.session_manager") as mock:
        mock.create_session = AsyncMock(return_value="tx_123")
        mock.get_session = MagicMock() # Sync method
        mock.close_session = AsyncMock()
        mock.list_sessions = lambda: [{"id": "tx_123"}]
        yield mock

@pytest.mark.asyncio
async def test_tx_begin(mock_session_manager):
    from coldquery.tools.tx_begin import tx_begin

    res = await tx_begin(isolation_level="SERIALIZABLE")

    mock_session_manager.create_session.assert_called_once_with(isolation_level="SERIALIZABLE")
    assert res == "tx_123"

@pytest.mark.asyncio
async def test_tx_commit(mock_session_manager):
    from coldquery.tools.tx_commit import tx_commit

    # Mock connection and execute
    conn = AsyncMock()
    mock_session_manager.get_session.return_value = conn

    await tx_commit(session_id="tx_123")

    mock_session_manager.get_session.assert_called_with("tx_123")
    conn.execute.assert_called_with("COMMIT")
    mock_session_manager.close_session.assert_called_with("tx_123")

@pytest.mark.asyncio
async def test_tx_rollback(mock_session_manager):
    from coldquery.tools.tx_rollback import tx_rollback

    conn = AsyncMock()
    mock_session_manager.get_session.return_value = conn

    await tx_rollback(session_id="tx_123")

    conn.execute.assert_called_with("ROLLBACK")
    mock_session_manager.close_session.assert_called_with("tx_123")

@pytest.mark.asyncio
async def test_tx_list(mock_session_manager):
    from coldquery.tools.tx_list import tx_list

    res = await tx_list()
    assert len(res) == 1
    assert res[0]["id"] == "tx_123"
