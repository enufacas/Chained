# AG-UI Security Guide

**Last Updated**: 2025-12-01  
**Status**: 📋 **Planning & Options**  
**Live URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/

---

## Overview

This guide covers security options for the AG-UI Frontend and its API endpoints. The primary concern is preventing unauthorized users from accessing the application and its endpoints, which could result in unauthorized Vertex AI API usage and associated costs.

### Current State

Currently, the AG-UI Frontend is deployed on Cloud Run with **public access** (`allUsers` has the `roles/run.invoker` role). This means:
- Anyone with the URL can access the frontend
- All API endpoints (including `/api/copilotkit`) are publicly accessible
- Every request to the chat feature triggers Vertex AI API calls
- **Cost risk**: Malicious users or bots can generate significant Vertex AI costs

### What Needs Protection

| Endpoint | Risk Level | Why It Matters |
|----------|------------|----------------|
| `/api/copilotkit` | 🔴 **Critical** | Each chat request calls Vertex AI (LLM costs) |
| `/api/pipeline` | 🟠 **High** | Creates pipelines calling multiple A2A agents |
| `/api/team` | 🟠 **High** | Team orchestration calls multiple agents |
| `/api/agent` | 🟠 **High** | Direct agent communication |
| Main UI pages | 🟡 **Medium** | Entry point to all API functionality |

---

## Security Options

### Option 1: Identity-Aware Proxy (IAP) - **Recommended**

**Best for**: User-facing applications requiring Google account authentication

IAP provides a security layer that:
- Requires users to sign in with Google accounts
- Allows fine-grained access control via IAM policies
- Handles OAuth 2.0 flows automatically
- Works seamlessly with Cloud Run

#### Implementation Steps

1. **Enable IAP for Cloud Run Service**

   ```bash
   # Enable IAP API
   gcloud services enable iap.googleapis.com
   
   # Configure OAuth consent screen (one-time setup)
   # Go to: https://console.cloud.google.com/apis/credentials/consent
   ```

2. **Update Terraform Configuration**

   Add to `infrastructure/terraform/adk-agents.tf`:

   ```hcl
   # =============================================================================
   # Identity-Aware Proxy (IAP) Configuration
   # =============================================================================
   
   # Note: IAP for Cloud Run is best configured through the GCP Console.
   # The steps below show the console-based approach which is more reliable.
   
   # Step 1: Remove public access from Cloud Run
   # Comment out or remove:
   # resource "google_cloud_run_v2_service_iam_member" "ag_ui_frontend_public" {
   #   ...
   # }
   
   # Step 2: Configure IAP via Console (see step 4 below)
   
   # Step 3: Grant IAP access to authorized users via IAM
   # In IAM, grant roles/iap.httpsResourceAccessor to users/groups
   ```

3. **Remove Public Access**

   Comment out or remove in `adk-agents.tf`:
   ```hcl
   # resource "google_cloud_run_v2_service_iam_member" "ag_ui_frontend_public" {
   #   ...
   # }
   ```

