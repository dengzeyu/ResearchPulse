# Docker Deployment Guide

This guide explains how to run ResearchPulse using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ or OrbStack
- Docker Compose v2.0+

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t research-pulse:latest .
```

This creates a Docker image with all dependencies installed, including:
- Python 3.11
- All required packages from pyproject.toml
- arxiv support (optional dependency)
- NLTK data files

### 2. Configure Environment Variables

Create a `.env` file in the project root with your API keys:

```bash
# LLM Provider (required - choose one)
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_BASE_URL=http://your-custom-endpoint  # Optional

# Or use OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=http://your-custom-endpoint  # Optional

# Or use Google Gemini
GOOGLE_API_KEY=your_key_here

# Or use Ollama (local)
OLLAMA_HOST=http://localhost:11434

# Optional: Social media APIs
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=researchpulse/1.0

GITHUB_TOKEN=your_token

GOOGLE_SEARCH_API_KEY=your_key
GOOGLE_SEARCH_ENGINE_ID=your_id

# Optional: Runtime configuration
RUN_ONCE=true  # Set to false for continuous mode
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
TIMEZONE=UTC
```

### 3. Run with Docker Compose (Recommended)

```bash
# Start services (research-pulse + nginx)
docker-compose up -d

# View logs
docker-compose logs -f research-pulse

# Stop services
docker-compose down
```

The static site will be served at http://localhost:8080

### 4. Run with Docker (Manual)

```bash
# Run once
docker run --rm \
  --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  research-pulse:latest

# Run in continuous mode (disable RUN_ONCE)
docker run -d \
  --name research-pulse \
  --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  research-pulse:latest

# View logs
docker logs -f research-pulse

# Stop container
docker stop research-pulse && docker rm research-pulse
```

## Docker Compose Services

### research-pulse
- Runs the Python pipeline
- Fetches papers, analyzes them, generates insights
- Outputs static HTML to `./output` directory
- Mounts:
  - `./output` → `/app/output` (generated site)
  - `./config` → `/app/config` (tracking configuration)
  - `./logs` → `/app/logs` (application logs)

### nginx
- Serves the static site on port 8080
- Read-only mount of `./output` directory
- Automatically restarts
- Depends on research-pulse service

## Configuration

### Tracking Keywords

Edit `config/tracking.yaml` to customize what papers to track:

```yaml
keywords:
  - area: "Machine Learning"
    terms:
      - "transformers"
      - "LLMs"
      - "attention mechanisms"
    sources: ["arxiv", "semantic_scholar"]
    max_results: 10
```

### LLM Provider

Edit `config/llm.yaml` to configure your LLM provider:

```yaml
provider: claude  # claude | openai | gemini | ollama

claude:
  model: claude-sonnet-4-5-20250929
  base_url: http://nexusnus:3000/api  # Optional custom endpoint

research_ideas:
  count: 5
  prompt: "Focus on practical applications"

hot_topics:
  count: 3
  prompt: "Identify breakthrough trends"
```

## Troubleshooting

### Docker daemon not running

If you see "Cannot connect to the Docker daemon":

```bash
# For OrbStack
open -a OrbStack

# For Docker Desktop
open -a Docker
```

### Build fails with README.md not found

The `.dockerignore` file has been updated to include README.md. Rebuild:

```bash
docker build --no-cache -t research-pulse:latest .
```

### Import errors in container

Ensure the Dockerfile sets the correct PYTHONPATH and WORKDIR:

```dockerfile
ENV PYTHONPATH=/app/src
WORKDIR /app/src
```

### Port 8080 already in use

Change the nginx port in `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "9090:80"  # Changed from 8080 to 9090
```

## Advanced Usage

### Custom Dockerfile

To modify the Docker image:

```dockerfile
FROM research-pulse:latest

# Add custom dependencies
RUN pip install your-package

# Override CMD
CMD ["python", "your_script.py"]
```

### Multi-stage Build

For smaller images, use multi-stage builds:

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ".[arxiv]"

FROM python:3.11-slim
WORKDIR /app/src
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app
CMD ["python", "main.py"]
```

### Scheduled Runs

Use cron or systemd timers to run periodically:

```bash
# Crontab entry (runs daily at 9 AM)
0 9 * * * docker run --rm --env-file /path/to/.env -v /path/to/output:/app/output research-pulse:latest
```

## Deployment

### AWS ECS

1. Push image to ECR
2. Create ECS task definition
3. Create scheduled ECS task (CloudWatch Events)
4. Serve static files from S3 + CloudFront

### Google Cloud Run

1. Push image to GCR
2. Deploy as Cloud Run job
3. Schedule with Cloud Scheduler
4. Serve from Cloud Storage

### Kubernetes

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: research-pulse
spec:
  schedule: "0 9 * * *"  # Daily at 9 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: research-pulse
            image: research-pulse:latest
            envFrom:
            - secretRef:
                name: research-pulse-secrets
            volumeMounts:
            - name: output
              mountPath: /app/output
          volumes:
          - name: output
            persistentVolumeClaim:
              claimName: research-pulse-output
          restartPolicy: OnFailure
```

## Monitoring

### Health Checks

Add to `docker-compose.yml`:

```yaml
research-pulse:
  healthcheck:
    test: ["CMD", "python", "-c", "import main"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Logging

View logs:

```bash
# Docker Compose
docker-compose logs -f --tail=100 research-pulse

# Docker
docker logs -f --tail=100 research-pulse

# Save to file
docker logs research-pulse > research-pulse.log 2>&1
```

## Security

- Never commit `.env` files
- Use Docker secrets for sensitive data
- Run containers as non-root user
- Keep base images updated
- Scan images for vulnerabilities:

```bash
docker scan research-pulse:latest
```

## Performance

### Build Cache

Speed up builds with BuildKit:

```bash
DOCKER_BUILDKIT=1 docker build -t research-pulse:latest .
```

### Resource Limits

Limit container resources in `docker-compose.yml`:

```yaml
research-pulse:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

## Cleanup

```bash
# Remove containers
docker-compose down

# Remove images
docker rmi research-pulse:latest

# Remove volumes
docker-compose down -v

# Clean up everything
docker system prune -a --volumes
```
