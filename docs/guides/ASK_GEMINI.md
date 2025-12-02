# Ask Gemini - Escalation Standard for Copilot

This guide documents the "ask gemini about X" escalation pattern, enabling GitHub Copilot users to consult Google's Gemini 3 Pro Preview for complex problems, second opinions, and expert insights during coding sessions.

## 🎯 Overview

**What is "Ask Gemini"?**
A human-controlled escalation mechanism that allows anyone using GitHub Copilot in the Chained repository to consult Gemini 3 Pro Preview for expert insights on complex problems.

**Why Use It?**
- Get second opinions on architectural decisions
- Analyze security implications of code changes
- Evaluate complex trade-offs (performance, maintainability, scalability)
- Explore unfamiliar technical domains
- Validate approaches against best practices
- Strategic guidance on technology choices

**How It Works:**
1. Human says "ask gemini about X" during a Copilot session
2. Copilot invokes the `@gemini-consultant` agent
3. Agent calls Gemini 3 Pro Preview API via `tools/ask_gemini.py`
4. Gemini provides expert analysis and recommendations
5. Agent synthesizes Gemini's insights with Chained context
6. Human receives comprehensive, actionable guidance

## 🚀 Quick Start

### Prerequisites

**Authentication (Choose One):**

#### Option A: Google AI Studio (Recommended - Simplest)
```bash
# 1. Get API key from https://aistudio.google.com/app/apikey
# 2. Set environment variable
export GEMINI_API_KEY="your-api-key-here"
```

#### Option B: Vertex AI (For GCP Users)
```bash
# 1. Get Vertex AI API key from Google Cloud Console
# 2. Set environment variables
export GOOGLE_API_KEY="your-vertex-api-key"
export USE_VERTEX_AI=true
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - Google AI Studio API
- `google-cloud-aiplatform` - Vertex AI API (optional)

### Test the Setup

```bash
# Test as a standalone tool
python3 tools/ask_gemini.py "What are the trade-offs between REST and GraphQL?"

# You should see:
# 🤔 Consulting Gemini 3 Pro Preview...
# ✅ Gemini's Response:
# [Detailed analysis from Gemini]
```

## 📖 Usage Patterns

### Pattern 1: During Copilot Session (Primary Use Case)

**Human Action:**
```
"ask gemini about whether we should use microservices or monolithic architecture for this project"
```

**What Happens:**
1. Copilot recognizes the "ask gemini" trigger
2. Invokes `@gemini-consultant` agent
3. Agent uses `ask_gemini.py` to consult Gemini
4. Agent presents formatted response with analysis

**Response Format:**
```markdown
## 🤔 Gemini Consultation

**Question:** Should we use microservices or monolithic architecture?

**Context Provided:**
- Current project structure (monolithic)
- Team size (5 developers)
- Performance requirements (moderate)
- Deployment frequency (weekly)

**Gemini's Response:**
[Detailed analysis of microservices vs monolithic trade-offs...]

**My Analysis:**
Given Chained's current team size and deployment patterns, starting with
a well-structured monolith is recommended. Microservices add operational
complexity that may not be justified at this stage.

**Recommendation:**
1. Maintain monolithic architecture with clear module boundaries
2. Design for future decomposition (loose coupling, clear interfaces)
3. Revisit microservices when team grows beyond 10-15 developers
4. Consider service-oriented architecture within the monolith first
```

### Pattern 2: Explicit Agent Mention

**Human Action:**
```
"@gemini-consultant what are the security implications of using regex for input validation?"
```

**What Happens:**
Same as Pattern 1, but explicitly mentions the agent.

### Pattern 3: Command-Line Tool (For Scripts/Automation)

```bash
# Direct question
python3 tools/ask_gemini.py "How should I structure error handling in async Python code?"

# With additional context
python3 tools/ask_gemini.py \
  "Should we refactor this 500-line function?" \
  --context "High cyclomatic complexity, low test coverage, frequent bugs"

# Use a different model
python3 tools/ask_gemini.py \
  "Explain this design pattern" \
  --model gemini-1.5-flash-latest
```

### Pattern 4: Python API (For Custom Tools)

```python
from tools.ask_gemini import ask_gemini

# Basic usage
response = ask_gemini("What are the benefits of type hints in Python?")
print(response)

