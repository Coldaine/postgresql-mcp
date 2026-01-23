import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_managers():
    # Patch at the source where tools import from
    with patch("coldquery.core.session.session_manager") as sm, \
         patch("coldquery.core.database.DatabaseManager") as db_class:

        # Setup common mocks
        conn = AsyncMock()
        # Singleton returns instance
        db_instance = db_class.return_value
        db_instance.get_connection = AsyncMock(return_value=conn)
        db_instance.release_connection = AsyncMock()
        sm.get_session.return_value = conn

        yield {"conn": conn, "sm": sm}

@pytest.mark.asyncio
async def test_schema_create_table(mock_managers):
    from coldquery.tools.schema_create import schema_create
    conn = mock_managers["conn"]
    conn.execute = AsyncMock()

    await schema_create("table", "users", "id INT", autocommit=True)

    conn.execute.assert_called_once()
    sql = conn.execute.call_args[0][0]
    assert 'CREATE TABLE "public"."users" (id INT)' in sql

@pytest.mark.asyncio
async def test_schema_create_table_transaction(mock_managers):
    from coldquery.tools.schema_create import schema_create
    conn = mock_managers["conn"]
    conn.execute = AsyncMock()

    await schema_create("table", "users", "id INT", session_id="tx_1")

    mock_managers["sm"].get_session.assert_called_with("tx_1")
    conn.execute.assert_called_once()
    assert 'CREATE TABLE "public"."users" (id INT)' in conn.execute.call_args[0][0]

@pytest.mark.asyncio
async def test_schema_list(mock_managers):
    from coldquery.tools.schema_list import schema_list
    conn = mock_managers["conn"]
    conn.fetch = AsyncMock(return_value=[{"tablename": "users"}])

    res = await schema_list("table")
    assert res == [{"tablename": "users"}]
    # Check SQL contains pg_tables
    args = conn.fetch.call_args
    assert "pg_tables" in args[0][0]
