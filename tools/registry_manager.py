#!/usr/bin/env python3
"""
Registry Manager - Distributed Agent Registry System

This module provides a unified interface for managing agent registry data,
supporting both legacy single-file format and new distributed file format.

Architecture:
- Abstracts registry operations behind a clean API
- Supports atomic updates to individual agents
- Handles migration between formats transparently
- Provides thread-safe operations
- Maintains backward compatibility

Usage:
    from registry_manager import RegistryManager
    
    registry = RegistryManager()
    agent = registry.get_agent("agent-123")
    registry.update_agent(agent_data)
    all_agents = registry.list_agents()
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import shutil
import fcntl
from contextlib import contextmanager


@dataclass
class RegistryConfig:
    """Registry configuration settings"""
    spawn_interval_hours: int = 3
    max_active_agents: int = 50
    elimination_threshold: float = 0.3
    promotion_threshold: float = 0.85
    metrics_weight: Dict[str, float] = field(default_factory=lambda: {
        "code_quality": 0.3,
        "issue_resolution": 0.2,
        "pr_success": 0.2,
        "peer_review": 0.15,
        "creativity": 0.15
    })
    spawn_mode: str = "mixed"
    new_agent_probability: float = 0.5
    protected_specializations: List[str] = field(default_factory=lambda: ["troubleshoot-expert"])
    strict_pr_attribution: bool = True


class RegistryManager:
    """
    Unified registry manager that supports both single-file and distributed formats.
    
    File Structure (Distributed Mode):
    .github/agent-system/
    ├── agents/
    │   ├── agent-123.json
    │   ├── agent-456.json
    │   └── ...
    ├── config.json
    ├── hall_of_fame.json
    ├── metadata.json
    └── registry.json (legacy, optional)
    """
    
    def __init__(self, base_path: str = ".github/agent-system"):
        """
        Initialize registry manager.
        
        Args:
            base_path: Base directory for agent system files
        """
        self.base_path = Path(base_path)
        self.agents_dir = self.base_path / "agents"
        self.config_file = self.base_path / "config.json"
        self.hall_of_fame_file = self.base_path / "hall_of_fame.json"
        self.metadata_file = self.base_path / "metadata.json"
        self.metadata_dir = self.base_path / "metadata"
        self.legacy_registry_file = self.base_path / "registry.json"
        
        # Create distributed directory structure if needed
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Detect which mode we're in
        self._mode = self._detect_mode()
        self._metadata_mode = self._detect_metadata_mode()
        
    def _detect_mode(self) -> str:
        """
        Detect whether we're using distributed or legacy mode.
        
        Returns:
            "distributed" if distributed files exist, "legacy" otherwise
        """
        # If distributed files exist, use distributed mode
        if self.config_file.exists() or len(list(self.agents_dir.glob("*.json"))) > 0:
            return "distributed"
        # Otherwise use legacy mode
        return "legacy"
    
    def _detect_metadata_mode(self) -> str:
        """
        Detect whether we're using distributed metadata or single file.
        
        Returns:
            "distributed" if metadata directory has files, "single_file" otherwise
        """
        # If metadata directory has .txt files, use distributed mode
        if self.metadata_dir.exists() and len(list(self.metadata_dir.glob("*.txt"))) > 0:
            return "distributed"
        # Otherwise use single file mode
        return "single_file"
    
    def _read_legacy_registry(self) -> Dict[str, Any]:
        """Read the legacy single-file registry"""
        if not self.legacy_registry_file.exists():
            return self._empty_registry()
        
        try:
            with open(self.legacy_registry_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read legacy registry: {e}")
            return self._empty_registry()
    
    def _empty_registry(self) -> Dict[str, Any]:
        """Return an empty registry structure"""
        return {
            "version": "2.0.0",
            "agents": [],
            "hall_of_fame": [],
            "system_lead": None,
            "config": {},
            "last_spawn": None,
            "last_evaluation": None,
            "specializations_note": "Specializations are dynamically loaded from .github/agents/ directory"
        }
    
    @contextmanager
    def _lock_file(self, filepath: Path, max_retries: int = 10, base_delay: float = 0.1):
        """
        Context manager for file locking with retry and exponential backoff.
        
        Args:
            filepath: Path to the file being locked
            max_retries: Maximum number of lock acquisition attempts
            base_delay: Initial delay between retries (doubles each time)
        
        Yields:
            None when lock is acquired
            
        Raises:
            IOError: If lock cannot be acquired after max_retries
        """
        lock_file = filepath.parent / f".{filepath.name}.lock"
        lock_file.touch(exist_ok=True)
        
        retry_delay = base_delay
        last_error = None
        
        for attempt in range(max_retries):
            try:
                with open(lock_file, 'w') as f:
                    # Try non-blocking lock first
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    try:
                        yield
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return  # Success, exit function
            except IOError as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff
                    import time
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 5.0)  # Cap at 5 seconds
        
        # If we get here, all retries failed
        raise IOError(f"Failed to acquire lock for {filepath} after {max_retries} attempts: {last_error}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent data by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent data dict or None if not found
        """
        if self._mode == "distributed":
            agent_file = self.agents_dir / f"{agent_id}.json"
            if not agent_file.exists():
                return None
            
            try:
                with open(agent_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        else:
            # Legacy mode
            registry = self._read_legacy_registry()
            for agent in registry.get("agents", []):
                if agent.get("id") == agent_id:
                    return agent
            return None
    
    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all agents, optionally filtered by status.
        
        Args:
            status: Optional status filter ("active", "inactive", etc.)
            
        Returns:
            List of agent data dictionaries
        """
        if self._mode == "distributed":
            agents = []
            for agent_file in sorted(self.agents_dir.glob("*.json")):
                try:
                    with open(agent_file, 'r') as f:
                        agent = json.load(f)
                        if status is None or agent.get("status") == status:
                            agents.append(agent)
                except (json.JSONDecodeError, IOError):
                    continue
            return agents
        else:
            # Legacy mode
            registry = self._read_legacy_registry()
            agents = registry.get("agents", [])
            if status:
                agents = [a for a in agents if a.get("status") == status]
            return agents
    
    def update_agent(self, agent_data: Dict[str, Any]) -> bool:
        """
        Update or create an agent record.
        
        Args:
            agent_data: Complete agent data dictionary (must include 'id')
            
        Returns:
            True if successful, False otherwise
        """
        agent_id = agent_data.get("id")
        if not agent_id:
            raise ValueError("Agent data must include 'id' field")
        
        if self._mode == "distributed":
            agent_file = self.agents_dir / f"{agent_id}.json"
            try:
                with self._lock_file(agent_file):
                    with open(agent_file, 'w') as f:
                        json.dump(agent_data, f, indent=2)
                return True
            except IOError as e:
                print(f"Error updating agent {agent_id}: {e}")
                return False
        else:
            # Legacy mode - update registry.json
            try:
                with self._lock_file(self.legacy_registry_file):
                    registry = self._read_legacy_registry()
                    
                    # Find and update existing agent, or append new one
                    found = False
                    for i, agent in enumerate(registry["agents"]):
                        if agent.get("id") == agent_id:
                            registry["agents"][i] = agent_data
                            found = True
                            break
                    
                    if not found:
                        registry["agents"].append(agent_data)
                    
                    with open(self.legacy_registry_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                return True
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error updating agent {agent_id} in legacy mode: {e}")
                return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent record.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if successful, False otherwise
        """
        if self._mode == "distributed":
            agent_file = self.agents_dir / f"{agent_id}.json"
            if agent_file.exists():
                try:
                    agent_file.unlink()
                    return True
                except OSError:
                    return False
            return False
        else:
            # Legacy mode
            try:
                with self._lock_file(self.legacy_registry_file):
                    registry = self._read_legacy_registry()
                    original_count = len(registry["agents"])
                    registry["agents"] = [a for a in registry["agents"] if a.get("id") != agent_id]
                    
                    if len(registry["agents"]) < original_count:
                        with open(self.legacy_registry_file, 'w') as f:
                            json.dump(registry, f, indent=2)
                        return True
                return False
            except (IOError, json.JSONDecodeError):
                return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get registry configuration"""
        if self._mode == "distributed":
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            # Return default config
            return RegistryConfig().__dict__
        else:
            registry = self._read_legacy_registry()
            return registry.get("config", RegistryConfig().__dict__)
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """Update registry configuration"""
        if self._mode == "distributed":
            try:
                with self._lock_file(self.config_file):
                    with open(self.config_file, 'w') as f:
                        json.dump(config_data, f, indent=2)
                return True
            except IOError:
                return False
        else:
            try:
                with self._lock_file(self.legacy_registry_file):
                    registry = self._read_legacy_registry()
                    registry["config"] = config_data
                    with open(self.legacy_registry_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                return True
            except (IOError, json.JSONDecodeError):
                return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get registry metadata (version, last_spawn, last_evaluation, etc.)"""
        # If metadata is in distributed mode, read from individual files
        # This works regardless of whether agents are in distributed or legacy mode
        if self._metadata_mode == "distributed":
            # Read from individual files in metadata directory
            metadata = {
                "version": "2.0.0",
                "last_spawn": None,
                "last_evaluation": None,
                "system_lead": None,
                "specializations_note": "Specializations are dynamically loaded from .github/agents/ directory"
            }
            
            # Read each field from individual files
            for field in ["version", "last_spawn", "last_evaluation", "system_lead", "specializations_note"]:
                field_file = self.metadata_dir / f"{field}.txt"
                if field_file.exists():
                    try:
                        with open(field_file, 'r') as f:
                            value = f.read().strip()
                            # Handle null/None values
                            if value and value.lower() != "null" and value.lower() != "none":
                                metadata[field] = value
                    except IOError:
                        pass
            
            return metadata
        elif self._mode == "distributed":
            # Read from single metadata.json file
            if self.metadata_file.exists():
                try:
                    with open(self.metadata_file, 'r') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            return {
                "version": "2.0.0",
                "last_spawn": None,
                "last_evaluation": None,
                "system_lead": None,
                "specializations_note": "Specializations are dynamically loaded from .github/agents/ directory"
            }
        else:
            # Legacy mode - read from registry.json
            registry = self._read_legacy_registry()
            return {
                "version": registry.get("version", "2.0.0"),
                "last_spawn": registry.get("last_spawn"),
                "last_evaluation": registry.get("last_evaluation"),
                "system_lead": registry.get("system_lead"),
                "specializations_note": registry.get("specializations_note", "")
            }
    
    def update_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Update registry metadata"""
        if self._mode == "distributed":
            if self._metadata_mode == "distributed":
                # Write to individual files in metadata directory
                try:
                    for field, value in metadata.items():
                        field_file = self.metadata_dir / f"{field}.txt"
                        with open(field_file, 'w') as f:
                            # Write value as string, handling None
                            if value is None:
                                f.write("null")
                            else:
                                f.write(str(value))
                    return True
                except IOError:
                    return False
            else:
                # Write to single metadata.json file
                try:
                    with self._lock_file(self.metadata_file):
                        with open(self.metadata_file, 'w') as f:
                            json.dump(metadata, f, indent=2)
                    return True
                except IOError:
                    return False
        else:
            try:
                with self._lock_file(self.legacy_registry_file):
                    registry = self._read_legacy_registry()
                    registry.update(metadata)
                    with open(self.legacy_registry_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                return True
            except (IOError, json.JSONDecodeError):
                return False
    
    def update_metadata_field(self, field: str, value: Any) -> bool:
        """
        Update a single metadata field atomically.
        This is the preferred method for concurrent updates.
        
        Args:
            field: Field name (e.g., "last_spawn", "last_evaluation")
            value: Field value (will be converted to string for distributed mode)
            
        Returns:
            True if successful, False otherwise
        """
        # If metadata is in distributed mode, update the individual file directly
        # This works regardless of whether agents are in distributed or legacy mode
        if self._metadata_mode == "distributed":
            # Atomic update of individual field file
            field_file = self.metadata_dir / f"{field}.txt"
            try:
                with open(field_file, 'w') as f:
                    if value is None:
                        f.write("null")
                    else:
                        f.write(str(value))
                return True
            except IOError:
                return False
        else:
            # Fall back to full metadata update
            metadata = self.get_metadata()
            metadata[field] = value
            return self.update_metadata(metadata)
    
    def get_hall_of_fame(self) -> List[Dict[str, Any]]:
        """Get hall of fame entries"""
        if self._mode == "distributed":
            if self.hall_of_fame_file.exists():
                try:
                    with open(self.hall_of_fame_file, 'r') as f:
                        data = json.load(f)
                        return data if isinstance(data, list) else []
                except (json.JSONDecodeError, IOError):
                    pass
            return []
        else:
            registry = self._read_legacy_registry()
            return registry.get("hall_of_fame", [])
    
    def update_hall_of_fame(self, hall_of_fame: List[Dict[str, Any]]) -> bool:
        """Update hall of fame entries"""
        if self._mode == "distributed":
            try:
                with self._lock_file(self.hall_of_fame_file):
                    with open(self.hall_of_fame_file, 'w') as f:
                        json.dump(hall_of_fame, f, indent=2)
                return True
            except IOError:
                return False
        else:
            try:
                with self._lock_file(self.legacy_registry_file):
                    registry = self._read_legacy_registry()
                    registry["hall_of_fame"] = hall_of_fame
                    with open(self.legacy_registry_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                return True
            except (IOError, json.JSONDecodeError):
                return False
    
    def migrate_to_distributed(self) -> bool:
        """
        Migrate from legacy single-file format to distributed format.
        
        Returns:
            True if successful, False otherwise
        """
        if self._mode == "distributed":
            print("Already in distributed mode")
            return True
        
        print("Migrating from legacy to distributed format...")
        
        try:
            # Read legacy registry
            registry = self._read_legacy_registry()
            
            # Create backup
            backup_file = self.legacy_registry_file.with_suffix('.json.backup')
            shutil.copy2(self.legacy_registry_file, backup_file)
            print(f"Created backup: {backup_file}")
            
            # Write individual agent files
            for agent in registry.get("agents", []):
                agent_id = agent.get("id")
                if agent_id:
                    agent_file = self.agents_dir / f"{agent_id}.json"
                    with open(agent_file, 'w') as f:
                        json.dump(agent, f, indent=2)
                    print(f"Created {agent_file.name}")
            
            # Write config file
            config = registry.get("config", {})
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Created {self.config_file.name}")
            
            # Write hall of fame
            hall_of_fame = registry.get("hall_of_fame", [])
            with open(self.hall_of_fame_file, 'w') as f:
                json.dump(hall_of_fame, f, indent=2)
            print(f"Created {self.hall_of_fame_file.name}")
            
            # Write metadata
            metadata = {
                "version": registry.get("version", "2.0.0"),
                "last_spawn": registry.get("last_spawn"),
                "last_evaluation": registry.get("last_evaluation"),
                "system_lead": registry.get("system_lead"),
                "specializations_note": registry.get("specializations_note", "")
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"Created {self.metadata_file.name}")
            
            # Update mode
            self._mode = "distributed"
            
            print("Migration completed successfully!")
            print(f"Backup of original registry: {backup_file}")
            print(f"You can safely delete {self.legacy_registry_file} after verification")
            
            return True
            
        except Exception as e:
            print(f"Migration failed: {e}")
            return False
    
    def migrate_metadata_to_distributed(self) -> bool:
        """
        Migrate metadata from single file to distributed format.
        
        Returns:
            True if successful, False otherwise
        """
        if self._metadata_mode == "distributed":
            print("Metadata already in distributed mode")
            return True
        
        print("Migrating metadata from single file to distributed format...")
        
        try:
            # Read current metadata
            metadata = self.get_metadata()
            
            # Create backup of metadata.json if it exists
            if self.metadata_file.exists():
                backup_file = self.metadata_file.with_suffix('.json.backup')
                shutil.copy2(self.metadata_file, backup_file)
                print(f"Created backup: {backup_file}")
            
            # Create metadata directory
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            
            # Write each field to individual file
            for field, value in metadata.items():
                field_file = self.metadata_dir / f"{field}.txt"
                with open(field_file, 'w') as f:
                    if value is None:
                        f.write("null")
                    else:
                        f.write(str(value))
                print(f"Created {field_file.name}")
            
            # Update metadata mode
            self._metadata_mode = "distributed"
            
            print("Metadata migration completed successfully!")
            print(f"You can safely delete {self.metadata_file} after verification")
            
            return True
            
        except Exception as e:
            print(f"Metadata migration failed: {e}")
            return False
    
    def get_mode(self) -> str:
        """Get current registry mode"""
        return self._mode


def main():
    """CLI interface for registry manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Registry Manager")
    parser.add_argument("command", choices=["migrate", "migrate-metadata", "list", "get", "mode"],
                       help="Command to execute")
    parser.add_argument("--agent-id", help="Agent ID (for 'get' command)")
    parser.add_argument("--status", help="Filter agents by status")
    
    args = parser.parse_args()
    
    registry = RegistryManager()
    
    if args.command == "migrate":
        success = registry.migrate_to_distributed()
        sys.exit(0 if success else 1)
    
    elif args.command == "migrate-metadata":
        success = registry.migrate_metadata_to_distributed()
        sys.exit(0 if success else 1)
    
    elif args.command == "list":
        agents = registry.list_agents(status=args.status)
        print(json.dumps(agents, indent=2))
    
    elif args.command == "get":
        if not args.agent_id:
            print("Error: --agent-id required for 'get' command")
            sys.exit(1)
        agent = registry.get_agent(args.agent_id)
        if agent:
            print(json.dumps(agent, indent=2))
        else:
            print(f"Agent {args.agent_id} not found")
            sys.exit(1)
    
    elif args.command == "mode":
        print(f"Current mode: {registry.get_mode()}")
        print(f"Metadata mode: {registry._metadata_mode}")


if __name__ == "__main__":
    import sys
    main()
