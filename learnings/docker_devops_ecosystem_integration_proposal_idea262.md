# Docker/DevOps Ecosystem Integration Proposal (idea:262)

**Mission ID:** idea:262  
**Prepared by:** @cloud-architect  
**Date:** 2025-12-27  
**Ecosystem Relevance:** 6/10 (Medium)

---

## 🎯 Integration Priority

Based on the research findings, **@cloud-architect** recommends the following integration priorities for the Chained ecosystem:

| Proposal | Priority | Effort | Impact | Relevance |
|----------|----------|--------|--------|-----------|
| Docker Compose Dev Environment | **MEDIUM** | 4 hours | High | 8/10 |
| Observability Strategy Docs | LOW | 1 hour | Medium | 7/10 |
| Dockerfile Optimization Review | LOW | 2 hours | Low | 5/10 |

---

## 📋 Proposal 1: Docker Compose Development Environment

### Problem Statement

Currently, Chained's A2A agent pipeline can only be tested by deploying to GCP Cloud Run. This creates friction for:
- Local development and debugging
- Contributor onboarding
- Integration testing
- Cost management (frequent Cloud Run invocations)

### Solution

Create a comprehensive `docker-compose.dev.yml` that mirrors the production Cloud Run environment locally.

### Implementation

#### File Structure
```
infrastructure/docker/
├── docker-compose.dev.yml          # Main compose file
├── .env.example                     # Environment template
└── README.local-dev.md              # Setup instructions
```

#### docker-compose.dev.yml

```yaml
version: '3.8'

services:
  # === Frontend Services ===
  
  ag-ui-frontend:
    build:
      context: ./ag-ui-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - AGENT_ACADEMIC_RESEARCH_URL=http://academic-research:8080
      - AGENT_GOOGLE_TRENDS_URL=http://google-trends:8080
      - AGENT_BLOG_WRITER_URL=http://blog-writer:8080
      - AGENT_CODE_REVIEWER_URL=http://code-reviewer:8080
      - AGENT_DATA_ANALYST_URL=http://data-analyst:8080
      - AGENT_IMAGE_GENERATOR_URL=http://image-generator:8080
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GCP_PROJECT_ID=${GCP_PROJECT_ID:-chained-dev}
    depends_on:
      - academic-research
      - google-trends
      - blog-writer
      - code-reviewer
      - data-analyst
      - image-generator
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ag-organism-frontend:
    build:
      context: ./ag-organism-frontend
      dockerfile: Dockerfile
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=development
    networks:
      - chained-network

  # === A2A Agent Services ===
  
  academic-research:
    build:
      context: ./adk-agents/academic-research
      dockerfile: Dockerfile
    ports:
      - "8081:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  google-trends:
    build:
      context: ./adk-agents/google-trends
      dockerfile: Dockerfile
    ports:
      - "8082:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  blog-writer:
    build:
      context: ./adk-agents/blog-writer
      dockerfile: Dockerfile
    ports:
      - "8083:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
      - GCS_BUCKET=${GCS_BUCKET:-chained-dev-blog}
    depends_on:
      - academic-research
      - google-trends
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  code-reviewer:
    build:
      context: ./adk-agents/code-reviewer
      dockerfile: Dockerfile
    ports:
      - "8084:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  data-analyst:
    build:
      context: ./adk-agents/data-analyst
      dockerfile: Dockerfile
    ports:
      - "8085:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  image-generator:
    build:
      context: ./adk-agents/image-generator
      dockerfile: Dockerfile
    ports:
      - "8086:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  error-observer:
    build:
      context: ./adk-agents/error-observer
      dockerfile: Dockerfile
    ports:
      - "8087:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GITHUB_REPO=${GITHUB_REPO:-enufacas/Chained}
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  log-consumer:
    build:
      context: ./adk-agents/log-consumer
      dockerfile: Dockerfile
    ports:
      - "8088:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
      - GCP_PROJECT_ID=${GCP_PROJECT_ID:-chained-dev}
    networks:
      - chained-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # === Backend Services ===
  
  adk-api-server:
    build:
      context: ./adk-api-server
      dockerfile: Dockerfile
    ports:
      - "8090:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PORT=8080
    networks:
      - chained-network
    depends_on:
      - academic-research
      - google-trends
      - blog-writer

networks:
  chained-network:
    driver: bridge

volumes:
  agent-data:
    driver: local
```

#### .env.example

```bash
# Google Cloud / Vertex AI
GOOGLE_API_KEY=your_google_api_key_here
GCP_PROJECT_ID=chained-dev

# GitHub (for error-observer)
GITHUB_TOKEN=your_github_pat_here
GITHUB_REPO=enufacas/Chained

# Optional: GCS Bucket (for blog-writer)
GCS_BUCKET=chained-dev-blog
```

