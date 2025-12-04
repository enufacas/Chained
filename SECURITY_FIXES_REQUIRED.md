# 🔒 Security Fixes Required - Error Observer System

**Priority:** 🔥 CRITICAL  
**Status:** BLOCKING PRODUCTION DEPLOYMENT  
**Reviewer:** @secure-specialist  
**Date:** 2025-12-02

---

## ⚠️ Executive Summary

The error observer implementation has **6 critical security vulnerabilities** that MUST be fixed before production deployment. These vulnerabilities expose the system to:

1. **Denial of Service attacks** ($$$ impact)
2. **Credential theft** via stack trace leaks
3. **Workflow manipulation** via GitHub PAT compromise
4. **Service impersonation** attacks

**Estimated Fix Time:** 2-3 days  
**Estimated Cost if Exploited:** $10,000+ (DoS attack costs)

---

## 🔥 CRITICAL FIXES (Block Production)

### 1. Rate Limiting on UI Error Endpoint

**File:** `infrastructure/docker/ag-ui-frontend/src/app/api/ui-error-report/route.ts`

**Vulnerability:** No rate limiting allows unlimited error submissions

**Fix:** Add IP-based rate limiting

```typescript
// Create: src/lib/rate-limiter.ts
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();

export function checkRateLimit(ip: string, limit: number = 10, windowMs: number = 60000): boolean {
  const now = Date.now();
  const rateLimit = rateLimitMap.get(ip);
  
  if (rateLimit) {
    if (now < rateLimit.resetAt) {
      if (rateLimit.count >= limit) {
        return false; // Rate limit exceeded
      }
      rateLimit.count++;
    } else {
      rateLimitMap.set(ip, { count: 1, resetAt: now + windowMs });
    }
  } else {
    rateLimitMap.set(ip, { count: 1, resetAt: now + windowMs });
  }
  
  // Clean up old entries periodically
  if (Math.random() < 0.01) { // 1% chance
    const entries = Array.from(rateLimitMap.entries());
    for (const [key, value] of entries) {
      if (now > value.resetAt) {
        rateLimitMap.delete(key);
      }
    }
  }
  
  return true;
}

// Update: src/app/api/ui-error-report/route.ts
import { checkRateLimit } from '@/lib/rate-limiter';

export async function POST(request: NextRequest) {
  const ip = request.ip ?? request.headers.get('x-forwarded-for') ?? 'unknown';
  
  // Check rate limit (10 requests per minute)
  if (!checkRateLimit(ip, 10, 60000)) {
    return NextResponse.json(
      { error: 'Rate limit exceeded. Please try again later.' },
      { status: 429, headers: { 'Retry-After': '60' } }
    );
  }
  
  // Rest of the handler...
}
```

**Test:**
```bash
# Should see 429 after 10 requests
for i in {1..15}; do
  curl -X POST http://localhost:3000/api/ui-error-report \
    -H "Content-Type: application/json" \
    -d '{"message":"test"}' \
    && echo " - Request $i: OK" || echo " - Request $i: BLOCKED"
done
```

---

### 2. Move GITHUB_REPO to Environment Variable

**File:** `infrastructure/docker/adk-agents/error-observer/agent.py`

**Vulnerability:** Hardcoded repository name creates privilege escalation risk

**Fix:**

```python
# Update: agent.py (line 46)
# OLD:
# GITHUB_REPO = "enufacas/Chained"

# NEW:
GITHUB_REPO = os.getenv("GITHUB_REPO")
if not GITHUB_REPO:
    raise ValueError("GITHUB_REPO environment variable is required")

# Validate repository format
import re
if not re.match(r'^[\w\-\.]+/[\w\-\.]+$', GITHUB_REPO):
    raise ValueError(f"Invalid repository format: {GITHUB_REPO}. Expected: owner/repo")

print(f"   GitHub repository: {GITHUB_REPO}")
```

```terraform
# Update: infrastructure/terraform/adk-agents.tf (add env var)
# In error_observer service template:

env {
  name  = "GITHUB_REPO"
  value = var.github_repo  # Default: "enufacas/Chained"
}
```

