# Option 3: The "Vertical Slices" Approach (Feature-First)

**Philosophy**: Organize code by *Feature* (e.g., `Schema`, `Stats`, `Maintenance`) rather than by technical layer (e.g., `Tools`, `Actions`, `Repositories`). Co-locate everything related to a feature in one folder.

### 🤖 Agent Prompt
> "Act as a Lead Developer adopting Vertical Slice Architecture. Your goal is to reorganize the `postgresql-mcp` codebase to improve cohesion and feature isolation.
> 
> Currently, the code is scattered by technical concern (tools/ vs actions/).
> 
> Please execute the following plan:
> 1.  **Feature Folders**: Create a `packages/core/src/features` directory.
> 2.  **Migrate Logic**: Move all logic for specific features into self-contained folders, e.g., `features/schema/` should contain:
>     *   `schema.tool.ts` (The MCP Tool definition)
>     *   `schema.handler.ts` (The business logic/service)
>     *   `schema.repository.ts` (The raw SQL queries)
>     *   `schema.types.ts` (Zod schemas)
> 3.  **Encapsulation**: Ensure that `server.ts` imports from the Feature's public index (barrel file) only, implementing a 'plugin-like' architecture.
> 4.  **Shared Kernel**: Keep `shared/executor` as a 'Shared Kernel' module used by all features, but avoid dependencies *between* peer features (e.g., Schema shouldn't depend on Stats).
> 
> Output the new directory structure."

### 📝 Detailed Plan

1.  **Restructure Directory**:
    *   Create `packages/core/src/features/`.
    *   Create `packages/core/src/features/schema/`.
    *   Create `packages/core/src/features/diagnostics/` (Stats, Vacuum, etc.).
    *   Create `packages/core/src/features/query/`.
2.  **Move & Rename**:
    *   `src/tools/pg-schema.ts` -> `src/features/schema/tool.ts`.
    *   `src/actions/schema/list.ts` -> `src/features/schema/handlers/list.ts`.
    *   `src/actions/schema/ddl.ts` -> `src/features/schema/handlers/ddl.ts`.
3.  **Strict Boundaries**:
    *   Each feature must export a `register(server)` function or a `tools` array.
    *   The main `server.ts` simply iterates over features to load them.
4.  **Benefits**:
    *   **Delete Code**: You can delete the generic `src/tools/` and `src/actions/` folders entirely.
    *   **Cognitive Load**: When working on "Schema", you only see files in `features/schema/`. You don't jump 3 folders up to find the Zod definition.

---

**Comparison to Other Options:**
*   **vs Option 1 (Purity)**: Less verbose than pure clean architecture (Service/Repo layers are optional inside the slice), but still structured.
*   **vs Option 2 (Collapse)**: More disciplined. It collapses *distance* (co-location) rather than collapsing *layers* (spaghetti code).

