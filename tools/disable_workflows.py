#!/usr/bin/env python3
"""
Disable all enabled GitHub workflows by commenting out their triggers.
Preserves original state with metadata for future re-enabling.
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def add_disable_metadata(content: str, workflow_info: Dict, disable_date: str) -> str:
    """Add metadata comment to the top of the workflow file."""
    metadata = [
        "# ============================================================================",
        "# WORKFLOW DISABLED",
        f"# Disabled on: {disable_date}",
        f"# Original workflow name: {workflow_info['name']}",
        f"# Original triggers: {', '.join(workflow_info['triggers'])}",
        "# ",
        "# To re-enable: Use the tools/enable_workflows.py script with the",
        "# workflow_disable_metadata.json file to restore original triggers.",
        "# ============================================================================",
        "",
    ]
    return "\n".join(metadata) + "\n" + content


def disable_workflow_triggers(file_path: Path, workflow_info: Dict, disable_date: str) -> bool:
    """
    Disable a workflow by modifying triggers to keep only workflow_dispatch.
    Uses text-based approach to preserve file structure.
    Returns True if workflow was modified, False otherwise.
    """
    try:
        # Read the original file
        with open(file_path, 'r') as f:
            original_content = f.read()
        
        # Parse YAML to verify structure
        workflow_data = yaml.safe_load(original_content)
        
        # Check if workflow has triggers
        on_section = workflow_data.get('on', workflow_data.get(True, {}))
        if not on_section:
            print(f"  ⚠️  No triggers found in {file_path.name}")
            return False
        
        # Get workflow_dispatch config if it exists
        workflow_dispatch_config = {}
        if isinstance(on_section, dict):
            workflow_dispatch_config = on_section.get('workflow_dispatch', {})
        
        # Create the new on: section preserving workflow_dispatch
        if workflow_dispatch_config:
            # Parse just the workflow_dispatch section from original
            import re
            
            # Find the on: section start
            on_match = re.search(r'^on:\s*$', original_content, re.MULTILINE)
            if on_match:
                # Find workflow_dispatch section
                wd_match = re.search(
                    r'^\s+workflow_dispatch:.*?(?=^\s+\w+:|^[^\s]|\Z)',
                    original_content[on_match.end():],
                    re.MULTILINE | re.DOTALL
                )
                
                if wd_match:
                    wd_content = wd_match.group(0).rstrip()
                    new_on_section = f"on:\n{wd_content}\n"
                else:
                    new_on_section = "on:\n  workflow_dispatch:\n"
            else:
                new_on_section = "on:\n  workflow_dispatch:\n"
        else:
            new_on_section = "on:\n  workflow_dispatch:\n"
        
        # Replace the on: section with just workflow_dispatch
        # Find the on: section and replace it
        import re
        
        # Pattern to match on: section (from 'on:' to the next top-level key or jobs:)
        pattern = r'(^on:.*?)(?=^[a-z_-]+:|^jobs:)'
        replacement = new_on_section + '\n'
        
        new_content = re.sub(pattern, replacement, original_content, flags=re.MULTILINE | re.DOTALL)
        
        # Add metadata header
        final_content = add_disable_metadata(new_content, workflow_info, disable_date)
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(final_content)
        
        print(f"  ✅ Disabled: {workflow_info['name']}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error disabling {file_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_backup(workflows_dir: Path, backup_dir: Path, enabled_workflows: List[Dict], repo_root: Path):
    """Create backup of all enabled workflows before disabling."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCreating backup in {backup_dir}...")
    backup_count = 0
    
    for workflow in enabled_workflows:
        src_path = repo_root / workflow['file']
        if src_path.exists():
            # Create same directory structure in backup
            rel_path = Path(workflow['file'])
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, backup_path)
            backup_count += 1
    
    print(f"✅ Backed up {backup_count} workflows")
    return backup_count


