# ColdQuery Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (local or remote)
- For production: Tailscale account and auth key

---

## Local Development Deployment

### 1. Start with Docker Compose

```bash
# Start PostgreSQL and ColdQuery
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost:3000/health

# Stop services
docker-compose down
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
DB_HOST=postgres
DB_PORT=5432
DB_USER=mcp
DB_PASSWORD=mcp
DB_DATABASE=mcp_test
```

---

## Production Deployment (Raspberry Pi)

### 1. Server Setup

```bash
# On Raspberry Pi
sudo apt update
sudo apt install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Create deployment directory
sudo mkdir -p /opt/coldquery
sudo chown $USER:$USER /opt/coldquery
```

### 2. Tailscale Setup

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate
sudo tailscale up

# Get auth key for containers
# https://login.tailscale.com/admin/settings/keys
```

### 3. Configure GitHub Secrets

In GitHub repository settings, add secrets:

- `RASPBERry_PI_SSH_KEY` - SSH private key for deployment
- `DB_HOST` - Database hostname
- `DB_PORT` - Database port
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_DATABASE` - Database name
- `TAILSCALE_AUTH_KEY` - Tailscale auth key

### 4. Deploy

Push to main branch triggers automatic deployment:

```bash
git push origin main
```

Or trigger manually:

```bash
gh workflow run deploy.yml
```

### 5. Verify Deployment

```bash
# SSH to Raspberry Pi
ssh raspberrypi

# Check containers
docker ps

# Check logs
docker-compose -f /opt/coldquery/docker-compose.yml logs -f

# Test health endpoint
curl http://localhost:3000/health
```

---

## Manual Deployment

### 1. Build Docker Image

```bash
# Build for ARM64 (Raspberry Pi)
docker buildx build --platform linux/arm64 -t coldquery:arm64 .

# Build for AMD64 (x86_64)
docker buildx build --platform linux/amd64 -t coldquery:amd64 .
```

### 2. Save and Transfer Image

```bash
# Save image
docker save coldquery:arm64 -o coldquery-arm64.tar

# Copy to server
scp coldquery-arm64.tar user@server:/tmp/

# On server: Load image
docker load -i /tmp/coldquery-arm64.tar
```

### 3. Run Container

```bash
docker run -d \
  --name coldquery \
  -p 3000:3000 \
  -e DB_HOST=your-db-host \
  -e DB_PORT=5432 \
  -e DB_USER=mcp \
  -e DB_PASSWORD=mcp \
  -e DB_DATABASE=mcp_prod \
  coldquery:arm64
```

---

## Monitoring

### Health Checks

```bash
# Check container health
docker ps

# Health endpoint
curl http://localhost:3000/health

# Container logs
docker logs coldquery-server -f
```

### Resource Usage

```bash
# Container stats
docker stats coldquery-server

# Disk usage
docker system df
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs coldquery-server

# Check health
docker inspect coldquery-server | grep Health

# Restart container
docker restart coldquery-server
```

### Database Connection Issues

```bash
# Test database connectivity
docker exec coldquery-server sh -c 'wget -q -O- http://localhost:3000/health'

# Check environment variables
docker exec coldquery-server env | grep DB_
```

### Tailscale Issues

```bash
# Check Tailscale status
docker exec coldquery-tailscale tailscale status

# Restart Tailscale
docker restart coldquery-tailscale
```

---

## Backup and Restore

### Backup Database

```bash
# Dump database
docker exec coldquery-postgres pg_dump -U mcp mcp_test > backup.sql
```

### Restore Database

```bash
# Restore from dump
docker exec -i coldquery-postgres psql -U mcp mcp_test < backup.sql
```

---

## Updating

### Update via CI/CD

```bash
# Push changes to main
git push origin main

# Deployment runs automatically
```

### Manual Update

```bash
# On Raspberry Pi
cd /opt/coldquery

# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Rollback Procedures

### Automated Rollback (via GitHub Actions)

To redeploy a previous, stable version of the application:

1.  **Find the commit SHA** of the last known good deployment. You can find this in the commit history on your `main` branch.
2.  **Go to the "Deploy to Raspberry Pi" workflow** in the "Actions" tab of your GitHub repository.
3.  **Run the workflow manually** by clicking "Run workflow".
4.  **In the "Use workflow from" dropdown, select "Branch"** and ensure it's set to `main`.
5.  **Enter the stable commit SHA** you identified in the input field (if the workflow is configured to accept a SHA, otherwise you may need to revert the `main` branch to that SHA).
6.  **Run the workflow.** This will build the Docker image from that specific commit and deploy it.

### Manual Rollback (on the Raspberry Pi)

If a new deployment fails and you need to quickly revert, you can do so directly on the Raspberry Pi:

1.  **SSH into your Raspberry Pi:**
    ```bash
    ssh your_user@your_pi_host
    ```

2.  **Navigate to your deployment directory:**
    ```bash
    cd /opt/coldquery
    ```

3.  **Find the image tag of the previous version.** Docker images pushed from the CI/CD pipeline are tagged with the commit SHA. You can list the images available locally:
    ```bash
    docker images | grep "ghcr.io/coldaine/coldquery"
    ```
    This will show you a list of images, including `latest` and the images tagged with commit SHAs. Identify the tag of the version you want to roll back to.

4.  **Update the `docker-compose.deploy.yml` file:**
    Open the `docker-compose.deploy.yml` file and change the `image` tag for the `coldquery` service to the specific commit SHA tag you want to deploy.

    For example, change:
    ```yaml
    services:
      coldquery:
        image: ghcr.io/coldaine/coldquery:latest
        ...
    ```
    to:
    ```yaml
    services:
      coldquery:
        image: ghcr.io/coldaine/coldquery:a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
        ...
    ```

5.  **Restart the service:**
    ```bash
    docker-compose -f docker-compose.deploy.yml up -d
    ```
    Docker Compose will see that the image tag has changed and will stop the current container and start a new one using the specified older image.

6.  **Verify the rollback:**
    Check the container logs and the health status to ensure the application is running correctly.
    ```bash
    docker logs coldquery-server
    ```
