# Refactoring & Reduction Strategies

This document outlines two distinct approaches for refactoring the `postgresql-mcp` codebase. Each approach includes a specific "Prompt" designed to be fed to an AI agent to execute the strategy, along with the rationale and detailed steps.

---

## Option 1: The "Architectural Purity" Approach (Scalability & SOLID)

**Philosophy**: Prioritize strict Type Safety, Dependency Injection, and Testability. Isolate the "MCP" layer from the "Business/Database" layer to allow for easier testing and future database swaps.

### 🤖 Agent Prompt
> "Act as a Senior Software Architect. Your goal is to refactor the `postgresql-mcp` monorepo to adhere to strict SOLID principles and Clean Architecture. 
> 
> Currently, the code couples MCP tool definitions directly with implementation logic. 
> 
> Please execute the following plan:
> 1. **Implement the Repository Pattern**: Refactor `shared/executor` to expose strongly-typed Repositories (e.g., `SchemaRepository`, `StatsRepository`) instead of raw SQL strings scattered in actions.
> 2. **Dependency Injection**: Refactor the Action handlers to accept these Repositories as dependencies, replacing any direct global imports of the database connection.
> 3. **Layer Separation**: Ensure `packages/core/src/tools` contains *only* the MCP-specific wiring (Zod schemas, request handling) and delegates all actual logic to `packages/core/src/domain` (or `actions`).
> 4. **Strict Typing**: Enforce strict return types for all database queries using Zod to validate data coming *out* of the DB, ensuring runtime safety.
> 
> Focus on testability and clear interfaces."

### 📝 Detailed Plan

1.  **Refactor `shared/executor`**:
    *   Create a generic `IDatabaseExecutor` interface.
    *   Implement a concrete `PostgresExecutor` using the singleton pattern for the pool.
    *   Create domain-specific Repositories (e.g., `PgSchemaRepository`, `PgAdminRepository`) that consume `IDatabaseExecutor`.
2.  **Refactor `packages/core/src/actions`**:
    *   Convert standalone functions into Service Classes (e.g., `SchemaService`).
    *   Inject repositories into these services.
3.  **Refactor `packages/core/src/tools`**:
    *   Rewrite tool definitions to purely handle:
        *   Input validation (Zod).
        *   Service invocation.
        *   Error mapping (Service Error -> MCP Error).
4.  **Shared Types**:
    *   Move all shared Zod schemas to `shared/types` to be used by both the Repository (for validation) and the Tool (for input).

---

## Option 2: The "Code Collapse" Approach (Reduction & Simplicity)

**Philosophy**: Reduce boilerplate and cognitive load. If a file exists just to call another file, delete it. Use functional programming to compose tools dynamically.

### 🤖 Agent Prompt
> "Act as a Principal Engineer focused on Developer Experience (DX) and Code Reduction. Your goal is to delete as much code as possible while maintaining functionality.
> 
> The current codebase has too many layers of abstraction for a simple MCP server.
> 
> Please execute the following plan:
> 1. **Create an MCP Factory**: Write a high-order function `createBinaryTool` or `createQueryTool` that abstracts away the repetitive Zod parsing and error handling found in every file in `packages/core/src/tools`.
> 2. **Inline Actions**: Where an 'Action' is just a single SQL query, remove the separate file in `src/actions` and move the logic directly into the Tool definition or a consolidated `GenericQueryTool`.
> 3. **Consolidate Files**: Merge scattered 'tool` files (e.g., `pg-schema.ts`, `pg-admin.ts`) into a single logical structure or route handler if they share similar patterns.
> 4. **Simplify Shared**: If `shared/executor/interface.ts` is just re-exporting native driver types, remove it and use the driver types directly to reduce indirection.
> 
> Output metrics on how many lines of code were removed."

### 📝 Detailed Plan

1.  **Boilerplate Destroyer (`ToolFactory`)**:
    *   Create a utility `createTool<Schema>(name, schema, implementation)`.
    *   This utility handles the `try/catch` wrapping, Zod parsing, and MCP error formatting globally.
2.  **Inline Simple Logic**:
    *   Identify "Pass-through" actions (actions that just call `db.query('SELECT...')`).
    *   Move these SQL queries into a mapping object in the Tool file.
    *   Delete the corresponding file in `src/actions`.
3.  **Unified Query Handler**:
    *   Instead of 5 different "read" tools, consider a robust `RunQuery` tool that takes a "Query Key" (safelisted query name) from the client, minimizing not just code but surface area.
4.  **Refactor `packages/core/src/server.ts`**:
    *   Use usage of the `ToolFactory` to register tools in a loop, rather than manually importing and registering each one.