4. **Enable IAP via Console** (recommended)

   - Go to [IAP Settings](https://console.cloud.google.com/security/iap)
   - Find the Cloud Run service
   - Toggle IAP ON
   - Add authorized users/groups

#### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Strong authentication | ❌ Requires Google accounts |
| ✅ No code changes needed | ❌ Adds login step for users |
| ✅ Fine-grained IAM control | ❌ May add latency |
| ✅ Audit logging included | ❌ More complex initial setup |

---

### Option 2: API Gateway with Authentication

**Best for**: Protecting specific API endpoints while keeping UI public

API Gateway can protect only the expensive API endpoints (`/api/*`) while leaving the UI accessible.

#### Implementation Steps

1. **Create API Gateway Configuration**

   Create `infrastructure/api-gateway/openapi.yaml`:
   ```yaml
   swagger: "2.0"
   info:
     title: AG-UI API Gateway
     version: "1.0.0"
   schemes:
     - https
   produces:
     - application/json
   
   securityDefinitions:
     api_key:
       type: apiKey
       name: x-api-key
       in: header
   
   paths:
     /api/copilotkit:
       post:
         security:
           - api_key: []
         x-google-backend:
           # Replace {HASH} with your Cloud Run service hash (e.g., sguacxy5gq)
           # You can find this in your Cloud Run service URL
           address: https://chained-ag-ui-frontend-{HASH}-uc.a.run.app/api/copilotkit
         responses:
           "200":
             description: Success
   ```

2. **Deploy API Gateway**

   ```bash
   gcloud api-gateway apis create ag-ui-api
   gcloud api-gateway api-configs create ag-ui-config \
     --api=ag-ui-api \
     --openapi-spec=openapi.yaml
   gcloud api-gateway gateways create ag-ui-gateway \
     --api=ag-ui-api \
     --api-config=ag-ui-config \
     --location=us-central1
   ```

3. **Update Frontend to Use API Gateway**

   ```typescript
   // In frontend code, configure API base URL
   const API_BASE = process.env.NEXT_PUBLIC_API_GATEWAY_URL || '/api';
   ```

#### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Protects only API endpoints | ❌ More complex architecture |
| ✅ API keys are simple | ❌ Requires API key management |
| ✅ Rate limiting built-in | ❌ Additional service to manage |
| ✅ UI remains public | ❌ Added network hop/latency |

---

### Option 3: Application-Level Authentication (Next.js Middleware)

**Best for**: Custom authentication requirements or integration with existing auth systems

Implement authentication directly in the Next.js application using middleware.

#### Implementation Steps

1. **Create Auth Configuration**

   Create the middleware file at the **root of the `src/` directory** (Next.js looks for middleware.ts at the root of src/ when using the src directory pattern):
   
   **Full path**: `infrastructure/docker/ag-ui-frontend/src/middleware.ts`
   
   > **Note**: When using Next.js with a `src/` directory, middleware.ts must be placed at `src/middleware.ts`, NOT inside `src/app/`. This is a Next.js convention.
   
   ```typescript
   import { NextResponse } from 'next/server';
   import type { NextRequest } from 'next/server';
   
   // Simple API key authentication
   const API_KEYS = new Set(
     (process.env.ALLOWED_API_KEYS || '').split(',').filter(Boolean)
   );
   
   // Routes that require authentication
   const PROTECTED_ROUTES = [
     '/api/copilotkit',
     '/api/pipeline',
     '/api/team',
     '/api/agent',
   ];
   
   export function middleware(request: NextRequest) {
     const { pathname } = request.nextUrl;
     
     // Check if route needs protection
     const needsAuth = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
     
     if (!needsAuth) {
       return NextResponse.next();
     }
     
     // Check for API key
     const apiKey = request.headers.get('x-api-key') || 
                    request.nextUrl.searchParams.get('api_key');
     
     if (!apiKey || !API_KEYS.has(apiKey)) {
       return new NextResponse(
         JSON.stringify({ error: 'Unauthorized', message: 'Valid API key required' }),
         { status: 401, headers: { 'Content-Type': 'application/json' } }
       );
     }
     
     return NextResponse.next();
   }
   
   export const config = {
     matcher: '/api/:path*',
   };
   ```

2. **Add Environment Variable**

   Update `.env.example`:
   ```bash
   # Authentication
   ALLOWED_API_KEYS=key1,key2,key3
   ```

3. **Update Terraform for Secret**

   ```hcl
   # Add API keys secret
   env {
     name = "ALLOWED_API_KEYS"
     value_source {
       secret_key_ref {
         secret  = "ag-ui-api-keys"
         version = "latest"
       }
     }
   }
   ```

#### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Full control over auth logic | ❌ Must manage keys yourself |
| ✅ No additional GCP services | ❌ Less secure than IAP |
| ✅ Easy to integrate with other auth | ❌ Code changes required |
| ✅ Can implement custom policies | ❌ Must update frontend clients |

---

### Option 4: Cloud Run Service-to-Service Authentication

**Best for**: Protecting backend agents (not the frontend)

Keep the frontend public but protect the backend Cloud Run agents to only accept authenticated requests.

#### Implementation Steps

1. **Remove Public Access from Agents**

   Comment out in `adk-agents.tf`:
   ```hcl
   # resource "google_cloud_run_v2_service_iam_member" "academic_research_public" { ... }
   # resource "google_cloud_run_v2_service_iam_member" "blog_writer_public" { ... }
   # etc.
   ```

2. **Grant Frontend Service Account Invoker Role**

   ```hcl
   resource "google_cloud_run_v2_service_iam_member" "frontend_can_invoke_research" {
     project  = var.project_id
     location = var.region
     name     = google_cloud_run_v2_service.academic_research.name
     role     = "roles/run.invoker"
     member   = "serviceAccount:${google_service_account.adk_agents.email}"
   }
   ```

3. **Add ID Token to Frontend Agent Calls**

   Update agent call functions in `route.ts` to include authentication:
   ```typescript
   import { GoogleAuth } from 'google-auth-library';
   
   const auth = new GoogleAuth();
   
   async function callA2AAgentWithAuth(
     agentUrl: string, 
     message: string, 
     metadata?: Record<string, unknown>
   ) {
     // Get ID token client for the target Cloud Run service
     const client = await auth.getIdTokenClient(agentUrl);
     const authHeaders = await client.getRequestHeaders(agentUrl);
     
     const request = {
       message: { role: "user", parts: [{ text: message }] },
       metadata,
     };
     
     const response = await fetch(`${agentUrl}/a2a/tasks`, {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         ...authHeaders,  // Includes Authorization: Bearer <token>
       },
       body: JSON.stringify(request),
     });
     
     return response.json();
   }
   ```

#### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Protects backend agents | ❌ Frontend still public |
| ✅ Service-to-service security | ❌ Doesn't prevent frontend abuse |
| ✅ Uses GCP IAM | ❌ Additional code complexity |
| ✅ No user login required | ❌ Frontend Vertex AI still exposed |

---

### Option 5: Rate Limiting + Monitoring (Defense in Depth)

**Best for**: Adding as an additional layer to any of the above options

Implement rate limiting to prevent abuse even with authentication.

#### Implementation Steps

1. **Cloud Armor (WAF) Rate Limiting**

   ```hcl
   resource "google_compute_security_policy" "ag_ui_rate_limit" {
     name = "ag-ui-rate-limit"
     
     rule {
       action   = "rate_based_ban"
       priority = 1000
       match {
         versioned_expr = "SRC_IPS_V1"
         config {
           src_ip_ranges = ["*"]
         }
       }
       rate_limit_options {
         conform_action = "allow"
         exceed_action  = "deny(429)"
         rate_limit_threshold {
           count        = 100
           interval_sec = 60
         }
         ban_duration_sec = 600
       }
       description = "Rate limit: 100 requests per minute per IP"
     }
   }
   ```

2. **Application-Level Rate Limiting**

   Add to middleware:
   ```typescript
   const rateLimitMap = new Map<string, { count: number; resetTime: number }>();
   const RATE_LIMIT = 100;  // requests per window
   const WINDOW_MS = 60 * 1000;  // 1 minute
   
   function checkRateLimit(ip: string): boolean {
     const now = Date.now();
     const record = rateLimitMap.get(ip);
     
     if (!record || now > record.resetTime) {
       rateLimitMap.set(ip, { count: 1, resetTime: now + WINDOW_MS });
       return true;
     }
     
     if (record.count >= RATE_LIMIT) {
       return false;
     }
     
     record.count++;
     return true;
   }
   ```

3. **Set Up Billing Alerts**

   ```bash
   # Create budget alert for unexpected Vertex AI costs
   gcloud billing budgets create \
     --billing-account=YOUR_BILLING_ACCOUNT \
     --display-name="AG-UI Vertex AI Alert" \
     --budget-amount=100USD \
     --threshold-rule=percent=50 \
     --threshold-rule=percent=90 \
     --threshold-rule=percent=100
   ```

---

## Recommended Approach

For your use case (preventing unauthorized Vertex AI usage), we recommend a **layered approach**:

### Immediate (Quick Win)
1. **Implement Application-Level API Key Auth** (Option 3)
   - Fast to implement
   - No infrastructure changes
   - Can be deployed immediately

### Short-Term (1-2 weeks)
2. **Enable IAP** (Option 1)
   - Strongest protection
   - Google account authentication
   - Centralized access control

### Ongoing
3. **Add Rate Limiting** (Option 5)
   - Defense in depth
   - Protects against key leakage
   - Billing alerts for cost monitoring

### Implementation Checklist

```markdown
- [ ] Choose primary authentication method
- [ ] Create/update Terraform configuration
- [ ] Test authentication locally
- [ ] Deploy to staging/test environment
- [ ] Verify authorized users can access
- [ ] Verify unauthorized users are blocked
- [ ] Set up billing alerts
- [ ] Update documentation
- [ ] Communicate changes to users
```

---

## Quick Start: Minimal API Key Protection

For the fastest path to protection, add this middleware to your frontend:

1. **Create the middleware file**:
   ```bash
   touch infrastructure/docker/ag-ui-frontend/src/middleware.ts
   ```

2. **Add the middleware code** (see Option 3 above)

3. **Add environment variable**:
   ```bash
   # Generate a random API key
   openssl rand -hex 32
   
   # Add to Cloud Run
   # Service name for this project: chained-ag-ui-frontend
   gcloud run services update chained-ag-ui-frontend \
     --update-env-vars ALLOWED_API_KEYS=your-generated-key \
     --region=us-central1
   ```

4. **Update your frontend clients** to include the API key in requests

---

## Security Considerations

### Do's
- ✅ Use HTTPS (already enforced by Cloud Run)
- ✅ Rotate API keys periodically
- ✅ Monitor usage and costs
- ✅ Use least-privilege IAM roles
- ✅ Enable audit logging

### Don'ts
- ❌ Don't commit API keys to git
- ❌ Don't expose keys in client-side code
- ❌ Don't share keys via unencrypted channels
- ❌ Don't ignore billing alerts

---

## Related Documentation

- [Cloud Run Authentication Overview](https://cloud.google.com/run/docs/authenticating/overview)
- [Enabling IAP for Cloud Run](https://cloud.google.com/iap/docs/enabling-cloud-run)
- [API Gateway Authentication](https://cloud.google.com/api-gateway/docs/authenticate-users)
- [Cloud Armor Rate Limiting](https://cloud.google.com/armor/docs/configure-rate-limiting)

---

*This security guide should be reviewed and updated as security requirements evolve.*
