import { FastMCP } from "fastmcp";

export function registerAnalyzePrompt(server: FastMCP) {
    server.addPrompt({
        name: "analyze_query",
        description: "Ask the assistant to analyze a SQL query for performance and correctness",
        arguments: [
            {
                name: "query",
                description: "The SQL query to analyze",
                required: true,
            },
        ],
        load: async (args) => {
            const query = String(args['query']);
            return {
                messages: [
                    {
                        role: "user",
                        content: {
                            type: "text",
                            text: `Please analyze the following SQL query for potential performance issues, security risks, and correctness:\n\n\`\`\`sql\n${query}\n\`\`\`\n\nProvide an explanation of the query plan (if obvious) and suggest optimizations.`,
                        },
                    },
                ],
            };
        },
    });
}
