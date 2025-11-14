#!/usr/bin/env python3
"""
Verify that all workflows that modify registry.json have proper concurrency control.
"""

import yaml
import sys
from pathlib import Path

# Workflows that modify registry.json (write operations)
REGISTRY_MODIFYING_WORKFLOWS = [
    '.github/workflows/agent-spawner.yml',
    '.github/workflows/learning-based-agent-spawner.yml',
    '.github/workflows/agent-evaluator.yml'
]

# Workflows that only read registry.json (no concurrency control needed)
REGISTRY_READING_WORKFLOWS = [
    '.github/workflows/agent-issue-discussion.yml',
    '.github/workflows/agent-data-sync.yml'
]

REQUIRED_CONCURRENCY_GROUP = 'agent-registry-updates'

def check_workflow(workflow_path: str, should_have_concurrency: bool) -> bool:
    """Check if a workflow has proper concurrency control."""
    try:
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        has_concurrency = 'concurrency' in workflow
        
        if should_have_concurrency:
            if not has_concurrency:
                print(f"❌ {workflow_path}: Missing concurrency control!")
                return False
            
            group = workflow['concurrency'].get('group')
            cancel = workflow['concurrency'].get('cancel-in-progress')
            
            if group != REQUIRED_CONCURRENCY_GROUP:
                print(f"❌ {workflow_path}: Wrong concurrency group (expected '{REQUIRED_CONCURRENCY_GROUP}', got '{group}')")
                return False
            
            if cancel is not False:
                print(f"❌ {workflow_path}: cancel-in-progress should be false (got {cancel})")
                return False
            
            print(f"✅ {workflow_path}: Properly configured")
            return True
        else:
            if has_concurrency:
                print(f"⚠️  {workflow_path}: Has concurrency control (not needed for read-only)")
            else:
                print(f"✅ {workflow_path}: Read-only (no concurrency control needed)")
            return True
            
    except Exception as e:
        print(f"❌ {workflow_path}: Error - {e}")
        return False

def main():
    print("🔍 Verifying registry.json concurrency control...\n")
    
    all_passed = True
    
    print("📝 Checking workflows that MODIFY registry.json:")
    for workflow in REGISTRY_MODIFYING_WORKFLOWS:
        if not check_workflow(workflow, should_have_concurrency=True):
            all_passed = False
    
    print("\n📖 Checking workflows that READ registry.json:")
    for workflow in REGISTRY_READING_WORKFLOWS:
        if not check_workflow(workflow, should_have_concurrency=False):
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All workflows properly configured!")
        print("\n🎯 Summary:")
        print(f"  - {len(REGISTRY_MODIFYING_WORKFLOWS)} workflows with concurrency control")
        print(f"  - {len(REGISTRY_READING_WORKFLOWS)} read-only workflows")
        print(f"  - Concurrency group: {REQUIRED_CONCURRENCY_GROUP}")
        print("\n🚀 Registry merge conflicts should be eliminated!")
        return 0
    else:
        print("❌ Some workflows need attention!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