```terraform
# Update: infrastructure/terraform/variables.tf (add variable)
variable "github_repo" {
  description = "GitHub repository for error dispatch (format: owner/repo)"
  type        = string
  default     = "enufacas/Chained"
  
  validation {
    condition     = can(regex("^[\\w\\-\\.]+/[\\w\\-\\.]+$", var.github_repo))
    error_message = "Repository must be in format: owner/repo"
  }
}
```

**Test:**
```bash
# Test with invalid repo format
GITHUB_REPO="invalid-format" python agent.py
# Expected: ValueError: Invalid repository format

# Test with valid format
GITHUB_REPO="owner/repo" python agent.py
# Expected: Starts successfully
```

---

### 3. Sanitize Stack Traces

**File:** `infrastructure/docker/adk-agents/shared/error_event.py`

**Vulnerability:** Stack traces leak credentials and secrets

**Fix:**

```python
# Add to error_event.py (after imports)
import re

def sanitize_stack_trace(stack_trace: Optional[str]) -> Optional[str]:
    """
    Remove sensitive information from stack traces.
    
    Removes:
    - API keys, tokens, passwords (32+ char alphanumerics)
    - Connection strings
    - Private IP addresses
    - File system paths (keeps relative paths)
    - Environment variable values
    """
    if not stack_trace:
        return stack_trace
    
    # Define redaction patterns
    patterns = [
        # API keys and tokens (32+ characters of alphanumeric)
        (r'\b[A-Za-z0-9_\-]{32,}\b', '[REDACTED_TOKEN]'),
        
        # Password/secret in various formats
        (r'password\s*[=:]\s*[^\s\'"]+', 'password=[REDACTED]'),
        (r'passwd\s*[=:]\s*[^\s\'"]+', 'passwd=[REDACTED]'),
        (r'secret\s*[=:]\s*[^\s\'"]+', 'secret=[REDACTED]'),
        (r'api[_-]?key\s*[=:]\s*[^\s\'"]+', 'api_key=[REDACTED]'),
        (r'token\s*[=:]\s*[^\s\'"]+', 'token=[REDACTED]'),
        
        # Connection strings
        (r'(postgresql|mysql|mongodb)://[^@\s]+@', r'\1://[REDACTED]@'),
        (r'mongodb\+srv://[^@\s]+@', 'mongodb+srv://[REDACTED]@'),
        
        # Private IP addresses
        (r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[PRIVATE_IP]'),
        (r'\b172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b', '[PRIVATE_IP]'),
        (r'\b192\.168\.\d{1,3}\.\d{1,3}\b', '[PRIVATE_IP]'),
        
        # AWS credentials
        (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),
        (r'aws_secret_access_key\s*=\s*[^\s]+', 'aws_secret_access_key=[REDACTED]'),
        
        # GCP credentials
        (r'"private_key":\s*"[^"]+', '"private_key": "[REDACTED]'),
        (r'"client_secret":\s*"[^"]+', '"client_secret": "[REDACTED]'),
    ]
    
    sanitized = stack_trace
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized

# Update from_exception method (line 121-170)
@classmethod
def from_exception(
    cls,
    service: str,
    exception: Exception,
    source_agent: Optional[str] = None,
    source_channel: str = "runtime",
    region: str = "us-central1",
    environment: str = "production",
    a2a_ui_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> "ErrorEvent":
    import traceback
    
    error_message = str(exception)
    stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    # ✅ SANITIZE before storing
    sanitized_stack = sanitize_stack_trace(stack_trace)
    sanitized_message = sanitize_stack_trace(error_message)
    
    now = datetime.utcnow().isoformat() + "Z"
    error_hash = cls.compute_error_hash(service, sanitized_message, "exception")
    
    return cls(
        service=service,
        region=region,
        environment=environment,
        error_message=sanitized_message,
        stack_trace=sanitized_stack,
        error_hash=error_hash,
        first_seen=now,
        last_seen=now,
        source_agent=source_agent,
        source_channel=source_channel,
        a2a_ui_url=a2a_ui_url,
        metadata=metadata or {},
    )

# Update from_ui_error method (line 172-217)
@classmethod
def from_ui_error(
    cls,
    message: str,
    stack: Optional[str] = None,
    url: Optional[str] = None,
    user_agent: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> "ErrorEvent":
    now = datetime.utcnow().isoformat() + "Z"
    
    # ✅ SANITIZE inputs
    sanitized_message = sanitize_stack_trace(message) or message
    sanitized_stack = sanitize_stack_trace(stack) if stack else None
    
    error_hash = cls.compute_error_hash("a2a-ui", sanitized_message, "ui-error")
    
    logs = []
    if user_agent:
        # Sanitize user agent (remove version details)
        user_agent_sanitized = re.sub(r'\d+\.\d+\.\d+\.?\d*', '*', user_agent)
        logs.append(f"User-Agent: {user_agent_sanitized}")
    if extra:
        logs.append(f"Extra: {json.dumps(extra)}")
    
    return cls(
        service="a2a-ui",
        region="us-central1",
        environment="production",
        error_message=sanitized_message,
        stack_trace=sanitized_stack,
        error_hash=error_hash,
        first_seen=now,
        last_seen=now,
        source_agent="a2a-ui-backend",
        source_channel="ui",
        a2a_ui_url=url,
        logs=logs,
        metadata=extra or {},
    )
```

