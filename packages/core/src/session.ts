import { QueryExecutor } from "@pg-mcp/shared/executor/interface.js";
import { randomUUID } from "crypto";

interface Session {
    id: string;
    executor: QueryExecutor;
    lastActive: number;
    timeoutTimer: NodeJS.Timeout;
}

export class SessionManager {
    private sessions = new Map<string, Session>();
    // 5 minutes default TTL - strictly enforced to prevent resource exhaustion
    private readonly TTL_MS = 5 * 60 * 1000; 

    constructor(private readonly globalExecutor: QueryExecutor) {}

    /**
     * Creates a new session with a dedicated database connection.
     * Returns the unique session ID.
     */
    async createSession(): Promise<string> {
        const id = randomUUID();
        const sessionExecutor = await this.globalExecutor.createSession();
        
        const session: Session = {
            id,
            executor: sessionExecutor,
            lastActive: Date.now(),
            timeoutTimer: this.startTimer(id),
        };

        this.sessions.set(id, session);
        return id;
    }

    /**
     * Retrieves the executor for a given session ID.
     * Resets the TTL timer on access.
     */
    getSessionExecutor(id: string): QueryExecutor | undefined {
        const session = this.sessions.get(id);
        if (!session) return undefined;

        // Reset TTL
        session.lastActive = Date.now();
        clearTimeout(session.timeoutTimer);
        session.timeoutTimer = this.startTimer(id);

        return session.executor;
    }

    /**
     * Closes a session, releasing the connection and ensuring cleanup.
     * If a transaction was open, the connection release will trigger an automatic rollback.
     */
    async closeSession(id: string): Promise<void> {
        const session = this.sessions.get(id);
        if (session) {
            clearTimeout(session.timeoutTimer);
            try {
                await session.executor.disconnect();
            } catch (error) {
                console.error(`Error closing session ${id}:`, error);
            }
            this.sessions.delete(id);
        }
    }

    private startTimer(id: string): NodeJS.Timeout {
        return setTimeout(() => {
            console.error(`[SessionManager] Session ${id} timed out. Auto-closing to prevent leaks.`);
            this.closeSession(id);
        }, this.TTL_MS);
    }
}