/**
 * Deployment Test Configuration
 *
 * These tests run against real remote PostgreSQL instances.
 * Configure via environment variables or use defaults for the Raspberry Pi test environment.
 */

export interface DeploymentConfig {
    host: string;
    port: number;
    user: string;
    password: string;
    database: string;
    name: string;
}

export const deploymentConfig: DeploymentConfig = {
    host: process.env['DEPLOY_TEST_HOST'] || '100.65.198.61', // Tailscale IP for raspberryoracle
    port: parseInt(process.env['DEPLOY_TEST_PORT'] || '5432'),
    user: process.env['DEPLOY_TEST_USER'] || 'mcp_test',
    password: process.env['DEPLOY_TEST_PASSWORD'] || 'mcp_test_password',
    database: process.env['DEPLOY_TEST_DATABASE'] || 'mcp_test',
    name: process.env['DEPLOY_TEST_NAME'] || 'raspberryoracle',
};

export function isDeploymentTestEnabled(): boolean {
    // Run deployment tests if explicitly enabled or if we can reach the host
    return process.env['RUN_DEPLOYMENT_TESTS'] === 'true';
}