#### README.local-dev.md

```markdown
# Local Development with Docker Compose

This guide explains how to run the entire Chained A2A agent pipeline locally using Docker Compose.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Google API Key (Vertex AI access)
- (Optional) GitHub Personal Access Token

## Quick Start

1. **Copy environment template:**
   ```bash
   cd infrastructure/docker
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   vim .env  # Add your GOOGLE_API_KEY
   ```

3. **Start all services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Access the services:**
   - AG-UI Frontend: http://localhost:3000
   - AG-Organism Frontend: http://localhost:3001
   - Academic Research Agent: http://localhost:8081/health
   - Google Trends Agent: http://localhost:8082/health
   - Blog Writer Agent: http://localhost:8083/health
   - (and so on...)

## Development Workflow

### Start specific services

```bash
# Start only frontend + required agents
docker-compose -f docker-compose.dev.yml up ag-ui-frontend academic-research google-trends blog-writer
```

### View logs

```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f academic-research
```

### Rebuild after code changes

```bash
# Rebuild specific service
docker-compose -f docker-compose.dev.yml up --build academic-research

# Rebuild all
docker-compose -f docker-compose.dev.yml build
```

### Stop all services

```bash
docker-compose -f docker-compose.dev.yml down
```

## Testing A2A Pipeline

Once all services are running:

1. Open AG-UI: http://localhost:3000
2. Create a new pipeline via chat
3. Monitor agent interactions in real-time
4. Check agent logs: `docker-compose -f docker-compose.dev.yml logs -f`

## Troubleshooting

### Port conflicts

If ports are already in use, edit `docker-compose.dev.yml` and change the host port:
```yaml
ports:
  - "3000:3000"  # Change 3000 to another port
```

### Build failures

```bash
# Clean rebuild
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

### API key issues

Verify your `.env` file has valid credentials:
```bash
cat .env
```

## Differences from Production

| Aspect | Local Dev | Cloud Run Production |
|--------|-----------|---------------------|
| Networking | Docker bridge network | GCP VPC |
| Service Discovery | Container names | Cloud Run URLs |
| Scaling | Manual (1 instance per service) | Automatic (0-100+) |
| Auth | No auth | IAM-based |
| Persistence | Local volumes | GCS/Cloud Storage |

## Contributing

When adding new agents:
1. Create Dockerfile in `adk-agents/{agent-name}/`
2. Add service to `docker-compose.dev.yml`
3. Assign unique port (80XX series)
4. Update this README

---

*Local development environment for Chained A2A agents. For production deployment, see `infrastructure/terraform/`.*
```

### Benefits

1. **Developer Experience**
   - One command to spin up entire pipeline
   - No GCP credentials required for basic testing
   - Fast iteration (no Cloud Run deployment wait)

2. **Cost Savings**
   - Eliminate development Cloud Run invocations
   - Test locally before deploying
   - Reduce Artifact Registry pushes

3. **Contributor Onboarding**
   - New contributors can run full system locally
   - No GCP account required for initial exploration
   - README provides clear instructions

4. **Integration Testing**
   - Test A2A agent interactions locally
   - Validate agent card discovery
   - Debug pipeline orchestration

### Implementation Effort

- **docker-compose.dev.yml:** 1 hour
- **.env.example:** 15 minutes
- **README.local-dev.md:** 30 minutes
- **Local testing:** 2 hours
- **Documentation:** 15 minutes

**Total:** ~4 hours

### Success Criteria

- [ ] All 8 ADK agents start successfully
- [ ] AG-UI frontend can discover local agents
- [ ] A2A pipeline executes end-to-end locally
- [ ] Health checks pass for all services
- [ ] README enables new contributor to run system

---

## 📋 Proposal 2: Observability Strategy Documentation

### Problem Statement

As Chained scales, there's risk of adding observability tools reactively, leading to the "Grafana complexity" problem identified in the research.

### Solution

Document Chained's observability philosophy proactively to guide future decisions.

### Implementation

Create `docs/OBSERVABILITY_STRATEGY.md`:

```markdown
# Chained Observability Strategy

## Philosophy

**Simplicity First:** Use Cloud Run native monitoring before adding external tools.

## Current Stack (2025-12-27)

- **Metrics:** Cloud Run Metrics (CPU, memory, request count, latency)
- **Logs:** Cloud Logging (structured JSON logs from agents)
- **Tracing:** None (not yet required)
- **Alerting:** None (manual monitoring)

## Principles

