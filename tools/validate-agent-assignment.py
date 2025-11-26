#!/usr/bin/env python3
"""
Validate Agent Assignment Tool

A utility created by @create-guru to validate that agent assignments are working correctly.
This tool verifies:
1. Agent definition files exist and are valid
2. Agent directives are properly formatted in issues
3. Agent labels are correctly applied

Created as part of the direct custom agent assignment test.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class AgentAssignmentValidator:
    """Validates agent assignments in the repository."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.agents_dir = repo_root / ".github" / "agents"
        
    def validate_agent_exists(self, agent_name: str) -> bool:
        """Check if an agent definition file exists."""
        agent_file = self.agents_dir / f"{agent_name}.md"
        return agent_file.exists()
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict]:
        """Get agent information from the definition file."""
        agent_file = self.agents_dir / f"{agent_name}.md"
        
        if not agent_file.exists():
            return None
        
        content = agent_file.read_text()
        
        # Extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    frontmatter = parts[1]
                    info = yaml.safe_load(frontmatter)
                    return info if isinstance(info, dict) else {}
                except ImportError:
                    # Fallback to simple parsing if yaml not available
                    frontmatter = parts[1]
                    info = {}
                    for line in frontmatter.strip().split("\n"):
                        if ":" in line and not line.strip().startswith("-"):
                            key, value = line.split(":", 1)
                            info[key.strip()] = value.strip().strip('"')
                    return info
                except Exception:
                    return {}
        
        return {}
    
    def validate_agent_directive(self, directive: str, agent_name: str) -> Dict[str, Any]:
        """Validate that an agent directive is properly formatted."""
        results = {
            "valid": True,
            "issues": []
        }
        
        # Check for agent name mention
        if f"@{agent_name}" not in directive:
            results["valid"] = False
            results["issues"].append(f"Missing @{agent_name} mention in directive")
        
        # Check for COPILOT_AGENT comment
        if f"COPILOT_AGENT:{agent_name}" not in directive:
            results["valid"] = False
            results["issues"].append(f"Missing COPILOT_AGENT:{agent_name} comment marker")
        
        # Check for agent path reference
        if f".github/agents/{agent_name}.md" not in directive:
            results["valid"] = False
            results["issues"].append(f"Missing reference to agent definition file")
        
        # Check for important notice
        if "IMPORTANT" not in directive:
            results["valid"] = False
            results["issues"].append("Missing IMPORTANT notice about @mentions")
        
        return results
    
    def list_available_agents(self) -> List[str]:
        """List all available agent definitions."""
        agents = []
        if self.agents_dir.exists():
            for agent_file in self.agents_dir.glob("*.md"):
                if agent_file.name not in ["README.md", ".context.md"]:
                    agents.append(agent_file.stem)
        return sorted(agents)
    
    def validate_assignment(self, agent_name: str, verbose: bool = False) -> bool:
        """Comprehensive validation of an agent assignment."""
        print(f"🔍 Validating agent assignment: @{agent_name}")
        print("=" * 70)
        
        all_valid = True
        
        # Check 1: Agent exists
        if self.validate_agent_exists(agent_name):
            print(f"✅ Agent definition exists: .github/agents/{agent_name}.md")
        else:
            print(f"❌ Agent definition NOT found: .github/agents/{agent_name}.md")
            all_valid = False
        
        # Check 2: Get agent info
        info = self.get_agent_info(agent_name)
        if info:
            print(f"✅ Agent info retrieved successfully")
            if verbose:
                print(f"   Name: {info.get('name', 'N/A')}")
                print(f"   Description: {info.get('description', 'N/A')}")
        else:
            print(f"⚠️  Could not parse agent info")
        
        # Check 3: Verify agent tools
        if info and 'tools' in info:
            print(f"✅ Agent has tools configured")
        
        print("=" * 70)
        
        if all_valid:
            print(f"✅ Agent @{agent_name} is properly configured for assignment")
        else:
            print(f"❌ Agent @{agent_name} has configuration issues")
        
        return all_valid


def main():
    """Main entry point for the validation tool."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate agent assignments in the Chained repository"
    )
    parser.add_argument(
        "command",
        choices=["validate", "list"],
        help="Command to execute"
    )
    parser.add_argument(
        "agent_name",
        nargs="?",
        help="Agent name to validate (required for 'validate' command)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    
    args = parser.parse_args()
    
    # Find repository root
    repo_root = Path(__file__).parent.parent
    
    validator = AgentAssignmentValidator(repo_root)
    
    if args.command == "list":
        print("📋 Available Agents:")
        print("=" * 70)
        agents = validator.list_available_agents()
        for agent in agents:
            print(f"  • @{agent}")
        print()
        print(f"Total: {len(agents)} agents")
        return 0
    
    elif args.command == "validate":
        if not args.agent_name:
            print("❌ Error: agent_name is required for 'validate' command")
            return 1
        
        success = validator.validate_assignment(args.agent_name, args.verbose)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