# With context
response = ask_gemini(
    question="Should we add caching to this API?",
    context="Current response time: 200ms, Cache hit rate: 80%",
    model="gemini-3-pro-preview",
    timeout_seconds=30,
)
print(response)
```

## 🎓 When to Use "Ask Gemini"

### ✅ Good Use Cases

1. **Architectural Decisions**
   - "ask gemini about REST vs GraphQL for agent APIs"
   - "ask gemini about event-driven vs request-response architecture"
   - Technology stack choices

2. **Security Analysis**
   - "ask gemini about security implications of this authentication approach"
   - "ask gemini about OWASP risks in this code pattern"
   - Vulnerability assessment

3. **Performance Trade-offs**
   - "ask gemini about caching strategies for this use case"
   - "ask gemini about database indexing for this query pattern"
   - Optimization approaches

4. **Complex Refactoring**
   - "ask gemini about how to refactor this 1000-line function"
   - "ask gemini about design patterns for this problem"
   - Code structure improvements

5. **Unknown Domains**
   - "ask gemini about WebAssembly for this use case"
   - "ask gemini about blockchain considerations for this feature"
   - Technologies outside current expertise

6. **Second Opinions**
   - "ask gemini to validate this API design"
   - "ask gemini about alternative approaches to this solution"
   - Expert validation

### ❌ Poor Use Cases

1. **Simple Questions**
   - Use documentation or existing agents instead
   - Example: "How do I format a Python string?" → No need for Gemini

2. **Repository-Specific Knowledge**
   - Use Chained's agents who know the codebase
   - Example: "Where is the agent registry?" → @investigate-champion knows this

3. **Rapid Iterations**
   - Gemini consultation adds 2-5 second latency
   - Better for one-time decisions than iterative debugging

4. **Already Clear Solutions**
   - Don't escalate unnecessarily
   - Trust existing agents for routine tasks

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes* | Google AI Studio API key |
| `GOOGLE_API_KEY` | Yes* | Vertex AI API key (alternative to GEMINI_API_KEY) |
| `USE_VERTEX_AI` | No | Set to `true` to use Vertex AI instead of Google AI Studio |
| `GOOGLE_CLOUD_PROJECT` | If Vertex | GCP project ID for Vertex AI |
| `GOOGLE_CLOUD_LOCATION` | No | GCP region (default: us-central1) |

*Required: Either `GEMINI_API_KEY` OR `GOOGLE_API_KEY` must be set

### Model Configuration

**Default:** `gemini-3-pro-preview` (latest Gemini 3 Pro preview)

**Available Models:**
- `gemini-3-pro-preview` - Latest Gemini 3 Pro preview (default)
- `gemini-1.5-pro-latest` - Stable production model
- `gemini-1.5-flash-latest` - Fast and efficient
- `gemini-1.0-pro` - Legacy model

**Change Model:**
```python
# In code
response = ask_gemini("Question", model="gemini-1.5-flash-latest")

# Command line
python3 tools/ask_gemini.py "Question" --model gemini-1.5-flash-latest
```

### Rate Limits (Free Tier)

| Model | Requests/Minute | Requests/Day |
|-------|----------------|--------------|
| gemini-3-pro-preview | 15 | 1,500 |
| gemini-1.5-pro-latest | 2 | 50 |
| gemini-1.5-flash-latest | 15 | 1,500 |

**Best Practice:** Use `gemini-3-pro-preview` or `gemini-1.5-flash-latest` for higher rate limits.

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Copilot Session                   │
│                                                              │
│  Human: "ask gemini about X"                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              @gemini-consultant Agent                        │
│                                                              │
│  - Clarifies question                                        │
│  - Gathers repository context                               │
│  - Formulates prompt for Gemini                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              tools/ask_gemini.py                             │
│                                                              │
│  - Handles authentication (Google AI / Vertex AI)           │
│  - Calls Gemini 3 Pro Preview API                           │
│  - Returns response                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Gemini 3 Pro Preview API                        │
│                                                              │
│  - generativelanguage.googleapis.com (Google AI Studio)     │
│  - OR aiplatform.googleapis.com (Vertex AI)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Response Flow                                   │
│                                                              │
│  Gemini Response → ask_gemini.py → @gemini-consultant       │
│  → Synthesizes with Chained context → Recommendations       │
│  → Presented to human                                        │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
Chained/
├── .github/agents/
│   └── gemini-consultant.md         # Agent definition
├── tools/
│   └── ask_gemini.py                # Python tool for Gemini API
├── docs/guides/
│   └── ASK_GEMINI.md                # This documentation
├── requirements.txt                 # Updated with Gemini dependencies
└── tests/
    └── test_ask_gemini.py           # Tests for ask_gemini tool
```

