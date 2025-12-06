"""
Test script for GCP client module

This script tests the GCP client functionality in both stub mode
(without credentials) and with real GCP credentials if available.
"""

import os
import sys

# Add parent directory to path so we can import gcp_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gcp_client import GCPClient, GCPClientError


def test_stub_mode():
    """Test that GCP client initializes properly without credentials"""
    print("\n=== Testing Stub Mode (No Credentials) ===")
    
    project_id = os.getenv("GCP_PROJECT_ID", "test-project-id")
    
    try:
        # This should initialize without error even without credentials
        client = GCPClient(project_id=project_id)
        print(f"✅ GCP client initialized with project: {project_id}")
        print(f"   GCS client: {client.gcs}")
        print(f"   Cloud Run client: {client.cloud_run}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize GCP client: {e}")
        return False


def test_bucket_operations():
    """Test bucket operations (requires credentials)"""
    print("\n=== Testing Bucket Operations ===")
    
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("⚠️  GCP_PROJECT_ID not set, skipping bucket tests")
        return True
    
    try:
        client = GCPClient(project_id=project_id)
        
        # Test bucket existence check (should not fail even if bucket doesn't exist)
        test_bucket = "nonexistent-bucket-12345"
        exists = client.bucket_exists(test_bucket)
        print(f"✅ Bucket existence check: {test_bucket} exists = {exists}")
        
        return True
    except Exception as e:
        print(f"❌ Bucket operations failed: {e}")
        return False


def test_service_operations():
    """Test Cloud Run service operations (requires credentials)"""
    print("\n=== Testing Service Operations ===")
    
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("⚠️  GCP_PROJECT_ID not set, skipping service tests")
        return True
    
    try:
        client = GCPClient(project_id=project_id)
        
        # Test service existence check
        test_service = "nonexistent-service"
        test_region = "us-central1"
        exists = client.service_exists(test_service, test_region)
        print(f"✅ Service existence check: {test_service} in {test_region} exists = {exists}")
        
        return True
    except Exception as e:
        print(f"❌ Service operations failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=== GCP Client Test Suite ===")
    print(f"GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID', 'Not set')}")
    
    results = []
    
    # Always run stub mode test
    results.append(("Stub Mode", test_stub_mode()))
    
    # Run GCP operations tests if credentials available
    if os.getenv("GCP_PROJECT_ID"):
        results.append(("Bucket Operations", test_bucket_operations()))
        results.append(("Service Operations", test_service_operations()))
    else:
        print("\n⚠️  Set GCP_PROJECT_ID to run full integration tests")
    
    # Print summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    return all(result for _, result in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
