import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_db_manager():
    # We patch the class so when tools instantiate it, they get our mock
    with patch("coldquery.core.database.DatabaseManager") as MockClass:
        # Singleton behavior: calling DatabaseManager() returns the SAME mock
        instance = MockClass.return_value
        instance.get_connection = AsyncMock()
        instance.release_connection = AsyncMock()
        yield instance

@pytest.fixture
def mock_session_manager():
    with patch("coldquery.core.session.session_manager") as mock:
        mock.get_session = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_query_read_stateless(mock_db_manager, mock_session_manager):
    from coldquery.tools.query_read import query_read

    # Setup mock connection
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[{"id": 1}])
    mock_db_manager.get_connection.return_value = conn

    res = await query_read("SELECT * FROM users")

    mock_db_manager.get_connection.assert_called_once()
    conn.fetch.assert_called_with("SELECT * FROM users")
    mock_db_manager.release_connection.assert_called_with(conn)
    assert res == [{"id": 1}]

@pytest.mark.asyncio
async def test_query_read_stateful(mock_db_manager, mock_session_manager):
    from coldquery.tools.query_read import query_read

    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[{"id": 1}])
    mock_session_manager.get_session.return_value = conn

    res = await query_read("SELECT * FROM users", session_id="tx_123")

    mock_session_manager.get_session.assert_called_with("tx_123")
    conn.fetch.assert_called_with("SELECT * FROM users")
    # Should NOT release connection from session
    mock_db_manager.release_connection.assert_not_called()
    assert res == [{"id": 1}]

@pytest.mark.asyncio
async def test_query_write_blocked(mock_db_manager, mock_session_manager):
    from coldquery.tools.query_write import query_write

    with pytest.raises(ValueError, match="Safety Error"):
        await query_write("INSERT INTO users VALUES (1)")

@pytest.mark.asyncio
async def test_query_write_autocommit(mock_db_manager, mock_session_manager):
    from coldquery.tools.query_write import query_write

    conn = AsyncMock()
    conn.execute = AsyncMock(return_value="INSERT 0 1")
    mock_db_manager.get_connection.return_value = conn

    res = await query_write("INSERT INTO users VALUES (1)", autocommit=True)

    conn.execute.assert_called_with("INSERT INTO users VALUES (1)")
    mock_db_manager.release_connection.assert_called_with(conn)
    assert res == "INSERT 0 1"

@pytest.mark.asyncio
async def test_query_write_stateful(mock_db_manager, mock_session_manager):
    from coldquery.tools.query_write import query_write

    conn = AsyncMock()
    conn.execute = AsyncMock(return_value="UPDATE 1")
    mock_session_manager.get_session.return_value = conn

    res = await query_write("UPDATE users SET x=1", session_id="tx_123")

    mock_session_manager.get_session.assert_called_with("tx_123")
    conn.execute.assert_called_with("UPDATE users SET x=1")
    mock_db_manager.release_connection.assert_not_called()
