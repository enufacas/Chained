#!/usr/bin/env python3
"""
Atomic Registry Update Tool

Safely updates the agent registry.json file with automatic conflict resolution
and retry logic to handle concurrent modifications from multiple workflows.

This tool uses git-based locking and automatic conflict resolution to ensure
that concurrent registry updates don't result in merge conflicts.
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import argparse


class RegistryUpdateError(Exception):
    """Base exception for registry update errors"""
    pass


class AtomicRegistryUpdater:
    """
    Handles atomic updates to the agent registry with conflict resolution.
    
    Uses a pull-modify-push approach with retry logic to handle concurrent
    modifications from multiple workflows.
    """
    
    REGISTRY_FILE = Path(".github/agent-system/registry.json")
    MAX_RETRIES = 5
    BASE_RETRY_DELAY = 2  # seconds
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.repo_root = self._find_repo_root()
        self.registry_path = self.repo_root / self.REGISTRY_FILE
        
    def _find_repo_root(self) -> Path:
        """Find the git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise RegistryUpdateError("Not in a git repository")
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[AtomicRegistry] {message}", file=sys.stderr)
    
    def _run_git_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command and return the result"""
        full_cmd = ["git"] + cmd
        self._log(f"Running: {' '.join(full_cmd)}")
        result = subprocess.run(
            full_cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False
        )
        
        if check and result.returncode != 0:
            raise RegistryUpdateError(
                f"Git command failed: {' '.join(full_cmd)}\n"
                f"Error: {result.stderr}"
            )
        
        return result
    
    def _pull_latest(self) -> bool:
        """
        Pull the latest changes from origin.
        Returns True if successful, False if there are local changes that need to be stashed.
        """
        self._log("Pulling latest changes from origin")
        
        # Check if we're in a clean state
        status_result = self._run_git_command(["status", "--porcelain"])
        if status_result.stdout.strip():
            self._log("Working directory has changes, will stash")
            return False
        
        # Pull latest changes
        pull_result = self._run_git_command(["pull", "origin", "main"], check=False)
        
        if pull_result.returncode != 0:
            self._log(f"Pull failed: {pull_result.stderr}")
            return False
        
        return True
    
    def _merge_agents_arrays(self, base: List[Dict], incoming: List[Dict]) -> List[Dict]:
        """
        Merge two agent arrays, handling concurrent additions.
        
        Strategy:
        - Keep all unique agents by ID
        - For duplicates, prefer the one with more recent spawned_at timestamp
        - Preserve order by spawned_at timestamp
        """
        agents_by_id = {}
        
        # Add base agents
        for agent in base:
            agent_id = agent.get('id')
            if agent_id:
                agents_by_id[agent_id] = agent
        
        # Add/update with incoming agents
        for agent in incoming:
            agent_id = agent.get('id')
            if not agent_id:
                continue
            
            if agent_id not in agents_by_id:
                # New agent, add it
                agents_by_id[agent_id] = agent
            else:
                # Duplicate - keep the one with more recent spawn time
                existing = agents_by_id[agent_id]
                existing_time = existing.get('spawned_at', '')
                incoming_time = agent.get('spawned_at', '')
                
                if incoming_time > existing_time:
                    agents_by_id[agent_id] = agent
        
        # Sort by spawned_at timestamp
        sorted_agents = sorted(
            agents_by_id.values(),
            key=lambda a: a.get('spawned_at', '1970-01-01T00:00:00Z')
        )
        
        return sorted_agents
    
    def _merge_registries(self, base: Dict, incoming: Dict) -> Dict:
        """
        Intelligently merge two registry states.
        
        For arrays (agents, hall_of_fame), we merge by ID.
        For simple fields, we take the most recent.
        """
        merged = base.copy()
        
        # Merge agents arrays intelligently
        if 'agents' in incoming:
            base_agents = base.get('agents', [])
            incoming_agents = incoming.get('agents', [])
            merged['agents'] = self._merge_agents_arrays(base_agents, incoming_agents)
        
        # Merge hall_of_fame arrays
        if 'hall_of_fame' in incoming:
            base_hof = base.get('hall_of_fame', [])
            incoming_hof = incoming.get('hall_of_fame', [])
            merged['hall_of_fame'] = self._merge_agents_arrays(base_hof, incoming_hof)
        
        # Take the most recent timestamp fields
        for field in ['last_spawn', 'last_evaluation']:
            base_val = base.get(field, '')
            incoming_val = incoming.get(field, '')
            if incoming_val and incoming_val > base_val:
                merged[field] = incoming_val
        
        # Take the latest system_lead if set
        if incoming.get('system_lead'):
            merged['system_lead'] = incoming['system_lead']
        
        # Config is typically static, but take incoming if exists
        if 'config' in incoming:
            merged['config'] = incoming['config']
        
        # Preserve version
        if 'version' in incoming:
            merged['version'] = incoming['version']
        
        if 'specializations_note' in incoming:
            merged['specializations_note'] = incoming['specializations_note']
        
        return merged
    
    def update_registry(
        self,
        update_func: Callable[[Dict], Dict],
        commit_message: str,
        max_retries: Optional[int] = None,
        skip_git_operations: bool = False
    ) -> bool:
        """
        Atomically update the registry with automatic conflict resolution.
        
        Args:
            update_func: Function that takes the current registry dict and returns the updated dict
            commit_message: Git commit message for the update
            max_retries: Maximum number of retry attempts (default: self.MAX_RETRIES)
            skip_git_operations: If True, only update the file without git operations (useful for workflows)
        
        Returns:
            True if successful, False otherwise
        """
        max_retries = max_retries or self.MAX_RETRIES
        
        # If skip_git_operations is True, just update the file directly
        if skip_git_operations:
            self._log("Skipping git operations - file-only update")
            
            # Read current registry state
            if not self.registry_path.exists():
                self._log("Registry file doesn't exist, creating new one")
                current_registry = self._create_initial_registry()
            else:
                with open(self.registry_path, 'r') as f:
                    current_registry = json.load(f)
            
            # Apply the update function
            updated_registry = update_func(current_registry.copy())
            
            # Write the updated registry
            with open(self.registry_path, 'w') as f:
                json.dump(updated_registry, f, indent=2)
                f.write('\n')  # Add trailing newline
            
            self._log("✅ Successfully updated registry file")
            return True
        
        for attempt in range(max_retries):
            try:
                self._log(f"Attempt {attempt + 1}/{max_retries}")
                
                # Step 1: Pull latest changes from origin
                if not self._pull_latest():
                    self._log("Cannot pull - working directory has changes")
                    time.sleep(self.BASE_RETRY_DELAY * (2 ** attempt))
                    continue
                
                # Step 2: Read current registry state
                if not self.registry_path.exists():
                    self._log("Registry file doesn't exist, creating new one")
                    current_registry = self._create_initial_registry()
                else:
                    with open(self.registry_path, 'r') as f:
                        current_registry = json.load(f)
                
                # Step 3: Apply the update function
                updated_registry = update_func(current_registry.copy())
                
                # Step 4: Write the updated registry
                with open(self.registry_path, 'w') as f:
                    json.dump(updated_registry, f, indent=2)
                    f.write('\n')  # Add trailing newline
                
                # Step 5: Check if there are changes to commit
                status_result = self._run_git_command(["status", "--porcelain", str(self.registry_path)])
                if not status_result.stdout.strip():
                    self._log("No changes detected in registry")
                    return True
                
                # Step 6: Commit the changes (but don't push yet)
                self._run_git_command(["add", str(self.registry_path)])
                self._run_git_command(["commit", "-m", commit_message])
                
                # Step 7: Try to push - this is where conflicts would occur
                push_result = self._run_git_command(["push", "origin", "HEAD"], check=False)
                
                if push_result.returncode == 0:
                    self._log("✅ Successfully pushed registry update")
                    return True
                
                # Step 8: Push failed - likely due to concurrent update
                self._log(f"Push failed (attempt {attempt + 1}): {push_result.stderr}")
                
                # Reset the commit to try again
                self._run_git_command(["reset", "HEAD~1"])
                
                # Exponential backoff before retry
                delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                self._log(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                
            except Exception as e:
                self._log(f"Error during attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(self.BASE_RETRY_DELAY * (2 ** attempt))
        
        raise RegistryUpdateError(f"Failed to update registry after {max_retries} attempts")
    
    def _create_initial_registry(self) -> Dict:
        """Create an initial empty registry structure"""
        return {
            "version": "2.0.0",
            "agents": [],
            "hall_of_fame": [],
            "system_lead": None,
            "config": {
                "spawn_interval_hours": 3,
                "max_active_agents": 50,
                "elimination_threshold": 0.3,
                "promotion_threshold": 0.85,
                "spawn_mode": "mixed",
                "new_agent_probability": 0.5,
                "metrics_weight": {
                    "code_quality": 0.3,
                    "issue_resolution": 0.2,
                    "pr_success": 0.2,
                    "peer_review": 0.15,
                    "creativity": 0.15
                },
                "protected_specializations": ["troubleshoot-expert"],
                "strict_pr_attribution": True
            },
            "last_spawn": None,
            "last_evaluation": None,
            "specializations_note": "Specializations are dynamically loaded from .github/agents/ directory"
        }
    
    def add_agent(self, agent_data: Dict, commit_message: Optional[str] = None) -> bool:
        """
        Add a new agent to the registry atomically.
        
        Args:
            agent_data: Agent data dictionary
            commit_message: Optional custom commit message
        
        Returns:
            True if successful
        """
        agent_id = agent_data.get('id', 'unknown')
        agent_name = agent_data.get('name', 'Unknown Agent')
        
        if not commit_message:
            commit_message = f"Add agent {agent_name} ({agent_id}) to registry"
        
        def update_func(registry: Dict) -> Dict:
            # Check if agent already exists
            existing_ids = {a.get('id') for a in registry.get('agents', [])}
            if agent_id in existing_ids:
                self._log(f"Agent {agent_id} already exists, skipping")
                return registry
            
            # Add the new agent
            registry['agents'].append(agent_data)
            registry['last_spawn'] = datetime.utcnow().isoformat() + 'Z'
            return registry
        
        return self.update_registry(update_func, commit_message)
    
    def remove_agents(self, agent_ids: List[str], reason: str, commit_message: Optional[str] = None) -> bool:
        """
        Remove agents from the registry atomically.
        
        Args:
            agent_ids: List of agent IDs to remove
            reason: Reason for removal
            commit_message: Optional custom commit message
        
        Returns:
            True if successful
        """
        if not commit_message:
            commit_message = f"Remove {len(agent_ids)} agent(s) from registry: {reason}"
        
        def update_func(registry: Dict) -> Dict:
            # Mark agents as deleted/eliminated
            for agent in registry.get('agents', []):
                if agent.get('id') in agent_ids:
                    agent['status'] = 'eliminated' if 'elimination' in reason.lower() else 'deleted'
                    agent['deleted_at'] = datetime.utcnow().isoformat() + 'Z'
                    agent['deletion_reason'] = reason
            
            # Remove from active agents list
            registry['agents'] = [
                a for a in registry.get('agents', [])
                if a.get('id') not in agent_ids
            ]
            
            return registry
        
        return self.update_registry(update_func, commit_message)
    
    def update_metrics(self, agent_id: str, metrics: Dict, commit_message: Optional[str] = None) -> bool:
        """
        Update an agent's metrics atomically.
        
        Args:
            agent_id: Agent ID to update
            metrics: New metrics dictionary
            commit_message: Optional custom commit message
        
        Returns:
            True if successful
        """
        if not commit_message:
            commit_message = f"Update metrics for agent {agent_id}"
        
        def update_func(registry: Dict) -> Dict:
            # Find and update the agent
            for agent in registry.get('agents', []):
                if agent.get('id') == agent_id:
                    agent['metrics'] = metrics
                    break
            
            # Also update in hall_of_fame if present
            for agent in registry.get('hall_of_fame', []):
                if agent.get('id') == agent_id:
                    agent['metrics'] = metrics
                    break
            
            registry['last_evaluation'] = datetime.utcnow().isoformat() + 'Z'
            return registry
        
        return self.update_registry(update_func, commit_message)


def main():
    """CLI interface for atomic registry updates"""
    parser = argparse.ArgumentParser(
        description='Atomically update the agent registry with conflict resolution'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add agent command
    add_parser = subparsers.add_parser('add', help='Add a new agent')
    add_parser.add_argument('agent_json', help='JSON string or file path containing agent data')
    add_parser.add_argument('--message', '-m', help='Commit message')
    
    # Remove agents command
    remove_parser = subparsers.add_parser('remove', help='Remove agents')
    remove_parser.add_argument('agent_ids', help='Comma-separated list of agent IDs')
    remove_parser.add_argument('--reason', '-r', required=True, help='Reason for removal')
    remove_parser.add_argument('--message', '-m', help='Commit message')
    
    # Update metrics command
    metrics_parser = subparsers.add_parser('update-metrics', help='Update agent metrics')
    metrics_parser.add_argument('agent_id', help='Agent ID')
    metrics_parser.add_argument('metrics_json', help='JSON string or file path containing metrics')
    metrics_parser.add_argument('--message', '-m', help='Commit message')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    updater = AtomicRegistryUpdater(verbose=args.verbose)
    
    try:
        if args.command == 'add':
            # Parse agent JSON
            agent_json = args.agent_json
            if os.path.exists(agent_json):
                with open(agent_json, 'r') as f:
                    agent_data = json.load(f)
            else:
                agent_data = json.loads(agent_json)
            
            success = updater.add_agent(agent_data, args.message)
            return 0 if success else 1
        
        elif args.command == 'remove':
            agent_ids = [id.strip() for id in args.agent_ids.split(',')]
            success = updater.remove_agents(agent_ids, args.reason, args.message)
            return 0 if success else 1
        
        elif args.command == 'update-metrics':
            # Parse metrics JSON
            metrics_json = args.metrics_json
            if os.path.exists(metrics_json):
                with open(metrics_json, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = json.loads(metrics_json)
            
            success = updater.update_metrics(args.agent_id, metrics, args.message)
            return 0 if success else 1
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
