# Claude-Cloud Integration Guide

**Created by:** @connector-ninja (Vint Cerf)  
**Mission:** idea:29 (Claude-Cloud-Infrastructure Innovation)  
**Date:** 2025-11-18

---

## 🎯 Overview

This guide provides step-by-step instructions for integrating Claude AI with Chained's infrastructure using the Model Context Protocol (MCP) and structured communication patterns.

**Key Integration Points:**
- ✅ MCP server for world knowledge access
- ✅ JSON schemas for reliable communication
- ✅ Structured outputs for production use
- ✅ Cloud deployment patterns

---

## 📦 Components Created

### 1. MCP Server Package

**Location:** `mcp-servers/chained-world-model/`

**Purpose:** Provide Claude (and other MCP clients) with structured access to Chained's world knowledge base.

**Features:**
- Query world knowledge
- Get mission/idea details
- Search technology patterns
- Access agent insights

### 2. JSON Schemas

**Location:** `schemas/`

**Purpose:** Enable type-safe, validated communication between agents and external systems.

**Schemas:**
- `mission-report.json` - Standardized mission reporting

### 3. Integration Documentation

**Location:** `learnings/claude-innovation-idea29/INTEGRATION_IMPLEMENTATION.md`

**Purpose:** Complete implementation guide with code examples and deployment patterns.

---

## 🚀 Quick Start

### Step 1: Install MCP Server

```bash
cd mcp-servers/chained-world-model
npm install
npm run build
```

### Step 2: Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chained-world-model": {
      "command": "node",
      "args": ["/absolute/path/to/Chained/mcp-servers/chained-world-model/dist/server.js"],
      "env": {
        "CHAINED_ROOT": "/absolute/path/to/Chained"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Claude will now have access to Chained's world knowledge through MCP!

### Step 4: Test Integration

In Claude, try:
```
"Query the Chained world knowledge for Claude innovation patterns"
```

Claude should use the MCP tool to access the world model and return relevant information.

---

## 🔧 Using JSON Schemas

### Validate Mission Reports

```javascript
const Ajv = require('ajv');
const ajv = new Ajv();

// Load schema
const schema = require('./schemas/mission-report.json');
const validate = ajv.compile(schema);

// Validate report
const report = require('./learnings/claude-innovation-idea29/mission-report-idea29.json');
const valid = validate(report);

if (!valid) {
  console.error('Validation errors:', validate.errors);
} else {
  console.log('✅ Report is valid!');
}
```

### Generate Type-Safe Reports

```typescript
// TypeScript types from schema
interface MissionReport {
  mission_id: string;
  agent: string;
  status: 'in_progress' | 'complete' | 'blocked' | 'failed';
  completion_percentage: number;
  deliverables: {
    research_report: {
      completed: boolean;
      word_count: number;
      key_insights: string[];
      document_path?: string;
    };
    // ... more fields
  };
  timestamp: string;
}

// Type-safe report generation
const report: MissionReport = {
  mission_id: 'idea:42',
  agent: '@connector-ninja',
  status: 'complete',
  completion_percentage: 100,
  // ... rest of report
};
```

---

## ☁️ Cloud Deployment

### Deploy to Gram (Managed MCP Hosting)

**Option 1: Using Gram CLI**

```bash
# Install Gram CLI
npm install -g @gram/cli

# Login
gram login

# Deploy MCP server
cd mcp-servers/chained-world-model
gram deploy
```

**Option 2: Manual Deployment**

See [Gram Documentation](https://gram.io/docs) for manual deployment instructions.

### Deploy to AWS Lambda

```bash
# Package for Lambda
cd mcp-servers/chained-world-model
npm run build
zip -r function.zip dist/ node_modules/

# Deploy with AWS CLI
aws lambda create-function \
  --function-name chained-world-model-mcp \
  --runtime nodejs20.x \
  --handler dist/server.handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --environment Variables="{CHAINED_ROOT=/tmp/chained}"
```

### Deploy to Google Cloud Run

```dockerfile
# Dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist/ ./dist/
CMD ["node", "dist/server.js"]
```

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT/chained-mcp
gcloud run deploy chained-mcp \
  --image gcr.io/PROJECT/chained-mcp \
  --platform managed \
  --allow-unauthenticated
```

---

## 🔌 MCP Server API

### Available Tools

#### 1. query_world_knowledge

**Description:** Search the world knowledge base for patterns, trends, and ideas.

**Parameters:**
- `query` (string, required) - Search query
- `limit` (number, optional) - Max results (default: 10)

**Example:**
```json
{
  "query": "Claude integration patterns",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "idea_id": "idea:29",
      "title": "Claude-Cloud-Infrastructure Innovation",
      "relevance": 7,
      "patterns": ["mcp-protocol", "structured-outputs"]
    }
  ]
}
```

#### 2. get_idea_details

**Description:** Get complete information about a specific mission/idea.

**Parameters:**
- `idea_id` (string, required) - Mission ID (e.g., "idea:29")

**Example:**
```json
{
  "idea_id": "idea:29"
}
```

**Response:**
```json
{
  "mission_id": "idea:29",
  "status": "complete",
  "agents": ["@investigate-champion", "@connector-ninja"],
  "deliverables": { /* ... */ },
  "artifacts": [ /* ... */ ]
}
```

#### 3. search_patterns

**Description:** Find technology patterns and trends in the world model.

**Parameters:**
- `pattern` (string, required) - Pattern to search for
- `category` (string, optional) - Category filter

**Example:**
```json
{
  "pattern": "mcp-protocol",
  "category": "integration"
}
```

#### 4. get_agent_insights

**Description:** Access agent performance data and insights.

**Parameters:**
- `agent_name` (string, optional) - Specific agent
- `metric` (string, optional) - Specific metric

**Example:**
```json
{
  "agent_name": "@connector-ninja",
  "metric": "missions_completed"
}
```

---

## 📊 Structured Outputs with Claude API

### Using JSON Schema with Claude

```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

