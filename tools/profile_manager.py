#!/usr/bin/env python3
"""
Agent Profile Manager

Elegant management of agent profiles and archives.
Handles status updates and archival with grace and clarity.

Beauty is in the details - this module makes profile management
a pleasure to read and maintain.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional


class ProfileManager:
    """
    Manages agent profiles with elegance.
    
    Handles reading, updating, and archiving agent profiles
    in a way that reads like poetry.
    """
    
    PROFILES_DIR = Path(".github/agent-system/profiles")
    ARCHIVE_DIR = Path(".github/agent-system/archive")
    
    def __init__(self):
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self) -> None:
        """Create necessary directories if they don't exist"""
        self.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    def update_status(
        self,
        agent_id: str,
        new_status: str,
        score: float
    ) -> bool:
        """
        Update an agent's profile status.
        
        Returns True if successful, False if profile not found.
        """
        profile_path = self.PROFILES_DIR / f"{agent_id}.md"
        
        if not profile_path.exists():
            return False
        
        content = profile_path.read_text()
        updated_content = self._replace_status_line(content, new_status, score)
        profile_path.write_text(updated_content)
        
        return True
    
    def _replace_status_line(
        self,
        content: str,
        status: str,
        score: float
    ) -> str:
        """Replace the status line in profile content"""
        old_status = '**Status**: 🟢 Active'
        
        if status == 'eliminated':
            new_status = f"**Status**: ❌ Eliminated (Score: {score:.2%})"
        elif status == 'hall_of_fame':
            new_status = f"**Status**: 🏆 Hall of Fame (Score: {score:.2%})"
        else:
            new_status = old_status
        
        return content.replace(old_status, new_status)
    
    def archive_profile(self, agent_id: str, agent_name: str) -> bool:
        """
        Archive an eliminated agent's profile.
        
        Returns True if successful, False if profile not found.
        """
        source = self.PROFILES_DIR / f"{agent_id}.md"
        destination = self.ARCHIVE_DIR / f"{agent_id}.md"
        
        if not source.exists():
            return False
        
        shutil.move(str(source), str(destination))
        print(f"📦 Archived profile for {agent_name}")
        
        return True


def update_agent_profiles(evaluation_results: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Update profiles for all evaluated agents.
    
    Beautiful simplicity - one function to handle all profile updates.
    """
    manager = ProfileManager()
    
    # Update eliminated agents
    for agent in evaluation_results.get('eliminated', []):
        manager.update_status(
            agent['id'],
            'eliminated',
            agent['score']
        )
    
    # Update promoted agents
    for agent in evaluation_results.get('promoted', []):
        manager.update_status(
            agent['id'],
            'hall_of_fame',
            agent['score']
        )
    
    print("✅ Agent profiles updated")


def archive_eliminated_agents(evaluation_results: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Archive profiles and note definitions for eliminated agents.
    
    Clean and purposeful - archives with care and clarity.
    """
    manager = ProfileManager()
    registry_path = Path(".github/agent-system/registry.json")
    
    # Load registry for specialization lookup
    with open(registry_path, 'r') as file:
        registry = json.load(file)
    
    for agent in evaluation_results.get('eliminated', []):
        agent_id = agent['id']
        agent_name = agent['name']
        
        # Archive the profile
        manager.archive_profile(agent_id, agent_name)
        
        # Note about agent definition (kept for future spawns)
        specialization = _find_agent_specialization(agent_id, registry)
        if specialization:
            definition_path = Path(f".github/agents/{specialization}.md")
            if definition_path.exists():
                print(f"  ℹ️  Agent definition {specialization}.md remains for future spawns")


def _find_agent_specialization(
    agent_id: str,
    registry: Dict[str, Any]
) -> Optional[str]:
    """Find an agent's specialization in the registry"""
    # Check active agents (though they shouldn't be there after elimination)
    for agent in registry.get('agents', []):
        if agent.get('id') == agent_id:
            return agent.get('specialization')
    
    # Historical data might be elsewhere, but we return None if not found
    return None


if __name__ == '__main__':
    # Load evaluation results and process profiles
    import sys
    
    results_path = Path('/tmp/evaluation_results.json')
    
    if not results_path.exists():
        print("No evaluation results found", file=sys.stderr)
        sys.exit(1)
    
    with open(results_path, 'r') as file:
        results = json.load(file)
    
    update_agent_profiles(results)
    archive_eliminated_agents(results)
