import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { PostgresExecutor } from "@pg-mcp/shared/executor/postgres.js";
import { pgQueryTool } from "./tools/pg-query.js";
import { pgSchemaTool } from "./tools/pg-schema.js";
import { pgAdminTool } from "./tools/pg-admin.js";
import { pgMonitorTool } from "./tools/pg-monitor.js";
import { pgTxTool } from "./tools/pg-tx.js";
import { setupHttpTransport } from "./transports/http.js";

const server = new McpServer({
    name: "pg-mcp-core",
    version: "1.0.0",
});

const executor = new PostgresExecutor({
    host: process.env.PGHOST || "localhost",
    port: parseInt(process.env.PGPORT || "5432"),
    user: process.env.PGUSER || "postgres",
    password: process.env.PGPASSWORD || "postgres",
    database: process.env.PGDATABASE || "postgres",
});

const context = { executor };

// Register all tools using the plugin pattern
const tools = [
    pgQueryTool,
    pgSchemaTool,
    pgAdminTool,
    pgMonitorTool,
    pgTxTool
];

for (const tool of tools) {
    console.error(`[server] registering tool: ${tool.name}`);
    server.registerTool(
        tool.name,
        tool.config,
        async (params) => {
            const result = await tool.handler(context)(params);
            return {
                content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
            };
        }
    );
}

async function main() {
    const transportType = process.argv.includes("--transport")
        ? process.argv[process.argv.indexOf("--transport") + 1]
        : "stdio";

    if (transportType === "sse" || transportType === "http") {
        const port = parseInt(process.env.PORT || "3000");
        await setupHttpTransport(server, port);
    } else {
        const transport = new StdioServerTransport();
        await server.connect(transport);
        console.error("PostgreSQL MCP Server running on stdio");
    }
}

main().catch(console.error);
