# ColdQuery TODO

Tracked work items for the ColdQuery PostgreSQL MCP server.

---

## High Priority

### Integration Test Fixtures
The integration tests (`tests/integration/`) have known async fixture lifecycle issues:
- Session-scoped async fixtures (`real_db_pool`) may cause event loop errors during teardown
- `AsyncpgPoolExecutor` creates its own pool, so `real_db_pool` fixture creates a redundant pool
- Function-scoped fixtures should be preferred for test isolation

**Action**: Refactor integration test fixtures to use function-scoped `AsyncpgPoolExecutor` and remove redundant `real_db_pool` fixture. See `docs/OBSERVATIONS.md` for detailed analysis.

### Schema List - Missing Target Types
`coldquery/actions/schema/list.py` only supports 3 target types (table, view, schema). The TypeScript version supports 7:
- [ ] function
- [ ] trigger
- [ ] sequence
- [ ] constraint

### Schema List - Unused Parameters
`schema` and `include_sizes` parameters are accepted but not wired up:
- [ ] Wire up schema filtering in list queries
- [ ] Wire up include_sizes option (add `pg_total_relation_size()`)

## Medium Priority

### Connection Pool Monitoring
No metrics or observability for the connection pool itself:
- [ ] Track pool size, idle connections, active connections
- [ ] Add pool stats to health check response

### Logging Consistency
Some error paths use different patterns:
- [ ] Ensure all handlers log errors consistently via `core/logger.py`
- [ ] Add request-scoped correlation IDs

### Settings Handler
`coldquery/actions/admin/settings.py`:
- [ ] Add category filtering for `pg_settings` list (ILIKE filter)
- [ ] Add pagination (LIMIT/OFFSET) for settings list

## Low Priority

### Auth Module
`security/auth.py` exists in the plan but is not yet implemented:
- [ ] Implement `COLDQUERY_AUTH_ENABLED` env var toggle
- [ ] Implement `auth_unlock` tool for token-based authentication
- [ ] Add `require_auth()` middleware hook

### Performance
- [ ] Add connection pool tuning options (min/max size, timeout)
- [ ] Add query result caching for repeated schema/monitor queries
- [ ] Benchmark tool response times

### Documentation
- [ ] Add API reference for all 5 tools with example requests/responses
- [ ] Add troubleshooting guide for common PostgreSQL errors
- [ ] Update OBSERVATIONS.md with PR #32 findings

---

## Completed

### PR #32 (2026-01-28)
- [x] Docker multi-stage build
- [x] GitHub Actions CI workflow (lint, test, docker build)
- [x] GitHub Actions deploy workflow (ARM64 + Tailscale + SSH)
- [x] Production docker-compose with Tailscale sidecar
- [x] Fixed all runtime bugs (health handler, session echo, executor disconnect, JSON serialization)
- [x] Live-tested all 5 MCP tools against real PostgreSQL (28/28 pass)
- [x] 71 unit tests passing
