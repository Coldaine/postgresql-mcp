import { describe, it, expect, vi, beforeEach } from "vitest";
import { getPgSchemaResources, getPgSchemaResourceTemplates } from "../../src/resources/pg-schema.js";

// Mock the actions to avoid DB dependency
vi.mock("../../src/actions/schema/list.js", () => ({
    listHandler: {
        handler: vi.fn().mockResolvedValue({
            rows: [
                { schema: "public", name: "mock_table" }
            ]
        })
    }
}));

vi.mock("../../src/actions/schema/describe.js", () => ({
    describeHandler: {
        handler: vi.fn().mockResolvedValue({
            columns: [
                { name: "id", type: "integer" }
            ]
        })
    }
}));

describe("pg_schema resources (mock)", () => {
    let context: any;

    beforeEach(() => {
        // Mock context (not used by mocked handlers but required by type)
        context = { executor: {}, sessionManager: {} };
    });

    it("should list tables via resource", async () => {
        const resources = getPgSchemaResources(context);
        const listResource = resources.find(r => r.uri === "postgres://schema/tables");
        expect(listResource).toBeDefined();

        if (listResource && listResource.load) {
             const result = await listResource.load();
             // Result should be { text: string }
             expect(result).toHaveProperty("text");
             const tables = JSON.parse((result as any).text);
             expect(Array.isArray(tables)).toBe(true);
             expect(tables[0].name).toBe("mock_table");
        }
    });

    it("should describe table via resource template", async () => {
        const templates = getPgSchemaResourceTemplates(context);
        const describeTemplate = templates.find(r => r.name === "Describe Table");
        expect(describeTemplate).toBeDefined();

        if (describeTemplate && describeTemplate.load) {
            const result = await describeTemplate.load({ schema: "public", table: "test_resource_table" });
             // Result should be { text: string }
             expect(result).toHaveProperty("text");
             const desc = JSON.parse((result as any).text);
             expect(desc.columns).toBeDefined();
             expect(desc.columns[0].name).toBe("id");
        }
    });
});