def disable_all_workflows(repo_root: Path, inventory_file: Path) -> Dict:
    """Disable all enabled workflows and save metadata."""
    # Load inventory
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    
    enabled_workflows = inventory['enabled']
    disable_date = datetime.now().isoformat()
    
    print(f"\n{'='*80}")
    print(f"DISABLING {len(enabled_workflows)} ENABLED WORKFLOWS")
    print(f"Disable date: {disable_date}")
    print(f"{'='*80}\n")
    
    # Create backup directory with timestamp
    backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = repo_root / 'workflow_backups' / f'backup_{backup_timestamp}'
    workflows_dir = repo_root / '.github' / 'workflows'
    
    # Create backup
    backup_count = create_backup(workflows_dir, backup_dir, enabled_workflows, repo_root)
    
    # Disable workflows
    print(f"\nDisabling workflows...")
    disabled_count = 0
    failed_count = 0
    disable_metadata = {
        'disable_date': disable_date,
        'backup_location': str(backup_dir.relative_to(repo_root)),
        'total_enabled': len(enabled_workflows),
        'workflows': []
    }
    
    for workflow in enabled_workflows:
        file_path = repo_root / workflow['file']
        
        if file_path.exists():
            success = disable_workflow_triggers(file_path, workflow, disable_date)
            
            if success:
                disabled_count += 1
                disable_metadata['workflows'].append({
                    'file': workflow['file'],
                    'name': workflow['name'],
                    'original_triggers': workflow['triggers'],
                    'disabled_date': disable_date,
                })
            else:
                failed_count += 1
        else:
            print(f"  ⚠️  File not found: {workflow['file']}")
            failed_count += 1
    
    # Save disable metadata
    metadata_file = repo_root / 'workflow_disable_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(disable_metadata, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"DISABLE OPERATION COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Successfully disabled: {disabled_count}")
    print(f"❌ Failed to disable: {failed_count}")
    print(f"📦 Backup location: {backup_dir.relative_to(repo_root)}")
    print(f"📋 Metadata saved to: workflow_disable_metadata.json")
    print(f"\nTo re-enable workflows later, use: python3 tools/enable_workflows.py")
    
    return disable_metadata


def generate_disable_report(metadata: Dict, output_file: Path):
    """Generate a human-readable report of the disable operation."""
    report = []
    report.append("=" * 80)
    report.append("WORKFLOW DISABLE OPERATION REPORT")
    report.append(f"Date: {metadata['disable_date']}")
    report.append("=" * 80)
    report.append("")
    report.append(f"Total workflows disabled: {len(metadata['workflows'])}")
    report.append(f"Backup location: {metadata['backup_location']}")
    report.append("")
    report.append("=" * 80)
    report.append("DISABLED WORKFLOWS")
    report.append("=" * 80)
    
    for i, workflow in enumerate(metadata['workflows'], 1):
        report.append(f"\n{i}. {workflow['name']}")
        report.append(f"   File: {workflow['file']}")
        report.append(f"   Original triggers: {', '.join(workflow['original_triggers'])}")
        report.append(f"   Disabled: {workflow['disabled_date']}")
    
    report.append("\n" + "=" * 80)
    report.append("RE-ENABLING INSTRUCTIONS")
    report.append("=" * 80)
    report.append("\nTo re-enable these workflows, run:")
    report.append("  python3 tools/enable_workflows.py")
    report.append("\nOr to re-enable specific workflows:")
    report.append("  python3 tools/enable_workflows.py --workflow <workflow-file-path>")
    report.append("")
    
    report_text = "\n".join(report)
    
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    return report_text


def main():
    """Main function."""
    repo_root = Path('/home/runner/work/Chained/Chained')
    inventory_file = repo_root / 'workflow_inventory.json'
    
    if not inventory_file.exists():
        print("❌ Error: workflow_inventory.json not found!")
        print("Run tools/inventory_workflows.py first.")
        return 1
    
    # Disable all workflows
    metadata = disable_all_workflows(repo_root, inventory_file)
    
    # Generate report
    report_file = repo_root / 'workflow_disable_report.txt'
    report = generate_disable_report(metadata, report_file)
    print(f"\n📄 Report saved to: {report_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"• {len(metadata['workflows'])} workflows have been disabled")
    print(f"• All workflows now only respond to manual workflow_dispatch")
    print(f"• Original configurations backed up to: {metadata['backup_location']}")
    print(f"• Metadata saved for future re-enabling")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    exit(main())
