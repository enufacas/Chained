# Identity-Aware Proxy (IAP) Setup Guide

This guide explains how to enable browser-based Google authentication for the ADK API Server using Identity-Aware Proxy (IAP).

## Overview

IAP provides a zero-trust security layer that:
- Requires users to authenticate with Google before accessing the service
- Works seamlessly in browsers (no CLI or tokens needed)
- Can restrict access to specific users, groups, or domains

## Prerequisites

1. **Custom Domain**: You need a domain to point to the load balancer (e.g., `adk-api.yourdomain.com`)
2. **GCP Project**: IAP APIs must be enabled
3. **OAuth Consent Screen**: Must be configured in GCP Console

## Step 1: Configure OAuth Consent Screen

1. Go to [APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Choose user type:
   - **Internal**: Only users in your Google Workspace organization
   - **External**: Any Google account (requires verification for production)
3. Fill in the required information:
   - App name: `Chained ADK API`
   - User support email: Your email
   - Developer contact email: Your email
4. Save

## Step 2: Create OAuth Client Credentials

1. Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Select **Web application**
4. Name: `Chained ADK API IAP`
5. Under **Authorized redirect URIs**, add:
   ```
   https://iap.googleapis.com/v1/oauth/clientIds/YOUR_CLIENT_ID:handleRedirect
   ```
   (You'll need to update this after getting the client ID)
6. Click **Create**
7. Save the **Client ID** and **Client Secret**

## Step 3: Update Terraform Variables

Create or update `terraform.tfvars`:

```hcl
# Enable IAP
enable_iap = true

# OAuth credentials (from Step 2)
iap_oauth_client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
iap_oauth_client_secret = "YOUR_CLIENT_SECRET"

# Your custom domain
iap_domain = "adk-api.yourdomain.com"

# Who can access (use your email or Google group)
iap_allowed_members = [
  "user:your-email@gmail.com",
  # "group:team@yourdomain.com",
  # "domain:yourdomain.com"
]
```

## Step 4: Deploy Infrastructure

### Option A: Via GitHub Actions

1. Add secrets to your repository:
   - `IAP_OAUTH_CLIENT_ID`: Your OAuth client ID
   - `IAP_OAUTH_CLIENT_SECRET`: Your OAuth client secret

2. Trigger the `deploy-adk-agents` workflow with IAP variables

### Option B: Via CLI

```bash
cd infrastructure/terraform

# Initialize
terraform init

# Plan with IAP variables
terraform plan \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="region=us-central1" \
  -var="enable_iap=true" \
  -var="iap_oauth_client_id=YOUR_CLIENT_ID" \
  -var="iap_oauth_client_secret=YOUR_SECRET" \
  -var="iap_domain=adk-api.yourdomain.com" \
  -var='iap_allowed_members=["user:your-email@gmail.com"]'

# Apply
terraform apply
```

## Step 5: Configure DNS

After applying Terraform, get the load balancer IP:

```bash
terraform output iap_load_balancer_ip
```

Add a DNS A record:
```
Type: A
Name: adk-api (or your subdomain)
Value: <IP from terraform output>
TTL: 300
```

## Step 6: Wait for SSL Certificate

The managed SSL certificate takes 15-30 minutes to provision. Check status:

```bash
gcloud compute ssl-certificates describe chained-adk-api-server-cert \
  --global \
  --format="value(managed.status)"
```

Status should change from `PROVISIONING` to `ACTIVE`.

## Step 7: Update OAuth Redirect URI

1. Go back to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click on your OAuth client
3. Update **Authorized redirect URIs** with your actual client ID:
   ```
   https://iap.googleapis.com/v1/oauth/clientIds/YOUR_CLIENT_ID:handleRedirect
   ```

## Step 8: Access the Service

Navigate to your domain in a browser:
```
https://adk-api.yourdomain.com/list-apps
```

You'll be prompted to sign in with Google. After authentication, you'll have access to the API.

## Troubleshooting

### "Error 403: Access Denied"
- Check that your email is in `iap_allowed_members`
- Run: `gcloud iap web get-iam-policy chained-adk-api-server-backend`

### SSL Certificate Not Provisioning
- Verify DNS is pointing to the correct IP
- Check certificate status: `gcloud compute ssl-certificates list`
- Ensure the domain is publicly resolvable

### "Invalid redirect_uri"
- Update the OAuth client's authorized redirect URI
- Format: `https://iap.googleapis.com/v1/oauth/clientIds/CLIENT_ID:handleRedirect`

## Cost Considerations

IAP adds minimal cost:
- Load balancer: ~$18/month (forwarding rules)
- SSL certificate: Free (managed)
- IAP itself: Free

## Alternative: Quick Access Without IAP

If you just need quick access without setting up IAP:

### Option 1: Make service public (development only)
```bash
gcloud run services add-iam-policy-binding chained-adk-api-server \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Option 2: Use gcloud identity token (CLI access)
```bash
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" \
  https://chained-adk-api-server-xxx.a.run.app/list-apps
```

## Related Documentation

- [Google Cloud IAP Documentation](https://cloud.google.com/iap/docs)
- [Enabling IAP for Cloud Run](https://cloud.google.com/iap/docs/enabling-cloud-run)
- [ADK API Server Guide](ADK_DEV_UI_GUIDE.md)
