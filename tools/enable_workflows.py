#!/usr/bin/env python3
"""
Re-enable previously disabled GitHub workflows using saved metadata.
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional


def remove_disable_metadata(content: str) -> str:
    """Remove the disable metadata header from workflow file."""
    lines = content.split('\n')
    
    # Find the end of the metadata section
    start_found = False
    end_idx = 0
    
    for i, line in enumerate(lines):
        if '# WORKFLOW DISABLED' in line or '# ============================================================================' in line:
            start_found = True
        elif start_found and line.strip() and not line.strip().startswith('#'):
            end_idx = i
            break
    
    if end_idx > 0:
        return '\n'.join(lines[end_idx:])
    return content


def restore_workflow_triggers(file_path: Path, original_triggers: List[str], metadata: Dict, repo_root: Path) -> bool:
    """
    Restore original triggers to a disabled workflow.
    Returns True if successful, False otherwise.
    """
    try:
        # Read current content
        with open(file_path, 'r') as f:
            current_content = f.read()
        
        # Remove disable metadata
        clean_content = remove_disable_metadata(current_content)
        
        # Parse YAML
        workflow_data = yaml.safe_load(clean_content)
        
        # Find the original workflow in backup
        # The backup has the full directory structure
        relative_path = file_path.relative_to(repo_root)
        backup_location = repo_root / metadata['backup_location'] / relative_path
        
        if backup_location.exists():
            # Load original workflow from backup
            with open(backup_location, 'r') as f:
                original_content = f.read()
            
            # Write original content back (complete restore)
            with open(file_path, 'w') as f:
                f.write(original_content)
            
            return True
        else:
            print(f"  ⚠️  Backup not found: {backup_location}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error restoring {file_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def enable_workflows(repo_root: Path, metadata_file: Path, specific_workflow: Optional[str] = None) -> Dict:
    """Enable workflows based on saved metadata."""
    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    workflows_to_enable = metadata['workflows']
    
    # Filter to specific workflow if requested
    if specific_workflow:
        workflows_to_enable = [w for w in workflows_to_enable if w['file'] == specific_workflow]
        if not workflows_to_enable:
            print(f"❌ Workflow not found in metadata: {specific_workflow}")
            return {'enabled': 0, 'failed': 0}
    
    print(f"\n{'='*80}")
    print(f"RE-ENABLING {len(workflows_to_enable)} WORKFLOWS")
    print(f"Original disable date: {metadata['disable_date']}")
    print(f"{'='*80}\n")
    
    enabled_count = 0
    failed_count = 0
    
    for workflow in workflows_to_enable:
        file_path = repo_root / workflow['file']
        
        if file_path.exists():
            print(f"Re-enabling: {workflow['name']}")
            success = restore_workflow_triggers(file_path, workflow['original_triggers'], metadata, repo_root)
            
            if success:
                print(f"  ✅ Restored triggers: {', '.join(workflow['original_triggers'])}")
                enabled_count += 1
            else:
                failed_count += 1
        else:
            print(f"  ⚠️  File not found: {workflow['file']}")
            failed_count += 1
    
    print(f"\n{'='*80}")
    print(f"RE-ENABLE OPERATION COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Successfully re-enabled: {enabled_count}")
    print(f"❌ Failed to re-enable: {failed_count}")
    
    return {
        'enabled': enabled_count,
        'failed': failed_count,
        'workflows': workflows_to_enable,
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Re-enable previously disabled workflows')
    parser.add_argument('--workflow', type=str, help='Specific workflow file to re-enable')
    parser.add_argument('--list', action='store_true', help='List all disabled workflows')
    args = parser.parse_args()
    
    repo_root = Path('/home/runner/work/Chained/Chained')
    metadata_file = repo_root / 'workflow_disable_metadata.json'
    
    if not metadata_file.exists():
        print("❌ Error: workflow_disable_metadata.json not found!")
        print("No workflows have been disabled, or metadata file was deleted.")
        return 1
    
    # Load metadata for listing
    if args.list:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        print(f"\n{'='*80}")
        print(f"DISABLED WORKFLOWS (as of {metadata['disable_date']})")
        print(f"{'='*80}\n")
        
        for i, workflow in enumerate(metadata['workflows'], 1):
            print(f"{i}. {workflow['name']}")
            print(f"   File: {workflow['file']}")
            print(f"   Original triggers: {', '.join(workflow['original_triggers'])}")
            print()
        
        return 0
    
    # Re-enable workflows
    result = enable_workflows(repo_root, metadata_file, args.workflow)
    
    if result['enabled'] > 0:
        print("\n✅ Workflows have been re-enabled successfully!")
        print("They will now respond to their original triggers.")
    
    return 0 if result['failed'] == 0 else 1


if __name__ == '__main__':
    exit(main())
