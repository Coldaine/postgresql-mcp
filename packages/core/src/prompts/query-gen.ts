import { Prompt } from "fastmcp";

export const analyzeQueryPrompt: Prompt<any> = {
    name: "analyze_query",
    description: "Analyze a SQL query for performance and correctness",
    arguments: [
        { name: "sql", description: "The SQL query to analyze", required: true }
    ],
    async load(args) {
        return {
            messages: [
                {
                    role: "user",
                    content: {
                        type: "text",
                        text: `Please analyze the following SQL query for performance issues, correctness, and adherence to best practices:\n\n\`\`\`sql\n${args.sql}\n\`\`\`\n\nIf possible, use the 'pg_query' tool with action='explain' to get the execution plan.`
                    }
                }
            ]
        };
    }
};
