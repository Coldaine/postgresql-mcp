# Changelog

All notable changes to ColdQuery are documented in this file.

---

## [Unreleased] - PR #32 Fixes (2026-01-28)

### Infrastructure Fixes
- **deploy.yml**: Complete rewrite of GitHub Actions deploy workflow
  - Fixed SSH heredoc variable expansion (`<< 'EOF'` -> `<< EOF`)
  - Replaced invalid `readFile()` function with SCP approach
  - Switched to `docker compose` v2 CLI
  - Added `permissions: packages: write` for GHCR push
  - Proper secret injection via `${{ secrets.* }}`
- **docker-compose.deploy.yml**: Fixed production compose
  - Changed image from `coldquery:arm64-latest` to `ghcr.io/coldaine/coldquery:latest`
  - Changed HOST from `100.0.0.0` to `0.0.0.0` (bind all interfaces)
  - Removed deprecated `version: '3.8'`
- **docker-compose.yml**: Removed deprecated `version: '3.8'`

### Runtime Bug Fixes
- **resolve_executor async/sync mismatch**: Changed `def resolve_executor()` to `async def` in `context.py` — all action handlers use `await`, so the function must be async. Fixed 21 unit test failures.
- **health_handler dict index crash**: Fixed `result.rows[0][0]` (KeyError on dict) to `result.rows[0].get("health_check")`. Changed query to `SELECT 1 AS health_check` for explicit column name.
- **session_echo.py AttributeError**: `SessionManager.get_session()` method didn't exist. Added `get_session()` method to `SessionManager` and `id`/`expires_in` properties to `SessionData`.
- **executor.disconnect() crashes**:
  - `AsyncpgPoolExecutor.disconnect()`: Removed `await` from `pool.terminate()` (sync method)
  - `AsyncpgSessionExecutor.disconnect()`: Fixed crash when calling `.close()` after `.release()` on a pool-managed connection
- **JSON serialization**: Added `default=str` to all `json.dumps()` calls that serialize query results. Fixes `TypeError: Object of type IPv4Address is not JSON serializable` and similar for datetime, Decimal, etc.

### Import Migration
- Migrated `resolve_executor` imports from `coldquery.core.executor` to `coldquery.core.context` across all 11 action handler files after removing duplicate function from executor.py

### Test Fixes
- Updated unit test mock data to use dict rows (`[{"health_check": 1}]`) instead of list rows (`[[1]]`) to match real `QueryResult` format
- Fixed integration tests: replaced non-existent `get_all_sessions()` with `list_sessions()` across 6 call sites
- Fixed integration test `get_session()` call to `get_session_executor()` in connection management test
- Updated integration test conftest.py docstring to reflect current state
- Added lint fixes: removed unused imports, added `# noqa: F841` for intentional placeholder variables
- Added live test script (`tests/live_test.py`) covering all 5 MCP tools against real PostgreSQL

### Verification
- 71 unit tests passing
- 28 live integration tests passing (all 5 tools verified against real PostgreSQL)
- All ruff lint checks passing

---

## [1.0.0] - Python Rewrite (2026-01-27)

### Added
- Complete Python rewrite from TypeScript using FastMCP 3.0
- 5 MCP tools: `pg_query`, `pg_schema`, `pg_admin`, `pg_monitor`, `pg_tx`
- 25 action handlers across query, schema, admin, monitor, and transaction domains
- Session management with UUID IDs, 30-minute TTL, max 10 concurrent sessions
- Default-Deny write policy (requires `session_id` or `autocommit=true`)
- SQL identifier sanitization (regex validation + double-quote escaping)
- Session echo middleware (expiry warnings in responses)
- MCP Resources: schema tables, table details, health, activity
- MCP Prompts: query performance analysis, lock contention debugging
- Docker multi-stage build (python:3.12-alpine)
- GitHub Actions CI (lint, unit tests, integration tests, docker build)
- GitHub Actions deploy (ARM64 QEMU build, GHCR push, SSH deploy to Raspberry Pi)
- Tailscale sidecar for production networking