# Define schema
mission_summary_schema = {
    "type": "object",
    "required": ["mission_id", "status", "key_insights"],
    "properties": {
        "mission_id": {"type": "string"},
        "status": {"type": "string", "enum": ["complete", "in_progress"]},
        "key_insights": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 5
        }
    }
}

# Request with schema validation
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Summarize mission idea:29"
    }],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "mission_summary",
            "schema": mission_summary_schema
        }
    }
)

# Response is guaranteed to match schema
summary = json.loads(response.content[0].text)
print(summary["mission_id"])  # Type-safe!
```

### TypeScript Example

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

interface MissionSummary {
  mission_id: string;
  status: 'complete' | 'in_progress';
  key_insights: string[];
}

const response = await client.messages.create({
  model: 'claude-3-5-sonnet-20241022',
  max_tokens: 1024,
  messages: [{
    role: 'user',
    content: 'Summarize mission idea:29'
  }],
  response_format: {
    type: 'json_schema',
    json_schema: {
      name: 'mission_summary',
      schema: {
        type: 'object',
        required: ['mission_id', 'status', 'key_insights'],
        properties: {
          mission_id: { type: 'string' },
          status: { type: 'string', enum: ['complete', 'in_progress'] },
          key_insights: {
            type: 'array',
            items: { type: 'string' },
            minItems: 3,
            maxItems: 5
          }
        }
      }
    }
  }
});

const summary: MissionSummary = JSON.parse(response.content[0].text);
```

---

## 🔒 Security Considerations

### Defensive AI Layer

Based on findings from mission idea:29, implement security monitoring:

```python
class DefensiveAILayer:
    """Monitor agent behavior for anomalies"""
    
    def __init__(self):
        self.baseline_behavior = self.load_baseline()
        self.anomaly_threshold = 0.8
    
    def monitor_agent_action(self, agent_id, action):
        """Check if action deviates from normal behavior"""
        risk_score = self.calculate_risk(action)
        
        if risk_score > self.anomaly_threshold:
            self.auto_sandbox(agent_id)
            self.alert_security_team(agent_id, action, risk_score)
            return False  # Block action
        
        return True  # Allow action
    
    def calculate_risk(self, action):
        """Calculate risk score for action"""
        # Implement risk calculation logic
        pass
```

### API Key Management

```bash
# Use environment variables
export ANTHROPIC_API_KEY="your-api-key"
export CHAINED_ROOT="/path/to/chained"

# Or use .env file (never commit!)
cat > .env << EOF
ANTHROPIC_API_KEY=your-api-key
CHAINED_ROOT=/path/to/chained
EOF
```

### Input Validation

```python
from jsonschema import validate, ValidationError

def validate_mission_report(report_data):
    """Validate mission report against schema"""
    try:
        with open('schemas/mission-report.json') as f:
            schema = json.load(f)
        
        validate(instance=report_data, schema=schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
```

---

## 📈 Monitoring and Observability

### MCP Server Metrics

```javascript
// Add instrumentation to MCP server
const prometheus = require('prom-client');

const requestCounter = new prometheus.Counter({
  name: 'mcp_requests_total',
  help: 'Total number of MCP requests',
  labelNames: ['tool', 'status']
});

const requestDuration = new prometheus.Histogram({
  name: 'mcp_request_duration_seconds',
  help: 'Duration of MCP requests',
  labelNames: ['tool']
});

// Instrument tool handlers
async function handleToolCall(tool, params) {
  const timer = requestDuration.startTimer({ tool });
  
  try {
    const result = await executeTool(tool, params);
    requestCounter.inc({ tool, status: 'success' });
    return result;
  } catch (error) {
    requestCounter.inc({ tool, status: 'error' });
    throw error;
  } finally {
    timer();
  }
}
```

### Logging Best Practices

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'chained-world-model-mcp' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

logger.info('MCP tool called', {
  tool: 'query_world_knowledge',
  params: { query: 'claude patterns' },
  user_id: 'claude-desktop',
  duration_ms: 145
});
```

---

## 🧪 Testing

### Unit Tests for MCP Tools

```javascript
const { describe, it, expect } = require('@jest/globals');
const { queryWorldKnowledge } = require('./tools');

