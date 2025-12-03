#!/usr/bin/env python3
"""
Test script for error_observer agent

This script tests the error_observer agent locally without needing full deployment.

Usage:
    python test_error_observer.py
"""

import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.error_event import ErrorEvent


def test_error_event_from_exception():
    """Test creating ErrorEvent from a Python exception."""
    print("✓ Testing ErrorEvent.from_exception()...")
    
    try:
        raise ValueError("Test error message")
    except Exception as e:
        event = ErrorEvent.from_exception(
            service="test-agent",
            exception=e,
            source_agent="test-agent",
            source_channel="runtime",
            metadata={"test": "data"}
        )
        
        assert event.service == "test-agent"
        assert event.error_message == "Test error message"
        assert event.source_channel == "runtime"
        assert event.stack_trace is not None
        assert "ValueError" in event.stack_trace
        assert event.metadata == {"test": "data"}
        
        print(f"  ✅ Created error event: {event.error_hash}")
        print(f"  ✅ Service: {event.service}")
        print(f"  ✅ Message: {event.error_message}")
        print(f"  ✅ Has stack trace: {len(event.stack_trace) > 0}")


def test_error_event_from_ui_error():
    """Test creating ErrorEvent from UI error."""
    print("\n✓ Testing ErrorEvent.from_ui_error()...")
    
    event = ErrorEvent.from_ui_error(
        message="Cannot read property of undefined",
        stack="TypeError: Cannot read property...\n    at Component...",
        url="https://example.com/app",
        user_agent="Mozilla/5.0...",
        extra={"component": "PipelineView", "line": 123}
    )
    
    assert event.service == "a2a-ui"
    assert event.error_message == "Cannot read property of undefined"
    assert event.source_channel == "ui"
    assert event.stack_trace is not None
    assert event.a2a_ui_url == "https://example.com/app"
    assert len(event.logs) > 0
    
    print(f"  ✅ Created UI error event: {event.error_hash}")
    print(f"  ✅ Service: {event.service}")
    print(f"  ✅ Channel: {event.source_channel}")
    print(f"  ✅ Logs count: {len(event.logs)}")


def test_error_event_from_cloudrun_log():
    """Test creating ErrorEvent from Cloud Run log entry."""
    print("\n✓ Testing ErrorEvent.from_cloudrun_log()...")
    
    log_entry = {
        "textPayload": "Database connection timeout",
        "severity": "ERROR",
        "timestamp": "2025-12-02T10:00:00Z",
        "resource": {
            "type": "cloud_run_revision",
            "labels": {
                "service_name": "chained-blog-writer",
                "location": "us-central1"
            }
        }
    }
    
    event = ErrorEvent.from_cloudrun_log(
        service_name="chained-blog-writer",
        log_entry=log_entry,
        region="us-central1",
        environment="production"
    )
    
    assert event.service == "chained-blog-writer"
    assert event.error_message == "Database connection timeout"
    assert event.source_channel == "cloudrun"
    assert event.region == "us-central1"
    
    print(f"  ✅ Created log error event: {event.error_hash}")
    print(f"  ✅ Service: {event.service}")
    print(f"  ✅ Region: {event.region}")
    print(f"  ✅ Channel: {event.source_channel}")


def test_error_event_to_a2a_artifact():
    """Test converting ErrorEvent to A2A artifact."""
    print("\n✓ Testing ErrorEvent.to_a2a_artifact()...")
    
    event = ErrorEvent(
        service="test-service",
        error_message="Test error",
        error_hash="abc123",
        first_seen="2025-12-02T10:00:00Z",
        last_seen="2025-12-02T10:00:00Z",
        source_channel="runtime"
    )
    
    artifact = event.to_a2a_artifact()
    
    assert artifact["name"] == "error_event"
    assert artifact["type"] == "error_event"
    assert isinstance(artifact["data"], str)
    
    # Verify it's valid JSON
    data = json.loads(artifact["data"])
    assert data["service"] == "test-service"
    assert data["error_message"] == "Test error"
    
    print(f"  ✅ Created A2A artifact")
    print(f"  ✅ Artifact name: {artifact['name']}")
    print(f"  ✅ Artifact type: {artifact['type']}")
    print(f"  ✅ Data is valid JSON: {len(artifact['data'])} bytes")


def test_error_event_to_github_payload():
    """Test converting ErrorEvent to GitHub dispatch payload."""
    print("\n✓ Testing ErrorEvent.to_github_payload()...")
    
    event = ErrorEvent(
        service="test-service",
        region="us-central1",
        environment="production",
        error_message="Test error",
        error_hash="abc123",
        first_seen="2025-12-02T10:00:00Z",
        last_seen="2025-12-02T10:00:00Z",
        occurrences=5,
        source_agent="test-agent",
        source_channel="runtime",
        a2a_ui_url="https://ui.example.com",
        stack_trace="Test stack trace",
        metadata={"key": "value"},
        logs=["log1", "log2"],
        run_console_url="https://console.cloud.google.com"
    )
    
    payload = event.to_github_payload()
    
    # GitHub repository_dispatch API allows max 10 properties
    assert isinstance(payload, dict)
    assert len(payload) <= 10, f"GitHub payload has {len(payload)} fields, max 10 allowed"
    
    # Verify essential fields are included
    assert payload["service"] == "test-service"
    assert payload["error_message"] == "Test error"
    assert payload["error_hash"] == "abc123"
    assert payload["stack_trace"] == "Test stack trace"
    assert payload["first_seen"] == "2025-12-02T10:00:00Z"
    assert payload["last_seen"] == "2025-12-02T10:00:00Z"
    assert payload["occurrences"] == 5
    assert payload["source_agent"] == "test-agent"
    assert payload["a2a_ui_url"] == "https://ui.example.com"
    assert payload["environment"] == "production"
    
    # Verify less important fields are NOT included (to stay under limit)
    assert "metadata" not in payload, "metadata should be excluded to stay under 10 field limit"
    assert "logs" not in payload, "logs should be excluded to stay under 10 field limit"
    assert "region" not in payload, "region should be excluded to stay under 10 field limit"
    
    print(f"  ✅ Created GitHub payload with {len(payload)} fields (max 10)")
    print(f"  ✅ Payload keys: {', '.join(payload.keys())}")
    print(f"  ✅ Service: {payload['service']}")


def test_error_hash_consistency():
    """Test that error hash is consistent for same inputs."""
    print("\n✓ Testing error hash consistency...")
    
    hash1 = ErrorEvent.compute_error_hash("service1", "error msg", "type1")
    hash2 = ErrorEvent.compute_error_hash("service1", "error msg", "type1")
    hash3 = ErrorEvent.compute_error_hash("service2", "error msg", "type1")
    
    assert hash1 == hash2, "Same inputs should produce same hash"
    assert hash1 != hash3, "Different inputs should produce different hash"
    
    print(f"  ✅ Hash consistency verified")
    print(f"  ✅ Hash 1: {hash1}")
    print(f"  ✅ Hash 2: {hash2} (same)")
    print(f"  ✅ Hash 3: {hash3} (different)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Error Observer Components")
    print("=" * 60)
    
    tests = [
        test_error_event_from_exception,
        test_error_event_from_ui_error,
        test_error_event_from_cloudrun_log,
        test_error_event_to_a2a_artifact,
        test_error_event_to_github_payload,
        test_error_hash_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {test_func.__name__}")
            print(f"   {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {test_func.__name__}")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