## 🧪 Testing

### Unit Tests

```bash
# Run tests
python3 -m pytest tests/test_ask_gemini.py -v

# Test with coverage
python3 -m pytest tests/test_ask_gemini.py --cov=tools.ask_gemini
```

### Manual Testing

```bash
# Test authentication configuration
python3 -c "from tools.ask_gemini import get_auth_mode; print(get_auth_mode())"

# Test basic query
python3 tools/ask_gemini.py "What is the Fibonacci sequence?"

# Test with context
python3 tools/ask_gemini.py \
  "How should I optimize this?" \
  --context "Python function with O(n^2) complexity"

# Test error handling (no API key)
unset GEMINI_API_KEY
python3 tools/ask_gemini.py "Test" # Should show auth error
```

## 🔒 Security Considerations

### API Key Protection

**Do:**
- Store API keys in environment variables
- Never commit API keys to repository
- Use GitHub Secrets for CI/CD workflows
- Rotate API keys regularly

**Don't:**
- Hardcode API keys in code
- Share API keys in issues or PRs
- Log API keys in console output
- Use API keys in public repositories without secrets

### Input Validation

- All user input is passed to Gemini API
- No code execution from Gemini responses
- Responses are treated as text, not executable code
- Agent synthesizes responses with proper context

### Rate Limiting

- Respect API rate limits (15 RPM on free tier)
- Implement exponential backoff on failures
- Cache common consultation patterns when applicable
- Monitor usage to stay within quotas

## 🐛 Troubleshooting

### Error: "No Gemini authentication configured"

**Cause:** Missing API key environment variable

**Solution:**
```bash
# Set Google AI Studio API key
export GEMINI_API_KEY="your-api-key"

# OR set Vertex AI credentials
export GOOGLE_API_KEY="your-vertex-key"
export USE_VERTEX_AI=true
export GOOGLE_CLOUD_PROJECT="your-project"
```

### Error: "google-generativeai package not installed"

**Cause:** Missing Python dependencies

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "API keys are not supported by this API"

**Cause:** Using Vertex AI key with Google AI Studio endpoint

**Solution:**
```bash
export USE_VERTEX_AI=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Error: "Rate limit exceeded"

**Cause:** Too many requests to Gemini API

**Solution:**
- Wait 1 minute for rate limit reset
- Use `gemini-1.5-flash-latest` for higher limits
- Implement request queuing for batch operations
- Upgrade to paid tier if needed

### Agent Not Responding

**Cause:** Agent pattern not recognized

**Solution:**
- Use exact phrase: "ask gemini about X"
- Or mention agent explicitly: "@gemini-consultant"
- Check that agent definition exists in `.github/agents/`

## 📊 Performance

### Response Times

| Operation | Average | Maximum |
|-----------|---------|---------|
| API call (Google AI Studio) | 2-3s | 5s |
| API call (Vertex AI) | 1-2s | 3s |
| Agent synthesis | <1s | 2s |
| **Total** | **3-4s** | **7s** |

### Resource Usage

- **Memory:** ~50MB for Python process
- **Network:** ~10KB request, ~50KB response
- **CPU:** Minimal (mostly I/O wait)

### Optimization Tips

1. **Use appropriate models:**
   - `gemini-1.5-flash-latest` for speed (1-2s)
   - `gemini-3-pro-preview` for quality (2-3s)

2. **Cache common consultations:**
   - Store frequent Q&A patterns
   - Avoid redundant API calls

3. **Batch related questions:**
   - Combine multiple questions in one prompt
   - Reduces total API calls

## 🎯 Best Practices

### Formulating Questions

**Good:**
```
"ask gemini about the security implications of storing JWT tokens in localStorage
vs httpOnly cookies, considering XSS and CSRF attack vectors"
```

**Better:**
```
"ask gemini about JWT storage: localStorage vs httpOnly cookies. Context: 
SPA application, high security requirements, concerned about XSS/CSRF.
Need specific recommendations for our use case."
```

### Providing Context

**Essential Context:**
- Current architecture/approach
- Constraints (performance, security, team skills)
- What you've already tried
- Specific concerns or questions

**Example:**
```python
ask_gemini(
    question="Should we add caching to this API endpoint?",
    context="""
    Current situation:
    - Response time: 200ms average, 500ms p99
    - Database queries: 3 per request
    - Traffic: 1000 req/min
    - Cache infrastructure: Redis available
    - Data staleness tolerance: 5 minutes acceptable
    
    Question: Is caching beneficial here?
    """
)
```

### Interpreting Responses

1. **Read critically:** Gemini provides general advice; adapt to your context
2. **Validate recommendations:** Cross-check with documentation and best practices
3. **Consider trade-offs:** Weigh Gemini's suggestions against your constraints
4. **Synthesize insights:** Combine Gemini's advice with repository knowledge
5. **Document decisions:** Record rationale for architectural choices

## 📚 Examples

### Example 1: Architecture Decision

**Human:**
```
"ask gemini about whether we should use WebSockets or Server-Sent Events 
for real-time agent status updates in the GitHub Pages dashboard"
```

**Gemini Consultation:**
```markdown
## 🤔 Gemini Consultation

