import { FastMCP } from "fastmcp";
import { ActionContext } from "../types.js";

export function registerSchemaResource(server: FastMCP, context: ActionContext) {
    server.addResource({
        uri: "postgres://schema",
        name: "Database Schema",
        description: "A JSON representation of all tables in the public schema",
        mimeType: "application/json",
        load: async () => {
            const result = await context.executor.execute(
                `SELECT table_name
                 FROM information_schema.tables
                 WHERE table_schema = 'public'
                 ORDER BY table_name`,
                []
            );
            return {
                text: JSON.stringify(result.rows, null, 2),
            };
        },
    });
}