**Test:**
```python
# tests/test_sanitization.py
def test_sanitize_stack_trace():
    dangerous_trace = """
    Traceback (most recent call last):
      File "app.py", line 42
        password = "SuperSecret123"
        api_key = "sk-1234567890abcdef"
        db_url = "postgresql://user:pass123@10.0.1.5/db"
    """
    
    from shared.error_event import sanitize_stack_trace
    sanitized = sanitize_stack_trace(dangerous_trace)
    
    assert "SuperSecret123" not in sanitized
    assert "sk-1234567890abcdef" not in sanitized
    assert "pass123" not in sanitized
    assert "[REDACTED]" in sanitized
    print("✅ Sanitization working correctly")
```

---

### 4. Add Pub/Sub Authentication

**File:** `infrastructure/docker/adk-agents/log-consumer/agent.py`

**Vulnerability:** Anyone can POST to `/pubsub/push` endpoint

**Fix Option 1: Use Cloud Run's built-in authentication**

```terraform
# Update: infrastructure/terraform/adk-agents.tf

# Remove public access to log consumer
# DELETE THIS:
# resource "google_cloud_run_v2_service_iam_member" "log_consumer_public" {
#   project  = var.project_id
#   location = var.region
#   name     = google_cloud_run_v2_service.log_consumer.name
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }

# Add Pub/Sub service account access
data "google_project" "project" {
  project_id = var.project_id
}

resource "google_cloud_run_v2_service_iam_member" "log_consumer_pubsub" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.log_consumer.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}
```

**Fix Option 2: Verify JWT token in application**

```python
# Update: log-consumer/agent.py
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

async def verify_pubsub_token(request: Request) -> bool:
    """
    Verify that the request comes from Cloud Pub/Sub.
    
    Cloud Pub/Sub adds an Authorization header with a JWT token.
    Reference: https://cloud.google.com/pubsub/docs/push#authentication
    """
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        print("❌ Missing Authorization header")
        return False
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    try:
        # Get the service URL for audience validation
        service_url = os.getenv("SERVICE_URL") or f"http://localhost:{PORT}"
        
        # Verify the token using Google's public keys
        claim = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=service_url,
        )
        
        # Check that the token is from Pub/Sub service account
        email = claim.get("email", "")
        if not email.endswith("@gcp-sa-pubsub.iam.gserviceaccount.com"):
            print(f"❌ Invalid service account: {email}")
            return False
        
        print(f"✅ Verified Pub/Sub request from {email}")
        return True
    
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return False

@app.post("/pubsub/push")
async def handle_pubsub_push(request: Request):
    """Handle Pub/Sub push messages with authentication."""
    
    # ✅ Verify authentication
    if not await verify_pubsub_token(request):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing Pub/Sub token"
        )
    
    # Rest of the handler...
```