**Question:** WebSockets vs Server-Sent Events for real-time updates?

**Context Provided:**
- GitHub Pages static site (no server)
- Agent status updates (one-way: server → client)
- Update frequency: every 5-10 seconds
- Browser compatibility required

**Gemini's Response:**
For your use case, Server-Sent Events (SSE) is the better choice:

1. **One-way communication:** SSE is designed for server→client updates
2. **Automatic reconnection:** Built-in retry logic
3. **Simpler implementation:** Native EventSource API
4. **Lower overhead:** HTTP-based, no complex protocol
5. **GitHub Pages compatible:** Works with static hosting + API

WebSockets would be overkill since you don't need bidirectional communication.

**My Analysis:**
Gemini correctly identified that SSE fits our needs better. However, 
we need to consider that GitHub Pages is fully static. We'd need an
external API endpoint (Cloud Run) to send events.

**Recommendation:**
1. Deploy a lightweight Cloud Run service as SSE event source
2. Use EventSource API in the frontend
3. Fall back to polling for older browsers
4. Implement exponential backoff for reconnection

Example implementation:
```javascript
const eventSource = new EventSource('https://api.chained.dev/agent-status');
eventSource.onmessage = (event) => {
  const status = JSON.parse(event.data);
  updateAgentDashboard(status);
};
```
```

### Example 2: Security Review

**Human:**
```
"ask gemini about potential security vulnerabilities in our agent 
assignment workflow that processes untrusted issue titles"
```

**Gemini Consultation:**
```markdown
## 🤔 Gemini Consultation

**Question:** Security review of agent assignment with untrusted input

**Context Provided:**
```python
# tools/match-issue-to-agent.py
def match_agent(issue_title: str):
    for agent, patterns in AGENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, issue_title):  # ⚠️ Untrusted input
                return agent
```

**Gemini's Response:**
Several security concerns identified:

1. **ReDoS (Regular Expression Denial of Service):**
   - Complex regex patterns with untrusted input
   - Attacker crafts title causing exponential backtracking
   - Example: `pattern = r'(a+)+$'` with input `'a' * 100 + '!'`
   - Can freeze the process for seconds/minutes

2. **Input Validation Missing:**
   - No length limits on issue titles
   - No sanitization of special regex characters
   - No timeout on regex matching

3. **Resource Exhaustion:**
   - Processing malicious titles in tight loop
   - No rate limiting per user/IP

**Recommended Mitigations:**

1. **Timeout Regex Operations:**
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Regex timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(1)  # 1 second timeout
try:
    match = re.search(pattern, issue_title)
finally:
    signal.alarm(0)
```

2. **Sanitize Input:**
```python
def sanitize_title(title: str) -> str:
    # Limit length
    title = title[:200]
    # Escape special characters
    return re.escape(title)
