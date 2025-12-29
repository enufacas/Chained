#!/usr/bin/env python3
"""
Inventory all GitHub workflows and determine their enabled/disabled status.
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def parse_workflow(file_path: Path) -> Optional[Dict]:
    """Parse a workflow file and extract relevant information."""
    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)
            
        # Determine if workflow is disabled
        # A workflow is considered disabled if:
        # 1. It's in the archive directory
        # 2. It has no triggers (on: section)
        # 3. All triggers are commented out or workflow_dispatch only with no other triggers
        
        is_archived = 'archive' in str(file_path)
        
        on_section = content.get('on', content.get(True, {}))
        
        # Check if workflow has any active triggers
        has_active_triggers = False
        trigger_types = []
        
        if on_section:
            if isinstance(on_section, dict):
                trigger_types = list(on_section.keys())
                # workflow_dispatch alone doesn't count as "active" for scheduled workflows
                has_active_triggers = len(trigger_types) > 0 and not (
                    len(trigger_types) == 1 and trigger_types[0] == 'workflow_dispatch'
                )
            elif isinstance(on_section, list):
                trigger_types = on_section
                has_active_triggers = len(trigger_types) > 0
            elif isinstance(on_section, str):
                trigger_types = [on_section]
                has_active_triggers = True
        
        # Get workflow name
        workflow_name = content.get('name', file_path.stem)
        
        return {
            'file': str(file_path.relative_to(Path.cwd())),
            'name': workflow_name,
            'is_archived': is_archived,
            'has_triggers': has_active_triggers,
            'triggers': trigger_types,
            'enabled': has_active_triggers and not is_archived,
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def inventory_workflows(workflows_dir: Path) -> Dict[str, List[Dict]]:
    """Inventory all workflows and categorize them."""
    enabled = []
    disabled = []
    
    # Find all workflow files
    workflow_files = sorted(workflows_dir.rglob('*.yml')) + sorted(workflows_dir.rglob('*.yaml'))
    
    for file_path in workflow_files:
        workflow_info = parse_workflow(file_path)
        if workflow_info:
            if workflow_info['enabled']:
                enabled.append(workflow_info)
            else:
                disabled.append(workflow_info)
    
    return {
        'enabled': enabled,
        'disabled': disabled,
        'total': len(enabled) + len(disabled),
        'enabled_count': len(enabled),
        'disabled_count': len(disabled),
        'inventory_date': datetime.now().isoformat(),
    }


def generate_report(inventory: Dict) -> str:
    """Generate a human-readable report of the workflow inventory."""
    report = []
    report.append("=" * 80)
    report.append("GITHUB WORKFLOWS INVENTORY REPORT")
    report.append(f"Generated: {inventory['inventory_date']}")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"Total Workflows: {inventory['total']}")
    report.append(f"Enabled: {inventory['enabled_count']}")
    report.append(f"Disabled: {inventory['disabled_count']}")
    report.append("")
    
    report.append("=" * 80)
    report.append("ENABLED WORKFLOWS")
    report.append("=" * 80)
    for i, workflow in enumerate(inventory['enabled'], 1):
        report.append(f"{i}. {workflow['name']}")
        report.append(f"   File: {workflow['file']}")
        report.append(f"   Triggers: {', '.join(workflow['triggers'])}")
        report.append("")
    
    report.append("=" * 80)
    report.append("DISABLED WORKFLOWS")
    report.append("=" * 80)
    for i, workflow in enumerate(inventory['disabled'], 1):
        report.append(f"{i}. {workflow['name']}")
        report.append(f"   File: {workflow['file']}")
        report.append(f"   Reason: {'Archived' if workflow['is_archived'] else 'No active triggers'}")
        report.append("")
    
    return "\n".join(report)


def main():
    """Main function."""
    # Get workflows directory
    repo_root = Path('/home/runner/work/Chained/Chained')
    workflows_dir = repo_root / '.github' / 'workflows'
    
    # Inventory workflows
    print("Inventorying workflows...")
    inventory = inventory_workflows(workflows_dir)
    
    # Generate report
    report = generate_report(inventory)
    
    # Save inventory as JSON
    inventory_file = repo_root / 'workflow_inventory.json'
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"Inventory saved to: {inventory_file}")
    
    # Save report as text
    report_file = repo_root / 'workflow_inventory_report.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_file}")
    
    # Print summary
    print("\n" + report)


if __name__ == '__main__':
    main()
