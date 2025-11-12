#!/usr/bin/env python3
"""
Dynamic Workflow Orchestrator

Automatically adjusts workflow schedules based on API usage and burn rate.
Updates workflow files with appropriate cron schedules dynamically.

Features:
- Monitors API usage via copilot-usage-tracker
- Updates workflow cron schedules automatically
- Preserves workflow structure and logic
- Backs up original workflows before modification
- Validates updated workflows
"""

import os
import sys
import re
import json
import shutil
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    # Import using importlib to handle dash in filename
    import importlib.util
    spec = importlib.util.spec_from_file_location("copilot_usage_tracker", 
                                                    os.path.join(os.path.dirname(__file__), "copilot-usage-tracker.py"))
    copilot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copilot_module)
    CopilotUsageTracker = copilot_module.CopilotUsageTracker
except ImportError:
    print("Error: Could not import copilot_usage_tracker", file=sys.stderr)
    print("Make sure copilot-usage-tracker.py is in the tools directory", file=sys.stderr)
    sys.exit(1)


class WorkflowOrchestrator:
    """Orchestrate dynamic workflow scheduling"""
    
    # Workflow files to manage
    MANAGED_WORKFLOWS = {
        'learn-tldr': '.github/workflows/learn-from-tldr.yml',
        'learn-hn': '.github/workflows/learn-from-hackernews.yml',
        'idea-generator': '.github/workflows/idea-generator.yml',
        'ai-friend': '.github/workflows/ai-friend-daily.yml',
        'agent-spawner': '.github/workflows/agent-spawner.yml',
    }
    
    def __init__(self, repo_root: str = None, dry_run: bool = False):
        """
        Initialize the orchestrator.
        
        Args:
            repo_root: Root directory of the repository
            dry_run: If True, don't actually modify files
        """
        self.repo_root = repo_root or os.getcwd()
        self.dry_run = dry_run
        self.tracker = CopilotUsageTracker()
        self.backup_dir = os.path.join(self.repo_root, '.github', 'workflow-backups')
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_workflow(self, workflow_path: str) -> str:
        """
        Backup a workflow file before modification.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Path to backup file
        """
        full_path = os.path.join(self.repo_root, workflow_path)
        
        if not os.path.exists(full_path):
            print(f"Warning: Workflow file not found: {workflow_path}", file=sys.stderr)
            return None
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        workflow_name = os.path.basename(workflow_path)
        backup_path = os.path.join(self.backup_dir, f"{workflow_name}.{timestamp}.bak")
        
        shutil.copy2(full_path, backup_path)
        print(f"✓ Backed up {workflow_path} to {backup_path}")
        
        return backup_path
    
    def update_workflow_schedule(self, workflow_path: str, new_cron: str) -> bool:
        """
        Update the cron schedule in a workflow file.
        
        Args:
            workflow_path: Path to workflow file
            new_cron: New cron schedule
            
        Returns:
            True if successful
        """
        full_path = os.path.join(self.repo_root, workflow_path)
        
        if not os.path.exists(full_path):
            print(f"Warning: Workflow file not found: {workflow_path}", file=sys.stderr)
            return False
        
        # Read workflow file
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Backup before modifying
        if not self.dry_run:
            self.backup_workflow(workflow_path)
        
        # Pattern to match cron schedule
        # Matches: - cron: '0 8,20 * * *'
        cron_pattern = r"(\s*-\s*cron:\s*['\"])([^'\"]+)(['\"])"
        
        # Check if cron schedule exists
        if not re.search(cron_pattern, content):
            print(f"Warning: No cron schedule found in {workflow_path}", file=sys.stderr)
            return False
        
        # Replace cron schedule
        new_content = re.sub(
            cron_pattern,
            rf"\g<1>{new_cron}\g<3>",
            content,
            count=1  # Only replace first occurrence (under 'schedule:')
        )
        
        if new_content == content:
            print(f"Info: No changes needed for {workflow_path}")
            return True
        
        # Write updated content
        if self.dry_run:
            print(f"[DRY RUN] Would update {workflow_path} with cron: {new_cron}")
            return True
        else:
            with open(full_path, 'w') as f:
                f.write(new_content)
            print(f"✓ Updated {workflow_path} with cron: {new_cron}")
            return True
    
    def update_all_workflows(self, mode: Optional[str] = None) -> Dict[str, bool]:
        """
        Update all managed workflows based on current usage mode.
        
        Args:
            mode: Force a specific mode ('aggressive', 'normal', 'conservative')
                  If None, mode is determined from usage stats
        
        Returns:
            Dictionary of workflow name to update success status
        """
        # Get usage stats and recommended frequencies
        stats = self.tracker.estimate_copilot_usage()
        selected_mode = mode or stats.recommended_mode
        frequencies = self.tracker.get_workflow_frequencies(selected_mode)
        
        print("\n" + "="*70)
        print(f"🎛️  Workflow Orchestrator - {selected_mode.upper()} Mode")
        print("="*70 + "\n")
        
        print(f"API Usage: {stats.used}/{stats.total_quota} ({(stats.used/stats.total_quota)*100:.1f}%)")
        print(f"Burn Rate: {stats.current_burn_rate:.1f} requests/day")
        print(f"Recommended Mode: {stats.recommended_mode}")
        if mode and mode != stats.recommended_mode:
            print(f"⚠️  Overriding with forced mode: {mode}")
        print()
        
        results = {}
        
        for workflow_name, workflow_path in self.MANAGED_WORKFLOWS.items():
            if workflow_name in frequencies:
                new_cron = frequencies[workflow_name]
                success = self.update_workflow_schedule(workflow_path, new_cron)
                results[workflow_name] = success
            else:
                print(f"Warning: No frequency defined for {workflow_name}", file=sys.stderr)
                results[workflow_name] = False
        
        print("\n" + "="*70)
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"\n✓ Updated {successful}/{total} workflows successfully")
        
        if not self.dry_run:
            print(f"✓ Backups saved to {self.backup_dir}")
        
        return results
    
    def get_current_schedules(self) -> Dict[str, str]:
        """
        Get current cron schedules from all managed workflows.
        
        Returns:
            Dictionary of workflow name to current cron schedule
        """
        schedules = {}
        cron_pattern = r"-\s*cron:\s*['\"]([^'\"]+)['\"]"
        
        for workflow_name, workflow_path in self.MANAGED_WORKFLOWS.items():
            full_path = os.path.join(self.repo_root, workflow_path)
            
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                
                match = re.search(cron_pattern, content)
                if match:
                    schedules[workflow_name] = match.group(1)
                else:
                    schedules[workflow_name] = "No schedule found"
            else:
                schedules[workflow_name] = "File not found"
        
        return schedules
    
    def print_status(self):
        """Print current workflow schedules and recommended changes"""
        print("\n" + "="*70)
        print("📊 Current Workflow Schedules")
        print("="*70 + "\n")
        
        current = self.get_current_schedules()
        stats = self.tracker.estimate_copilot_usage()
        recommended = self.tracker.get_workflow_frequencies(stats.recommended_mode)
        
        print(f"Recommended Mode: {stats.recommended_mode.upper()}\n")
        
        for workflow_name in self.MANAGED_WORKFLOWS.keys():
            current_cron = current.get(workflow_name, "Unknown")
            recommended_cron = recommended.get(workflow_name, "Unknown")
            
            needs_update = current_cron != recommended_cron
            status = "⚠️  UPDATE NEEDED" if needs_update else "✓ OK"
            
            print(f"{workflow_name}:")
            print(f"  Current:     {current_cron}")
            print(f"  Recommended: {recommended_cron}")
            print(f"  Status:      {status}\n")
        
        print("="*70 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Dynamically orchestrate workflow schedules based on API usage'
    )
    parser.add_argument(
        '--mode',
        choices=['aggressive', 'normal', 'conservative'],
        help='Force a specific scheduling mode'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current schedules and recommendations without updating'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        repo_root=args.repo_root,
        dry_run=args.dry_run
    )
    
    if args.status:
        # Just show status
        orchestrator.print_status()
    else:
        # Update workflows
        results = orchestrator.update_all_workflows(mode=args.mode)
        
        # Exit with error if any updates failed
        if not all(results.values()):
            sys.exit(1)


if __name__ == '__main__':
    main()