describe('MCP Tools', () => {
  it('should query world knowledge successfully', async () => {
    const result = await queryWorldKnowledge({
      query: 'claude patterns',
      limit: 5
    });
    
    expect(result).toHaveProperty('results');
    expect(result.results).toBeInstanceOf(Array);
    expect(result.results.length).toBeLessThanOrEqual(5);
  });
  
  it('should validate idea_id format', async () => {
    await expect(
      getIdeaDetails({ idea_id: 'invalid' })
    ).rejects.toThrow('Invalid idea_id format');
  });
});
```

### Integration Tests

```javascript
describe('Claude API Integration', () => {
  it('should return structured output', async () => {
    const response = await claudeClient.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      messages: [{ role: 'user', content: 'Test query' }],
      response_format: {
        type: 'json_schema',
        json_schema: {
          name: 'test_response',
          schema: testSchema
        }
      }
    });
    
    const parsed = JSON.parse(response.content[0].text);
    expect(parsed).toMatchSchema(testSchema);
  });
});
```

---

## 🚧 Troubleshooting

### Common Issues

#### MCP Server Won't Start

**Symptom:** Server fails to start with error
**Solution:**
```bash
# Check Node.js version (requires 20+)
node --version

# Rebuild dependencies
cd mcp-servers/chained-world-model
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Claude Can't Find MCP Server

**Symptom:** Tools not appearing in Claude
**Solution:**
1. Check config file path: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Verify absolute paths (no `~` or relative paths)
3. Restart Claude Desktop completely
4. Check server logs for errors

#### JSON Schema Validation Fails

**Symptom:** Schema validation errors
**Solution:**
```bash
# Validate JSON syntax
jq . your-report.json

# Check against schema
npm install -g ajv-cli
ajv validate -s schemas/mission-report.json -d your-report.json
```

#### Environment Variables Not Set

**Symptom:** `CHAINED_ROOT` not found
**Solution:**
```json
{
  "mcpServers": {
    "chained-world-model": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "CHAINED_ROOT": "/absolute/path/to/Chained",
        "NODE_ENV": "production"
      }
    }
  }
}
```

---

## 🎓 Best Practices

### 1. Always Validate Inputs

```javascript
function validateParams(params, schema) {
  if (!validate(params, schema)) {
    throw new Error(`Invalid parameters: ${validate.errors}`);
  }
}
```

### 2. Use Structured Outputs

```python
# Always define schemas for AI responses
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    response_format={
        "type": "json_schema",
        "json_schema": { "name": "response", "schema": schema }
    }
)
```

### 3. Monitor Everything

```javascript
// Log all MCP tool calls
logger.info('Tool called', { tool, params, result, duration });

// Track errors
logger.error('Tool failed', { tool, params, error: error.message });
```

### 4. Handle Errors Gracefully

```javascript
try {
  const result = await mcpTool.execute(params);
  return result;
} catch (error) {
  logger.error('Tool execution failed', { error });
  return {
    error: 'Internal error',
    message: 'Please try again later'
  };
}
```

### 5. Document Everything

```javascript
/**
 * Query the world knowledge base
 * 
 * @param {Object} params - Query parameters
 * @param {string} params.query - Search query
 * @param {number} [params.limit=10] - Max results
 * @returns {Promise<Object>} Search results
 * @throws {ValidationError} If params are invalid
 */
async function queryWorldKnowledge(params) {
  // Implementation
}
```

---

## 📚 Additional Resources

### Documentation
- [MCP Specification](https://modelcontextprotocol.io)
- [Claude API Docs](https://docs.anthropic.com)
- [Chained Repository](https://github.com/enufacas/Chained)

### Related Missions
- **idea:29** - Claude-Cloud-Infrastructure Innovation
- Research by @investigate-champion
- Integration by @connector-ninja

### Code Examples
- See `learnings/claude-innovation-idea29/INTEGRATION_IMPLEMENTATION.md`
- Check `mcp-servers/chained-world-model/README.md`
- Review `schemas/mission-report.json`

---

## 🤝 Contributing

### Adding New MCP Tools

1. Define tool schema
2. Implement tool handler
3. Add tests
4. Update documentation
5. Submit PR

### Creating New Schemas

1. Follow JSON Schema draft-07 spec
2. Include examples
3. Add validation tests
4. Document usage
5. Update integration guide

### Reporting Issues

Open an issue with:
- Component affected (MCP server, schema, etc.)
- Expected behavior
- Actual behavior
- Steps to reproduce
- Environment details

---

## 📝 License

MIT License - See repository LICENSE file

---

## ✨ Credits

**Created by @connector-ninja** (Vint Cerf)  
*Protocol-minded and inclusive - enabling interoperability*

**Based on research by @investigate-champion**  
*Analytical and visionary - discovering strategic intelligence*

**Mission idea:29:** Claude-Cloud-Infrastructure Innovation  
**Status:** ✅ Complete

---

*"Protocols enable interoperability. Integration enables innovation."*  
— @connector-ninja, 2025-11-18
