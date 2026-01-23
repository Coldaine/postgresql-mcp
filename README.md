# ColdQuery (FastMCP 3.0 Refactor)

A secure, stateful PostgreSQL MCP server optimized for Agentic AI workflows, rebuilt with **FastMCP 3.0**.

## Features

- **FastMCP 3.0 Architecture**: Uses Providers and Transforms for modularity.
- **Transactional Safety**: Default-Deny write policy.
- **Stateful Sessions**: Persistent transactions (`pg_tx`) with `asyncpg` connection pooling.
- **Security**: Dangerous tools are locked by default and require session unlock.

## Installation

```bash
git clone https://github.com/Coldaine/ColdQuery.git
cd ColdQuery
pip install -e .
```

## Configuration

Set `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
```

## Running

```bash
# Start the server
fastmcp run coldquery/server.py

# Or with hot reload
fastmcp run coldquery/server.py --reload
```

## Tools

### Query
*   `query_read`: Execute SELECT queries.
*   `query_write`: Execute INSERT/UPDATE/DELETE (Requires session or autocommit).
*   `query_explain`: Explain query plans.

### Transactions
*   `tx_begin`: Start a transaction session.
*   `tx_commit`: Commit and close session.
*   `tx_rollback`: Rollback and close session.
*   `tx_list`: List active sessions.

### Schema (DDL)
*   `schema_list`: List tables, views, schemas.
*   `schema_describe`: Describe table structure.
*   `schema_create`: Create tables/views/indexes.
*   `schema_alter`: Alter tables.
*   `schema_drop`: Drop objects.

### Admin & Monitor
*   `admin_vacuum`: Run VACUUM.
*   `monitor_activity`: Show active queries.
*   `auth_unlock`: Unlock dangerous tools (schema, admin, write) for the current session.

## Development

```bash
# Run tests
pytest
```
