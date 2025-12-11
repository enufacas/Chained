# RL Resource Optimizer API

> **Created by @APIs-architect** - REST API for GitHub Actions Resource Optimization

## Overview

The RL Optimizer API provides a REST interface for real-time GitHub Actions resource optimization using reinforcement learning. It enables workflow automation, webhook integration, and programmatic access to optimization recommendations.

## Quick Start

### Start the API Server

```bash
# Install dependencies
pip install flask flask-cors

# Start server on default port 5000
python3 tools/rl_optimizer_api.py

# Start with custom configuration
python3 tools/rl_optimizer_api.py --host 0.0.0.0 --port 8080 --debug
```

### Basic Usage

```bash
# Health check
curl http://localhost:5000/health

# Get recommendation for a workflow
curl http://localhost:5000/api/v1/recommend?workflow=code-quality

# Train the model
curl -X POST http://localhost:5000/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{"episodes": 100}'

# Get metrics
curl http://localhost:5000/api/v1/metrics
```

## API Endpoints

### Health Check

**GET** `/health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "rl-optimizer-api",
  "version": "1.0.0",
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Get Recommendation

**GET** `/api/v1/recommend`

Get optimization recommendation for a specific workflow.

**Parameters:**
- `workflow` (required): Workflow name
- `include_alternatives` (optional): Include alternative actions (default: true)

**Example:**
```bash
curl "http://localhost:5000/api/v1/recommend?workflow=code-quality&include_alternatives=true"
```

**Response:**
```json
{
  "workflow": "code-quality",
  "current_state": {
    "concurrency_limit": 2,
    "timeout_minutes": 60,
    "caching_enabled": false,
    "parallel_jobs": 1,
    "avg_duration_seconds": 342.5,
    "success_rate": 0.85,
    "resource_utilization": 0.45
  },
  "recommended_action": "enable_caching",
  "expected_improvement": 12.5,
  "confidence": 0.75,
  "reasoning": [
    "⏱️ Long average duration (5.7min) - optimization potential",
    "💡 Enabling caching can significantly reduce build times",
    "📈 High confidence action (Q-value: 0.125)"
  ],
  "alternative_actions": [
    {
      "action": "parallelize_jobs",
      "expected_improvement": 8.2
    },
    {
      "action": "increase_concurrency",
      "expected_improvement": 5.1
    }
  ],
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Train Model

**POST** `/api/v1/train`

Train the RL model with simulation episodes.

**Body Parameters:**
- `episodes` (optional): Number of training episodes (default: 100)
- `save` (optional): Save model after training (default: true)

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{"episodes": 200, "save": true}'
```

**Response:**
```json
{
  "success": true,
  "episodes_trained": 200,
  "duration_seconds": 2.34,
  "total_episodes": 270,
  "epsilon": 0.654,
  "q_table_size": 85,
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Get Metrics

**GET** `/api/v1/metrics`

Get optimizer performance metrics and statistics.

**Example:**
```bash
curl http://localhost:5000/api/v1/metrics
```

**Response:**
```json
{
  "model_stats": {
    "total_episodes": 270,
    "epsilon": 0.654,
    "q_table_size": 85,
    "experience_buffer_size": 150,
    "learning_rate": 0.1,
    "discount_factor": 0.95
  },
  "metrics": {
    "total_optimizations": 15,
    "successful_optimizations": 12,
    "avg_improvement": 8.7,
    "workflow_improvements": {
      "code-quality": 12.5,
      "tests": 7.3
    }
  },
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Get Status

**GET** `/api/v1/status`

Get current model status and configuration.

**Example:**
```bash
curl http://localhost:5000/api/v1/status
```

**Response:**
```json
{
  "status": "ready",
  "model_loaded": true,
  "configuration": {
    "learning_rate": 0.1,
    "discount_factor": 0.95,
    "epsilon": 0.654,
    "min_epsilon": 0.05,
    "epsilon_decay": 0.995,
    "replay_buffer_size": 1000,
    "batch_size": 32
  },
  "reward_weights": {
    "duration": 0.4,
    "success": 0.35,
    "utilization": 0.25
  },
  "storage": {
    "directory": "/path/to/repo/.github/rl-optimizer",
    "q_table_file": "/path/to/repo/.github/rl-optimizer/q_table.json",
    "experience_file": "/path/to/repo/.github/rl-optimizer/experiences.json",
    "metrics_file": "/path/to/repo/.github/rl-optimizer/metrics.json"
  },
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### Apply Recommendation

**POST** `/api/v1/apply`

Apply an optimization recommendation (webhook support).

**Body Parameters:**
- `workflow` (required): Workflow name
- `action` (optional): Specific action to apply (will recommend if not provided)
- `dry_run` (optional): Simulate only, don't apply (default: true)

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/apply \
  -H "Content-Type: application/json" \
  -d '{"workflow": "code-quality", "action": "enable_caching", "dry_run": false}'
```

**Response:**
```json
{
  "workflow": "code-quality",
  "action": "enable_caching",
  "applied": true,
  "dry_run": false,
  "message": "Applied enable_caching to code-quality",
  "warning": "Automatic application not yet implemented. Manual workflow update required.",
  "timestamp": "2025-12-11T10:00:00Z"
}
```

### List Workflows

**GET** `/api/v1/workflows`

List all known workflows with their current states.

**Example:**
```bash
curl http://localhost:5000/api/v1/workflows
```

**Response:**
```json
{
  "workflows": [
    {
      "name": "code-quality",
      "state": {
        "workflow_name": "code-quality",
        "concurrency_limit": 2,
        "timeout_minutes": 60,
        "caching_enabled": true,
        "parallel_jobs": 2,
        "avg_duration_seconds": 285.3,
        "success_rate": 0.92,
        "resource_utilization": 0.65
      }
    }
  ],
  "count": 1,
  "timestamp": "2025-12-11T10:00:00Z"
}
```

## Integration Examples

### Python Client

```python
import requests

class RLOptimizerClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_recommendation(self, workflow: str):
        """Get optimization recommendation."""
        response = requests.get(
            f"{self.base_url}/api/v1/recommend",
            params={"workflow": workflow}
        )
        return response.json()
    
    def train_model(self, episodes: int = 100):
        """Train the RL model."""
        response = requests.post(
            f"{self.base_url}/api/v1/train",
            json={"episodes": episodes}
        )
        return response.json()
    
    def get_metrics(self):
        """Get optimizer metrics."""
        response = requests.get(f"{self.base_url}/api/v1/metrics")
        return response.json()

# Usage
client = RLOptimizerClient()
rec = client.get_recommendation("code-quality")
print(f"Recommended: {rec['recommended_action']}")
print(f"Expected improvement: {rec['expected_improvement']:.1f}%")
```

### Webhook Integration

```yaml
# GitHub Actions workflow example
name: Auto-Optimize Workflow
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]

jobs:
  optimize:
    runs-on: ubuntu-latest
    steps:
      - name: Get optimization recommendation
        id: optimize
        run: |
          RECOMMENDATION=$(curl -s "http://optimizer-api:5000/api/v1/recommend?workflow=${{ github.event.workflow.name }}")
          echo "recommendation=$RECOMMENDATION" >> $GITHUB_OUTPUT
      
      - name: Apply if confident
        run: |
          CONFIDENCE=$(echo '${{ steps.optimize.outputs.recommendation }}' | jq -r '.confidence')
          if (( $(echo "$CONFIDENCE > 0.8" | bc -l) )); then
            curl -X POST http://optimizer-api:5000/api/v1/apply \
              -H "Content-Type: application/json" \
              -d '{"workflow": "${{ github.event.workflow.name }}", "dry_run": false}'
          fi
```

### JavaScript/TypeScript

```typescript
class RLOptimizerClient {
  constructor(private baseUrl: string = 'http://localhost:5000') {}

  async getRecommendation(workflow: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/recommend?workflow=${workflow}`
    );
    return response.json();
  }

  async trainModel(episodes: number = 100): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ episodes })
    });
    return response.json();
  }

  async getMetrics(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/metrics`);
    return response.json();
  }
}

// Usage
const client = new RLOptimizerClient();
const rec = await client.getRecommendation('code-quality');
console.log(`Recommended: ${rec.recommended_action}`);
console.log(`Expected improvement: ${rec.expected_improvement.toFixed(1)}%`);
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY tools/rl_optimizer_api.py .
COPY tools/rl_resource_optimizer.py .

RUN pip install flask flask-cors

EXPOSE 5000

CMD ["python", "rl_optimizer_api.py", "--host", "0.0.0.0", "--port", "5000"]
```

### Cloud Run

```yaml
# Deploy to GCP Cloud Run
gcloud run deploy rl-optimizer-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="PORT=8080"
```

## Testing

Run the test suite:

```bash
# Unit tests
python3 tests/test_rl_optimizer_api.py

# With pytest
pytest tests/test_rl_optimizer_api.py -v

# With coverage
pytest tests/test_rl_optimizer_api.py --cov=tools/rl_optimizer_api --cov-report=html
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid parameters or request body
- **500 Internal Server Error**: Server-side error

Error responses include details:

```json
{
  "error": "Missing required parameter: workflow"
}
```

## Security Considerations

1. **Authentication**: Add API key or OAuth for production
2. **Rate Limiting**: Implement rate limiting for public endpoints
3. **CORS**: Configure CORS for specific origins in production
4. **HTTPS**: Use HTTPS in production environments
5. **Input Validation**: All inputs are validated before processing

## Performance

- **Recommendation latency**: &lt;100ms typical
- **Training latency**: ~0.01s per episode
- **Memory usage**: ~50MB base + model size
- **Concurrent requests**: Supports multiple concurrent clients

## Related Documentation

- [RL Resource Optimizer](./RL_RESOURCE_OPTIMIZER_README.md) - Core RL implementation
- [GitHub Actions Data Collector](./GITHUB_ACTIONS_DATA_COLLECTOR_README.md) - Data collection
- [AI Workflow Predictor](./AI_WORKFLOW_PREDICTOR_README.md) - Execution prediction

---

*Created by **@APIs-architect** - Part of the Chained autonomous AI ecosystem 🏭*
