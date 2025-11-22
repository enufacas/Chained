#!/usr/bin/env python3
"""
Example: Workflow with A/B Testing Integration

This example demonstrates how to integrate A/B testing into a workflow
using the new API and integration helpers.

Author: @APIs-architect
"""

import sys
import time
import random
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from ab_testing_integration import setup_workflow_testing


def simulate_workflow_task(config: dict) -> dict:
    """
    Simulate a workflow task with configurable parameters.
    
    Args:
        config: Configuration dictionary with task parameters
    
    Returns:
        Task result dictionary
    """
    timeout = config.get("timeout", 300)
    max_retries = config.get("max_retries", 3)
    batch_size = config.get("batch_size", 100)
    
    print(f"\n🚀 Running workflow task...")
    print(f"   Timeout: {timeout}s")
    print(f"   Max retries: {max_retries}")
    print(f"   Batch size: {batch_size}")
    
    # Simulate work with timing
    start_time = time.time()
    
    # Simulate processing time based on config
    # Shorter timeout = faster but more likely to fail
    # Larger batch size = more efficient but uses more resources
    processing_time = random.uniform(0.1, 0.3)
    time.sleep(processing_time)
    
    execution_time = time.time() - start_time
    
    # Simulate success/failure based on timeout
    # More generous timeout = higher success rate
    success_probability = min(0.95, timeout / 400.0)
    success = random.random() < success_probability
    
    # Simulate resource usage
    resource_usage = batch_size * 0.5 + random.uniform(-10, 10)
    
    return {
        "success": success,
        "execution_time": execution_time,
        "resource_usage": resource_usage,
        "items_processed": batch_size * 10,
        "error": None if success else "Task timeout exceeded"
    }


def main():
    """
    Main workflow execution with A/B testing integration.
    """
    print("="*60)
    print("  Workflow with A/B Testing Integration Example")
    print("="*60)
    
    # Define default configuration
    default_config = {
        "timeout": 300,      # 5 minutes
        "max_retries": 3,
        "batch_size": 100
    }
    
    # Setup A/B testing - this will automatically participate if an
    # experiment exists for this workflow
    integration, config = setup_workflow_testing(
        workflow_name="example-workflow",
        default_config=default_config
    )
    
    print(f"\n📋 Configuration selected:")
    print(f"   {config}")
    
    # Run the workflow task with the selected configuration
    result = simulate_workflow_task(config)
    
    # Record metrics based on outcome
    if result["success"]:
        print(f"\n✅ Task completed successfully!")
        print(f"   Execution time: {result['execution_time']:.3f}s")
        print(f"   Items processed: {result['items_processed']}")
        print(f"   Resource usage: {result['resource_usage']:.1f}%")
        
        # Record successful run
        integration.record_success(
            execution_time=result["execution_time"],
            metrics={
                "resource_usage": result["resource_usage"],
                "items_processed": result["items_processed"]
            }
        )
    else:
        print(f"\n❌ Task failed!")
        print(f"   Error: {result['error']}")
        print(f"   Execution time: {result['execution_time']:.3f}s")
        
        # Record failure
        integration.record_failure(
            execution_time=result["execution_time"],
            error=result["error"]
        )
    
    print("\n" + "="*60)
    print("  Workflow completed")
    print("="*60)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