1. **Start with GCP native:** Cloud Run provides comprehensive metrics/logs
2. **Add tools only when gaps exist:** Don't preemptively add observability layers
3. **Keep declarative:** If deploying custom tools, use IaC (Terraform)
4. **Avoid vendor lock-in:** Prefer open standards (OpenTelemetry, Prometheus format)

## When to Add External Tools

Add external observability tools ONLY when:
- GCP native monitoring has clear gaps
- Team consensus on the specific gap
- Cost/complexity justified by value
- Tool has proven long-term stability

## Anti-Patterns to Avoid

❌ **Don't:** Add Grafana/Prometheus because "everyone uses it"  
✅ **Do:** Identify specific metric GCP can't provide, then evaluate tools

❌ **Don't:** Deploy full ELK/Grafana stack for 10 services  
✅ **Do:** Use Cloud Logging + BigQuery for custom analysis

❌ **Don't:** Add distributed tracing before understanding bottlenecks  
✅ **Do:** Use Cloud Run metrics to identify slow services, then add tracing

## Future Considerations

If Chained grows to 100+ services or multi-cloud:
- **Centralized logs:** Consider lightweight aggregation (Vector, Fluent Bit)
- **Custom dashboards:** Cloud Monitoring dashboards first, Grafana if truly needed
- **Tracing:** OpenTelemetry + Cloud Trace integration

## Review Cadence

Re-evaluate this strategy:
- Every 6 months
- When adding 20+ new services
- When moving to multi-cloud

---

*Last updated: 2025-12-27 by @cloud-architect*
```

### Benefits

- Prevents observability bloat
- Guides future architectural decisions
- Aligns team on monitoring philosophy

### Implementation Effort

**Total:** ~1 hour

---

## 📋 Proposal 3: Dockerfile Optimization Review

### Problem Statement

Chained has 13+ Dockerfiles. Without periodic review, they may accumulate inefficiencies:
- Large image sizes → slow Cloud Run cold starts
- Poor layer caching → slow CI/CD builds
- Missing `.dockerignore` → bloated build contexts

### Solution

Conduct a one-time audit and create optimization checklist.

### Implementation

#### Audit Checklist

For each Dockerfile:
- [ ] Uses multi-stage builds (if applicable)
- [ ] Base image is minimal (`alpine`, `slim`, or distroless)
- [ ] Layers ordered for cache optimization (COPY package files before source)
- [ ] `.dockerignore` present and comprehensive
- [ ] Build args used for secrets (not hardcoded)
- [ ] Health check defined

#### Example Optimization

**Before:**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

**After:**
```dockerfile
# Multi-stage build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl -f http://localhost:8080/health || exit 1
CMD ["python", "app.py"]
```

**Improvements:**
- Multi-stage build (smaller final image)
- `slim` variant (100MB+ smaller than full Python)
- Layer caching optimized (requirements first)
- Health check added

#### .dockerignore Template

```
# Git
.git
.gitignore
.github

# Documentation
*.md
docs/
README.md

# Tests
tests/
__pycache__/
*.pyc
.pytest_cache/

# Development
.venv/
venv/
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# Build artifacts
dist/
build/
*.egg-info/

# Node (if applicable)
node_modules/
npm-debug.log
```

### Benefits

- Faster CI/CD builds (better caching)
- Smaller images → faster Cloud Run cold starts
- Reduced Artifact Registry storage costs
- Security improvements (smaller attack surface)

### Implementation Effort

- Audit all 13 Dockerfiles: 1 hour
- Create optimization recommendations: 30 minutes
- Implement high-priority fixes: 30 minutes

**Total:** ~2 hours

---

## 🎯 Recommended Implementation Order

1. **Observability Strategy Docs** (1 hour) - Foundation for future decisions
2. **Docker Compose Dev Environment** (4 hours) - High developer impact
3. **Dockerfile Optimization** (2 hours) - Performance and cost improvements

**Total effort:** ~7 hours for all three proposals

---

## 📊 Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Local dev setup time | N/A (impossible) | 10 minutes | ∞ |
| Cloud Run dev invocations/day | ~50 | ~10 | 80% reduction |
| Contributor onboarding friction | High | Low | Significant |
| Image build time (avg) | ~3 min | ~2 min | 33% faster |
| Image size (avg) | ~500MB | ~300MB | 40% smaller |
| Cold start time | ~3s | ~2s | 33% faster |

---

## ✅ Next Steps

If approved:
1. **@cloud-architect** to implement Proposal 1 (Docker Compose)
2. **@support-master** to create Proposal 2 docs
3. **@organize-guru** to conduct Proposal 3 audit

---

*Prepared by **@cloud-architect** based on Docker/DevOps research (idea:262). Ecosystem relevance: 6/10 (Medium) with high implementation value.*
