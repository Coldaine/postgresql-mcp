import { Resource, ResourceTemplate } from "fastmcp";
import { ActionContext } from "../types.js";
import { listHandler } from "../actions/schema/list.js";
import { describeHandler } from "../actions/schema/describe.js";

export function getPgSchemaResources(context: ActionContext): Resource<any>[] {
    return [
        {
            uri: "postgres://schema/tables",
            name: "List Tables",
            description: "List all tables in the public schema",
            mimeType: "application/json",
            async load() {
                const result = await listHandler.handler({
                    action: "list",
                    target: "table",
                    schema: "public"
                }, context);
                return {
                    text: JSON.stringify(result.rows, null, 2)
                };
            }
        }
    ];
}

export function getPgSchemaResourceTemplates(context: ActionContext): ResourceTemplate<any>[] {
    return [
        {
            uriTemplate: "postgres://schema/table/{schema}/{table}",
            name: "Describe Table",
            description: "Get detailed schema information for a specific table",
            mimeType: "application/json",
            arguments: [
                { name: "schema", description: "Schema name (e.g., public)", required: true },
                { name: "table", description: "Table name", required: true }
            ],
            async load(args) {
                const result = await describeHandler.handler({
                    action: "describe",
                    target: "table",
                    name: args.table,
                    schema: args.schema
                }, context);

                return {
                    text: JSON.stringify(result, null, 2)
                };
            }
        }
    ];
}
