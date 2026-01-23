import { Resource } from "fastmcp";
import { ActionContext } from "../types.js";
import { observabilityHandler } from "../actions/monitor/observability.js";

export function getPgMonitorResources(context: ActionContext): Resource<any>[] {
    return [
        {
            uri: "postgres://monitor/activity",
            name: "Database Activity",
            description: "Current active queries and sessions",
            mimeType: "application/json",
            async load() {
                const result = await observabilityHandler.handler({
                    action: "activity"
                }, context);
                return {
                    text: JSON.stringify(result, null, 2)
                };
            }
        },
        {
            uri: "postgres://monitor/locks",
            name: "Database Locks",
            description: "Current active locks",
            mimeType: "application/json",
            async load() {
                const result = await observabilityHandler.handler({
                    action: "locks"
                }, context);
                return {
                    text: JSON.stringify(result, null, 2)
                };
            }
        }
    ];
}
