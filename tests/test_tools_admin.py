import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_managers():
    with patch("coldquery.core.database.DatabaseManager") as db_class:
        conn = AsyncMock()
        db_instance = db_class.return_value
        db_instance.get_connection = AsyncMock(return_value=conn)
        db_instance.release_connection = AsyncMock()
        yield {"conn": conn}

@pytest.mark.asyncio
async def test_admin_vacuum(mock_managers):
    from coldquery.tools.admin_vacuum import admin_vacuum
    conn = mock_managers["conn"]
    conn.execute = AsyncMock()

    await admin_vacuum(table="users", analyze=True)

    conn.execute.assert_called_once()
    assert 'VACUUM ANALYZE "users"' in conn.execute.call_args[0][0]

@pytest.mark.asyncio
async def test_monitor_activity(mock_managers):
    from coldquery.tools.monitor_activity import monitor_activity
    conn = mock_managers["conn"]
    conn.fetch = AsyncMock(return_value=[{"pid": 123}])

    res = await monitor_activity()

    conn.fetch.assert_called_once()
    assert res == [{"pid": 123}]
