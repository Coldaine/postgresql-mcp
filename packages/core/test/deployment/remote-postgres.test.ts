/**
 * Deployment Tests - Remote PostgreSQL
 *
 * These tests verify the MCP server works against a real remote PostgreSQL instance.
 * Target: Raspberry Pi (raspberryoracle) via Tailscale
 *
 * Run with: RUN_DEPLOYMENT_TESTS=true npm test -- --testPathPattern=deployment
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { PostgresExecutor } from "../../../../shared/executor/postgres.js";
import { SessionManager } from "../../src/session.js";
import { pgQueryHandler } from "../../src/tools/pg-query.js";
import { pgSchemaHandler } from "../../src/tools/pg-schema.js";
import { pgMonitorHandler } from "../../src/tools/pg-monitor.js";
import { deploymentConfig, isDeploymentTestEnabled } from "./config.js";

describe.skipIf(!isDeploymentTestEnabled())(`Deployment: ${deploymentConfig.name}`, () => {
    let executor: PostgresExecutor;
    let context: { executor: PostgresExecutor; sessionManager: SessionManager };

    beforeAll(async () => {
        console.log(`Connecting to ${deploymentConfig.name} at ${deploymentConfig.host}:${deploymentConfig.port}`);

        executor = new PostgresExecutor({
            host: deploymentConfig.host,
            port: deploymentConfig.port,
            user: deploymentConfig.user,
            password: deploymentConfig.password,
            database: deploymentConfig.database,
        });

        const sessionManager = new SessionManager(executor);
        context = { executor, sessionManager };

        // Verify connection
        const result = await executor.execute("SELECT 1 as connected");
        expect(result.rows[0].connected).toBe(1);
        console.log(`Connected successfully to ${deploymentConfig.name}`);
    });

    afterAll(async () => {
        await executor.disconnect();
    });

    describe("pg_query", () => {
        it("should execute read queries against remote database", async () => {
            const result = await pgQueryHandler({
                action: "read",
                sql: "SELECT COUNT(*) as count FROM test_products",
            }, context);

            expect(parseInt(result.rows[0].count)).toBeGreaterThan(0);
        });

        it("should handle parameterized queries", async () => {
            const result = await pgQueryHandler({
                action: "read",
                sql: "SELECT * FROM test_products WHERE id = $1",
                params: [1],
            }, context);

            expect(result.rows.length).toBe(1);
            expect(result.rows[0].id).toBe(1);
        });

        it("should execute write operations in transaction", async () => {
            // Create a test table for this run
            const tableName = `deploy_test_${Date.now()}`;

            await executor.execute(`CREATE TABLE ${tableName} (id SERIAL, value TEXT)`);

            try {
                const result = await pgQueryHandler({
                    action: "write",
                    sql: `INSERT INTO ${tableName} (value) VALUES ($1)`,
                    params: ["deployment test"],
                    autocommit: true,
                }, context);

                expect(result.rowCount).toBe(1);

                // Verify
                const verify = await executor.execute(`SELECT value FROM ${tableName}`);
                expect(verify.rows[0].value).toBe("deployment test");
            } finally {
                await executor.execute(`DROP TABLE ${tableName}`);
            }
        });

        it("should execute batch transactions atomically", async () => {
            const tableName = `deploy_batch_${Date.now()}`;
            await executor.execute(`CREATE TABLE ${tableName} (id INT UNIQUE)`);

            try {
                const result = await pgQueryHandler({
                    action: "transaction",
                    operations: [
                        { sql: `INSERT INTO ${tableName} VALUES (1)` },
                        { sql: `INSERT INTO ${tableName} VALUES (2)` },
                        { sql: `INSERT INTO ${tableName} VALUES (3)` },
                    ],
                }, context);

                expect(result.status).toBe("committed");
                expect(result.results.length).toBe(3);

                const verify = await executor.execute(`SELECT COUNT(*) as cnt FROM ${tableName}`);
                expect(verify.rows[0].cnt).toBe("3");
            } finally {
                await executor.execute(`DROP TABLE ${tableName}`);
            }
        });

        it("should rollback batch transaction on failure", async () => {
            const tableName = `deploy_rollback_${Date.now()}`;
            await executor.execute(`CREATE TABLE ${tableName} (id INT UNIQUE)`);

            try {
                await expect(pgQueryHandler({
                    action: "transaction",
                    operations: [
                        { sql: `INSERT INTO ${tableName} VALUES (1)` },
                        { sql: `INSERT INTO ${tableName} VALUES (1)` }, // Duplicate - will fail
                    ],
                }, context)).rejects.toThrow();

                // Should be empty due to rollback
                const verify = await executor.execute(`SELECT COUNT(*) as cnt FROM ${tableName}`);
                expect(verify.rows[0].cnt).toBe("0");
            } finally {
                await executor.execute(`DROP TABLE ${tableName}`);
            }
        });
    });

    describe("pg_schema", () => {
        it("should list tables in remote database", async () => {
            const result = await pgSchemaHandler({
                action: "list",
                target: "table",
            }, context);

            expect(result.rows.length).toBeGreaterThan(0);
            const tableNames = result.rows.map((t: any) => t.name);
            expect(tableNames).toContain("test_products");
        });

        it("should describe table structure", async () => {
            const result = await pgSchemaHandler({
                action: "describe",
                target: "table",
                name: "test_products",
            }, context);

            expect(result.columns.length).toBeGreaterThan(0);
            const columnNames = result.columns.map((c: any) => c.name);
            expect(columnNames).toContain("id");
            expect(columnNames).toContain("name");
            expect(columnNames).toContain("price");
        });

        it("should list views", async () => {
            const result = await pgSchemaHandler({
                action: "list",
                target: "view",
            }, context);

            // Should have at least our test view
            expect(result.rows.length).toBeGreaterThan(0);
        });
    });

    describe("pg_monitor", () => {
        it("should check database health", async () => {
            const result = await pgMonitorHandler({
                action: "health",
            }, context);

            expect(result.status).toBe("healthy");
            expect(result.version).toContain("PostgreSQL");
        });

        it("should retrieve connection info", async () => {
            const result = await pgMonitorHandler({
                action: "connections",
            }, context);

            expect(result.rows).toBeDefined();
        });

        it("should retrieve database size", async () => {
            const result = await pgMonitorHandler({
                action: "size",
            }, context);

            expect(result.rows).toBeDefined();
        });
    });

    describe("Performance", () => {
        it("should handle concurrent queries", async () => {
            const queries = Array(10).fill(null).map((_, i) =>
                pgQueryHandler({
                    action: "read",
                    sql: `SELECT $1::int as query_num, COUNT(*) as cnt FROM test_measurements`,
                    params: [i],
                }, context)
            );

            const results = await Promise.all(queries);

            expect(results.length).toBe(10);
            results.forEach((r, i) => {
                expect(r.rows[0].query_num).toBe(i);
            });
        });

        it("should complete complex query within reasonable time", async () => {
            const start = Date.now();

            await pgQueryHandler({
                action: "read",
                sql: `
                    SELECT
                        p.name,
                        COUNT(o.id) as order_count,
                        SUM(o.total_price) as revenue
                    FROM test_products p
                    LEFT JOIN test_orders o ON p.id = o.product_id
                    GROUP BY p.name
                    ORDER BY revenue DESC NULLS LAST
                `,
            }, context);

            const elapsed = Date.now() - start;

            // Should complete within 5 seconds over network
            expect(elapsed).toBeLessThan(5000);
        });
    });

    describe("Data Integrity", () => {
        it("should preserve data types correctly", async () => {
            const result = await pgQueryHandler({
                action: "read",
                sql: `
                    SELECT
                        id,
                        name,
                        price,
                        created_at
                    FROM test_products
                    LIMIT 1
                `,
            }, context);

            const row = result.rows[0];

            expect(typeof row.id).toBe("number");
            expect(typeof row.name).toBe("string");
            // Price comes back as string from pg driver for DECIMAL
            expect(typeof row.price).toBe("string");
            expect(row.created_at instanceof Date).toBe(true);
        });

        it("should handle JSONB data", async () => {
            const result = await pgQueryHandler({
                action: "read",
                sql: "SELECT metadata, tags FROM test_jsonb_docs WHERE id = 1",
            }, context);

            const row = result.rows[0];
            expect(typeof row.metadata).toBe("object");
            expect(row.metadata.type).toBe("article");
            expect(Array.isArray(row.tags)).toBe(true);
        });
    });
});