```

3. **Use Safe Patterns:**
```python
# Avoid catastrophic backtracking
# Bad: r'(a+)+$'
# Good: r'a+$'
```

**My Analysis:**
Gemini correctly identified ReDoS vulnerability in our pattern matching.
This is a real risk given we process external issues. We should:

**Recommendation:**
1. ✅ **Immediate:** Add timeout to regex operations (signal-based)
2. ✅ **Short-term:** Sanitize/validate issue titles before pattern matching
3. ✅ **Long-term:** Migrate to keyword-based matching instead of regex
4. ✅ **Monitor:** Add metrics for pattern matching duration

**Implementation Priority:** HIGH - Security vulnerability affects all
agent assignments from external issues.
```

### Example 3: Performance Optimization

**Human:**
```
"ask gemini about optimizing our workflow that processes 1000+ agent metrics
every 5 minutes. Currently takes 30 seconds, need to reduce to under 10s."
```

**Gemini Consultation:**
```markdown
## 🤔 Gemini Consultation

**Question:** How to optimize agent metrics processing from 30s to <10s?

**Context Provided:**
- Volume: 1000+ agent performance metrics
- Frequency: Every 5 minutes
- Current duration: 30 seconds
- Target: Under 10 seconds
- Language: Python
- Current approach: Sequential file reads + JSON parsing

**Gemini's Response:**
Multiple optimization strategies available:

1. **Parallel Processing:**
   - Use `multiprocessing` or `concurrent.futures`
   - Process agents in parallel (8-16 workers)
   - Expected speedup: 4-8x on multi-core systems

2. **Caching:**
   - Cache unchanged agent metrics
   - Only recompute modified agents
   - Expected speedup: 3-5x for typical updates

3. **Batch File I/O:**
   - Read all files at once (parallel reads)
   - Parse JSON in memory pool
   - Expected speedup: 2-3x

4. **Incremental Updates:**
   - Track what changed since last run
   - Only process deltas
   - Expected speedup: 5-10x for small changes

**Implementation Example:**

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

def process_agent(agent_file):
    """Process single agent metrics."""
    with open(agent_file) as f:
        return json.load(f)

def process_all_agents_parallel(agent_files):
    """Process all agents in parallel."""
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_agent, f): f 
                   for f in agent_files}
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    return results
```

**Expected Performance:**
- Sequential: 30 seconds
- Parallel (8 workers): 4-6 seconds ✅
- With caching: 2-3 seconds ✅✅

**My Analysis:**
Gemini's parallel processing recommendation is solid. Given our workflow
runs in GitHub Actions runners (2-4 cores), we should see 2-3x speedup.
Caching unchanged metrics is also valuable since most agents don't change
every run.

**Recommendation:**
1. ✅ **Phase 1:** Implement parallel processing with `ProcessPoolExecutor`
2. ✅ **Phase 2:** Add caching layer with file modification time checks
3. ✅ **Phase 3:** Implement incremental updates for further optimization

**Expected Timeline:**
- Phase 1: 2 hours implementation → 10-12s runtime ✅ Meets target
- Phase 2: 4 hours implementation → 4-6s runtime
- Phase 3: 8 hours implementation → 2-3s runtime

**Decision:** Proceed with Phase 1 immediately to meet <10s target.
Evaluate Phases 2-3 based on actual results.
```

## 🔗 Related Resources

- **Gemini API Documentation:** https://ai.google.dev/docs
- **Google AI Studio:** https://aistudio.google.com/
- **Vertex AI:** https://cloud.google.com/vertex-ai/docs
- **Chained Agent System:** `/docs/AGENT_QUICKSTART.md`
- **Gemini CLI Integration:** `/docs/GEMINI_CLI_INTEGRATION.md`

## 📝 Change Log

### v1.0.0 (2024-12-02)
- Initial implementation of "ask gemini" escalation standard
- Created `@gemini-consultant` agent
- Created `tools/ask_gemini.py` tool
- Added Google AI Studio and Vertex AI authentication support
- Comprehensive documentation and examples

---

*"Think of it as an escalation that the human steering the copilot session can control."*

This escalation mechanism empowers humans to leverage Gemini's capabilities when they need expert consultation, while maintaining control over when and how that escalation occurs.
