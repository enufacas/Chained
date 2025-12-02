"""
Log Consumer Agent - Cloud Run Log to Error Event Processor
=============================================================

This agent is a scaffold for consuming Cloud Run logs and converting them
into error_event tasks sent to the error_observer agent.

In a production setup, this would be triggered by:
- Cloud Logging -> Log Router -> Pub/Sub -> This agent
- Or: Cloud Run service subscribing to Pub/Sub topic

For now, this provides:
- Entry point function for processing log entries
- Example of how to map Cloud Run logs to error_event schema
- A2A integration for sending error events to error_observer
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Add shared utilities to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.a2a_utils import send_error_to_observer
from shared.error_event import ErrorEvent

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "log-consumer"
AGENT_DESCRIPTION = "Processes Cloud Run logs and converts ERROR-level entries to error events"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8091"))

ERROR_OBSERVER_URL = os.getenv("ERROR_OBSERVER_URL") or os.getenv("AGENT_ERROR_OBSERVER_URL")

# =============================================================================
# Models
# =============================================================================

class CloudRunLogEntry(BaseModel):
    """
    Simplified Cloud Run log entry structure.
    
    Based on Cloud Logging format:
    https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
    """
    
    textPayload: Optional[str] = None
    jsonPayload: Optional[Dict[str, Any]] = None
    severity: str = "DEFAULT"
    timestamp: str
    resource: Optional[Dict[str, Any]] = None
    labels: Optional[Dict[str, str]] = None
    insertId: Optional[str] = None

# =============================================================================
# Log Processing Functions
# =============================================================================

def extract_service_name(log_entry: CloudRunLogEntry) -> str:
    """
    Extract Cloud Run service name from log entry.
    
    Args:
        log_entry: The log entry
        
    Returns:
        Service name or "unknown-service"
    """
    if log_entry.resource:
        # Cloud Run resource format:
        # resource.type = "cloud_run_revision"
        # resource.labels.service_name = "chained-academic-research"
        labels = log_entry.resource.get("labels", {})
        service_name = labels.get("service_name") or labels.get("serviceName")
        if service_name:
            return service_name
    
    if log_entry.labels:
        # Try labels as fallback
        service_name = log_entry.labels.get("service_name") or log_entry.labels.get("serviceName")
        if service_name:
            return service_name
    
    return "unknown-service"

def should_process_log(log_entry: CloudRunLogEntry) -> bool:
    """
    Determine if a log entry should be processed as an error.
    
    Args:
        log_entry: The log entry
        
    Returns:
        True if this log should trigger an error event
    """
    # Only process ERROR severity logs
    if log_entry.severity not in ("ERROR", "CRITICAL", "ALERT", "EMERGENCY"):
        return False
    
    # Could add more filtering here:
    # - Ignore certain service names
    # - Ignore certain error patterns
    # - Rate limiting by error_hash
    
    return True

async def process_cloudrun_log_entry(log_entry: CloudRunLogEntry) -> Optional[Dict[str, Any]]:
    """
    Process a Cloud Run log entry and send to error_observer if it's an error.
    
    This is the main entry point for log processing.
    
    Args:
        log_entry: The log entry to process
        
    Returns:
        Processing result dict, or None if log was filtered out
    """
    print(f"📥 Processing log entry: severity={log_entry.severity}")
    
    # Filter non-error logs
    if not should_process_log(log_entry):
        print(f"   Skipped: severity {log_entry.severity} not an error")
        return None
    
    # Extract service name
    service_name = extract_service_name(log_entry)
    region = "us-central1"  # Default region
    
    # Try to extract region from resource labels
    if log_entry.resource:
        labels = log_entry.resource.get("labels", {})
        region = labels.get("location") or labels.get("region") or region
    
    # Convert to error event
    error_event = ErrorEvent.from_cloudrun_log(
        service_name=service_name,
        log_entry=log_entry.model_dump(),
        region=region,
        environment="production",
    )
    
    print(f"   Created error event: {error_event.error_hash} from {service_name}")
    
    # Send to error observer
    if ERROR_OBSERVER_URL:
        success = await send_error_to_observer(
            error_event.model_dump(),
            ERROR_OBSERVER_URL,
        )
        
        return {
            "success": success,
            "error_hash": error_event.error_hash,
            "service": service_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    else:
        print("⚠️ ERROR_OBSERVER_URL not configured, cannot send error event")
        return {
            "success": False,
            "error_hash": error_event.error_hash,
            "service": service_name,
            "message": "Error observer not configured",
        }

# =============================================================================
# FastAPI Application (for Pub/Sub push subscriptions)
# =============================================================================

app = FastAPI(title="Log Consumer Agent", version=AGENT_VERSION)

@app.post("/pubsub/push")
async def handle_pubsub_push(request: Request):
    """
    Handle Pub/Sub push messages containing Cloud Run logs.
    
    Pub/Sub push format:
    {
      "message": {
        "data": "base64-encoded-log-entry",
        "attributes": {...},
        "messageId": "...",
        "publishTime": "..."
      },
      "subscription": "..."
    }
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        
        # Decode Pub/Sub message data
        import base64
        data_encoded = message.get("data", "")
        data_decoded = base64.b64decode(data_encoded).decode("utf-8")
        
        # Parse as JSON (Cloud Logging JSON format)
        log_entry_dict = json.loads(data_decoded)
        
        # Convert to our model
        log_entry = CloudRunLogEntry(**log_entry_dict)
        
        # Process the log entry
        result = await process_cloudrun_log_entry(log_entry)
        
        if result:
            return {
                "status": "processed",
                "result": result,
            }
        else:
            return {
                "status": "filtered",
                "message": "Log entry did not match error criteria",
            }
    
    except Exception as e:
        print(f"❌ Error processing Pub/Sub message: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return 200 to acknowledge message even if processing failed
        # This prevents infinite retries
        return {
            "status": "error",
            "error": str(e),
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": AGENT_NAME,
        "version": AGENT_VERSION,
        "observer_configured": bool(ERROR_OBSERVER_URL),
    }

@app.get("/")
async def root():
    """Root endpoint with agent info."""
    return {
        "agent": AGENT_NAME,
        "description": AGENT_DESCRIPTION,
        "version": AGENT_VERSION,
        "endpoints": {
            "/pubsub/push": "Pub/Sub push endpoint for Cloud Logging",
            "/health": "Health check",
        },
        "configuration": {
            "error_observer_url": "configured" if ERROR_OBSERVER_URL else "not configured",
        },
    }

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print(f"🚀 Log Consumer Agent starting on port {PORT}")
    print(f"   Error observer URL: {ERROR_OBSERVER_URL or 'NOT CONFIGURED'}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