```terraform
# Add SERVICE_URL environment variable
env {
  name  = "SERVICE_URL"
  value = "https://chained-log-consumer-${data.google_project.project.number}.${var.region}.run.app"
}
```

**Test:**
```bash
# Should fail without valid token
curl -X POST https://log-consumer.run.app/pubsub/push \
  -H "Content-Type: application/json" \
  -d '{"message":{"data":"dGVzdA=="}}'
# Expected: 401 Unauthorized

# Should succeed with valid Pub/Sub token
# (Only testable from actual Pub/Sub service)
```

---

### 5. Add Request Size Limits

**File:** `infrastructure/docker/ag-ui-frontend/src/app/api/ui-error-report/route.ts`

**Vulnerability:** Unbounded request size can exhaust memory

**Fix:**

```typescript
export async function POST(request: NextRequest) {
  const ip = request.ip ?? request.headers.get('x-forwarded-for') ?? 'unknown';
  
  // Check rate limit first
  if (!checkRateLimit(ip, 10, 60000)) {
    return NextResponse.json(
      { error: 'Rate limit exceeded. Please try again later.' },
      { status: 429, headers: { 'Retry-After': '60' } }
    );
  }
  
  // ✅ Check Content-Length before parsing
  const contentLength = request.headers.get('content-length');
  const MAX_SIZE = 10 * 1024; // 10KB max
  
  if (contentLength && parseInt(contentLength) > MAX_SIZE) {
    return NextResponse.json(
      { error: 'Request payload too large. Maximum size: 10KB' },
      { status: 413 }
    );
  }
  
  try {
    const body = await request.json() as UIErrorReport;
    
    // Validate required fields
    if (!body.message) {
      return NextResponse.json(
        { error: "Missing required field: message" },
        { status: 400 }
      );
    }
    
    // ✅ Truncate fields if too long
    if (body.message.length > 1000) {
      body.message = body.message.substring(0, 997) + '...';
    }
    if (body.stack && body.stack.length > 5000) {
      body.stack = body.stack.substring(0, 4997) + '...';
    }
    
    // ✅ Validate URL format if provided
    if (body.url) {
      try {
        new URL(body.url);
        // Limit URL length
        if (body.url.length > 500) {
          body.url = body.url.substring(0, 497) + '...';
        }
      } catch {
        body.url = '[invalid URL]';
      }
    }
    
    // Continue with processing...
    
  } catch (error) {
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        { error: 'Invalid JSON payload' },
        { status: 400 }
      );
    }
    
    console.error("❌ Error processing UI error report:", error);
    return NextResponse.json(
      { success: false, message: "Error report received but processing failed" },
      { status: 200 }
    );
  }
}
```

**Test:**
```bash
# Test with large payload
dd if=/dev/urandom bs=1024 count=20 | base64 > large_payload.txt
curl -X POST http://localhost:3000/api/ui-error-report \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"$(cat large_payload.txt)\"}"
# Expected: 413 Payload Too Large
```

---

### 6. Remove Public Access from Error Observer

**File:** `infrastructure/terraform/adk-agents.tf`

**Vulnerability:** Error observer accessible to anyone

**Fix:**

```terraform
# Update: infrastructure/terraform/adk-agents.tf

# Remove public access to error observer
# DELETE THIS:
# resource "google_cloud_run_v2_service_iam_member" "error_observer_public" {
#   project  = var.project_id
#   location = var.region
#   name     = google_cloud_run_v2_service.error_observer.name
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }

# Add service-to-service access for ADK agents
resource "google_cloud_run_v2_service_iam_member" "agents_to_error_observer" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.error_observer.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.adk_agents.email}"
}

# Add access for UI frontend
resource "google_cloud_run_v2_service_iam_member" "ui_to_error_observer" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.error_observer.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.adk_agents.email}"
}
```

