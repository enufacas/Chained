#!/bin/bash
# Trigger the intentional bug in code-reviewer agent for error observer testing
#
# This script sends a code review request containing the "test_error_observer"
# keyword to trigger the intentional ZeroDivisionError bug.
#
# Usage:
#   ./trigger-bug-test.sh [code-reviewer-url]
#
# If URL not provided, will try to get from environment or use localhost

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get code-reviewer URL
if [ -n "$1" ]; then
    CODE_REVIEWER_URL="$1"
elif [ -n "$CODE_REVIEWER_URL" ]; then
    # Use environment variable
    :
else
    echo -e "${YELLOW}No URL provided. Attempting to get from GCP...${NC}"
    if command -v gcloud &> /dev/null; then
        CODE_REVIEWER_URL=$(gcloud run services describe chained-code-reviewer \
            --region us-central1 \
            --format='value(status.url)' 2>/dev/null || echo "")
    fi
    
    if [ -z "$CODE_REVIEWER_URL" ]; then
        CODE_REVIEWER_URL="http://localhost:8084"
        echo -e "${YELLOW}Using localhost URL: $CODE_REVIEWER_URL${NC}"
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Error Observer Testing - Bug Trigger${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Target:${NC} $CODE_REVIEWER_URL"
echo ""

# Check if agent is reachable
echo -e "${YELLOW}1. Checking agent health...${NC}"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$CODE_REVIEWER_URL/health" || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "   ${GREEN}✅ Agent is healthy${NC}"
    
    # Get agent info
    AGENT_INFO=$(curl -s "$CODE_REVIEWER_URL/health")
    echo "   Info: $AGENT_INFO"
else
    echo -e "   ${RED}❌ Agent not reachable (HTTP $HEALTH_CHECK)${NC}"
    echo -e "   ${YELLOW}Continuing anyway (might be authentication issue)...${NC}"
fi

echo ""
echo -e "${YELLOW}2. Sending code review request with trigger keyword...${NC}"

# Prepare the request payload
REQUEST_PAYLOAD='{
  "message": {
    "role": "user",
    "parts": [
      {
        "text": "Please review this code:\n\n```python\n# test_error_observer - This keyword triggers the intentional bug\ndef example_function():\n    \"\"\"This is a test function for error observer testing\"\"\"\n    return \"Hello, World!\"\n\nif __name__ == \"__main__\":\n    result = example_function()\n    print(result)\n```\n\nPlease provide a comprehensive review including:\n- Code quality assessment\n- Best practices\n- Potential improvements\n- Security considerations"
      }
    ]
  },
  "contextId": "error-observer-test-'$(date +%s)'"
}'

# Send the request
echo "   Request payload prepared"
echo ""

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST "$CODE_REVIEWER_URL/a2a/tasks" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_PAYLOAD")

# Extract HTTP code and response body
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

echo -e "${YELLOW}3. Response received:${NC}"
echo "   HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    # Parse response
    TASK_STATE=$(echo "$RESPONSE_BODY" | grep -o '"state":"[^"]*"' | cut -d':' -f2 | tr -d '"')
    
    if [ "$TASK_STATE" = "failed" ]; then
        echo -e "   ${GREEN}✅ SUCCESS: Agent returned FAILED task (as expected)${NC}"
        echo ""
        echo -e "${GREEN}This means the bug was triggered successfully!${NC}"
        echo ""
        
        # Try to extract error message
        ERROR_MSG=$(echo "$RESPONSE_BODY" | grep -o '"text":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
        if [ -n "$ERROR_MSG" ]; then
            echo "   Error message: $ERROR_MSG"
        fi
        
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${GREEN}Next Steps:${NC}"
        echo -e "${BLUE}========================================${NC}"
        echo ""
        echo "1. Check error_observer agent received the error:"
        echo "   curl https://chained-error-observer-XXX.a.run.app/status"
        echo ""
        echo "2. Check GitHub for automatically created issue:"
        echo "   https://github.com/enufacas/Chained/issues"
        echo ""
        echo "3. Check A2A UI error observer status:"
        echo "   https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/"
        echo ""
        echo "4. Check Cloud Run logs for both services:"
        echo "   gcloud logging read 'resource.type=cloud_run_revision' --limit 50"
        echo ""
        
    elif [ "$TASK_STATE" = "completed" ]; then
        echo -e "   ${RED}❌ UNEXPECTED: Agent completed successfully${NC}"
        echo -e "   ${YELLOW}Bug may not have been triggered or was already removed${NC}"
        echo ""
        echo "   Full response:"
        echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
        
    else
        echo -e "   ${YELLOW}⚠️ Unknown task state: $TASK_STATE${NC}"
        echo ""
        echo "   Full response:"
        echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
    fi
else
    echo -e "   ${RED}❌ Request failed with HTTP $HTTP_CODE${NC}"
    echo ""
    echo "   Response:"
    echo "$RESPONSE_BODY"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "For more information, see: docs/ERROR_OBSERVER_TESTING.md"
echo ""
