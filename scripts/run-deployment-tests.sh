#!/bin/bash
# scripts/run-deployment-tests.sh
#
# Run tests against real remote PostgreSQL instances (deployment tests).
# These tests verify the MCP server works in production-like environments.
#
# Usage:
#   ./scripts/run-deployment-tests.sh                    # Run against default (raspberryoracle)
#   ./scripts/run-deployment-tests.sh --host 10.0.0.1   # Run against custom host

set -e

# Default configuration (Raspberry Pi via Tailscale)
DEPLOY_TEST_HOST="${DEPLOY_TEST_HOST:-100.65.198.61}"
DEPLOY_TEST_PORT="${DEPLOY_TEST_PORT:-5432}"
DEPLOY_TEST_USER="${DEPLOY_TEST_USER:-mcp_test}"
DEPLOY_TEST_PASSWORD="${DEPLOY_TEST_PASSWORD:-mcp_test_password}"
DEPLOY_TEST_DATABASE="${DEPLOY_TEST_DATABASE:-mcp_test}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            DEPLOY_TEST_HOST="$2"
            shift 2
            ;;
        --port)
            DEPLOY_TEST_PORT="$2"
            shift 2
            ;;
        --user)
            DEPLOY_TEST_USER="$2"
            shift 2
            ;;
        --password)
            DEPLOY_TEST_PASSWORD="$2"
            shift 2
            ;;
        --database)
            DEPLOY_TEST_DATABASE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "============================================"
echo "Deployment Tests"
echo "============================================"
echo "Host:     $DEPLOY_TEST_HOST"
echo "Port:     $DEPLOY_TEST_PORT"
echo "User:     $DEPLOY_TEST_USER"
echo "Database: $DEPLOY_TEST_DATABASE"
echo "============================================"

# Check connectivity first
echo "Checking connectivity..."
if ! nc -z -w5 "$DEPLOY_TEST_HOST" "$DEPLOY_TEST_PORT" 2>/dev/null; then
    echo "ERROR: Cannot connect to $DEPLOY_TEST_HOST:$DEPLOY_TEST_PORT"
    echo "Make sure the host is reachable (Tailscale connected?)"
    exit 1
fi
echo "Connection OK"
echo ""

# Export environment variables for tests
export RUN_DEPLOYMENT_TESTS=true
export DEPLOY_TEST_HOST
export DEPLOY_TEST_PORT
export DEPLOY_TEST_USER
export DEPLOY_TEST_PASSWORD
export DEPLOY_TEST_DATABASE

# Run only deployment tests
echo "Running deployment tests..."
npx vitest run packages/core/test/deployment/

echo ""
echo "============================================"
echo "Deployment tests completed!"
echo "============================================"