```python
# Update agents to use service identity when calling error observer
# Add to shared/a2a_utils.py

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token as google_id_token

async def get_service_auth_token(target_url: str) -> Optional[str]:
    """
    Get an ID token for authenticating to another Cloud Run service.
    
    This uses Application Default Credentials (ADC) which automatically
    work on Cloud Run using the service account identity.
    """
    try:
        auth_req = GoogleRequest()
        token = google_id_token.fetch_id_token(auth_req, target_url)
        return token
    except Exception as e:
        print(f"⚠️ Failed to get service auth token: {e}")
        return None

# Update send_error_to_observer function
async def send_error_to_observer(
    error_event_dict: Dict[str, Any],
    error_observer_url: Optional[str] = None,
) -> bool:
    """Send an error event to the error_observer agent with authentication."""
    if not error_observer_url:
        error_observer_url = os.getenv("ERROR_OBSERVER_URL")
    
    if not error_observer_url:
        print("⚠️ Error observer URL not configured")
        return False
    
    try:
        # ✅ Get service-to-service auth token
        auth_token = await get_service_auth_token(error_observer_url)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Content-Type": "application/json"}
            
            # Add Authorization header if we have a token
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            
            response = await client.post(
                f"{error_observer_url}/a2a/tasks",
                json={
                    "message": {
                        "role": "user",
                        "parts": [{"text": json.dumps(error_event_dict)}],
                    },
                    "contextId": f"error-{datetime.utcnow().timestamp()}",
                    "metadata": {"error_event": error_event_dict},
                },
                headers=headers,
            )
            
            if response.status_code in (200, 201, 204):
                print(f"✅ Sent error event to observer")
                return True
            else:
                print(f"❌ Error observer returned {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ Failed to send error to observer: {e}")
        return False
```

**Update requirements.txt for all agents:**
```
google-auth>=2.23.0
```

**Test:**
```bash
# Should fail without service account token
curl -X POST https://error-observer.run.app/a2a/tasks \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"test"}]}}'
# Expected: 401 or 403

# Should succeed from another Cloud Run service
# (Only testable from actual service)
```

---

## 📋 Implementation Checklist

### Day 1: Core Security (4-6 hours)

- [ ] Add rate limiting to UI error endpoint
- [ ] Add request size limits and field truncation
- [ ] Move GITHUB_REPO to environment variable
- [ ] Add input validation and sanitization
- [ ] Write unit tests for new security features

### Day 2: Authentication & Data Protection (4-6 hours)

- [ ] Implement stack trace sanitization
- [ ] Remove public access from error observer
- [ ] Remove public access from log consumer
- [ ] Add Pub/Sub authentication verification
- [ ] Add service-to-service authentication
- [ ] Update Terraform configuration

### Day 3: Testing & Documentation (4-6 hours)

- [ ] Run security tests (manual + automated)
- [ ] Update deployment documentation
- [ ] Add security monitoring alerts
- [ ] Create incident response runbook
- [ ] Final security review

---

## 🧪 Testing Strategy

### Manual Security Testing

```bash
# 1. Test rate limiting
./tests/security/test_rate_limit.sh

# 2. Test authentication
./tests/security/test_authentication.sh

# 3. Test input sanitization
./tests/security/test_sanitization.sh

# 4. Test request size limits
./tests/security/test_size_limits.sh
```

### Automated Testing

```bash
# Run pytest security tests
pytest tests/security/ -v

# Run integration tests
pytest tests/integration/test_error_observer.py -v
```

---

## 📊 Success Criteria

✅ **Implementation is complete when:**

1. Rate limiting returns 429 after 10 requests/minute
2. Stack traces no longer contain passwords/tokens
3. Pub/Sub endpoint requires valid authentication
4. Request size is limited to 10KB
5. Error observer is not publicly accessible
6. GITHUB_REPO is configurable via environment
7. All security tests pass
8. Documentation is updated

---

## 🚨 Deployment Process

**DO NOT deploy to production until:**

1. All CRITICAL fixes are implemented
2. Security tests pass 100%
3. Code review by security team
4. Staging deployment tested for 24 hours
5. Monitoring alerts configured
6. Incident response plan documented

---

## 📞 Support & Questions

For questions about these security fixes:
- **Security Lead:** @secure-specialist
- **Infrastructure:** @create-botter
- **Documentation:** @support-master

---

**Status:** 🔴 BLOCKING  
**Next Review:** After fixes are implemented  
**Approval Required:** Security team sign-off before production deployment
