#!/usr/bin/env python3
"""
AGENTS.md Configuration Parser

Parses and validates the AGENTS.md configuration file for Chained agents.
Inspired by GitHub Agent HQ's AGENTS.md pattern.

Usage:
    python parse_agent_config.py --agent secure-specialist
    python parse_agent_config.py --validate
    python parse_agent_config.py --list

Author: @agents-tech-lead
Mission: idea:41 - GitHub Innovation Integration
"""

import yaml
import json
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, Any, Optional


class AgentConfigParser:
    """Parser for AGENTS.md configuration"""
    
    def __init__(self, config_path: str = "AGENTS.md"):
        self.config_path = Path(config_path)
        self.config = None
        self.global_defaults = {}
        self.agent_overrides = {}
        
    def load(self) -> bool:
        """Load and parse AGENTS.md file"""
        if not self.config_path.exists():
            print(f"Error: Configuration file not found: {self.config_path}")
            return False
        
        try:
            content = self.config_path.read_text()
            self._parse_markdown_config(content)
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def _parse_markdown_config(self, content: str):
        """Parse YAML blocks from markdown content"""
        # Extract YAML blocks from markdown
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', content, re.DOTALL)
        
        if not yaml_blocks:
            raise ValueError("No YAML blocks found in AGENTS.md")
        
        # Parse global defaults (first YAML block)
        self.global_defaults = yaml.safe_load(yaml_blocks[0])
        if 'global_defaults' in self.global_defaults:
            self.global_defaults = self.global_defaults['global_defaults']
        
        # Parse agent overrides (remaining YAML blocks)
        for block in yaml_blocks[1:]:
            try:
                override_data = yaml.safe_load(block)
                if 'agent_overrides' in override_data:
                    self.agent_overrides.update(override_data['agent_overrides'])
            except yaml.YAMLError:
                continue  # Skip invalid YAML blocks
    
    def get_agent_settings(self, agent_name: str) -> Dict[str, Any]:
        """
        Get merged settings for a specific agent
        
        Args:
            agent_name: Name of the agent (with or without @ prefix)
        
        Returns:
            Dictionary of merged settings (defaults + overrides)
        """
        # Remove @ prefix if present
        agent_name = agent_name.lstrip('@')
        
        # Start with global defaults
        settings = self.global_defaults.copy()
        
        # Apply agent-specific overrides
        if agent_name in self.agent_overrides:
            settings.update(self.agent_overrides[agent_name])
        
        return settings
    
    def list_agents(self) -> list:
        """Get list of all configured agents"""
        return sorted(self.agent_overrides.keys())
    
    def validate(self) -> tuple[bool, list]:
        """
        Validate configuration
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required global defaults
        required_defaults = [
            'logging_style',
            'commit_message_format',
            'test_framework'
        ]
        
        for field in required_defaults:
            if field not in self.global_defaults:
                errors.append(f"Missing required global default: {field}")
        
        # Validate each agent configuration
        for agent_name, overrides in self.agent_overrides.items():
            # Check agent name format
            if not re.match(r'^[a-z0-9-]+$', agent_name):
                errors.append(f"Invalid agent name format: {agent_name}")
            
            # Validate specialization_tags if present
            if 'specialization_tags' in overrides:
                if not isinstance(overrides['specialization_tags'], list):
                    errors.append(f"{agent_name}: specialization_tags must be a list")
            
            # Validate numeric fields
            numeric_fields = {
                'max_file_changes': (1, 100),
                'max_retries': (0, 10),
                'task_timeout_minutes': (1, 1440)
            }
            
            for field, (min_val, max_val) in numeric_fields.items():
                if field in overrides:
                    value = overrides[field]
                    if not isinstance(value, (int, float)):
                        errors.append(f"{agent_name}: {field} must be numeric")
                    elif value < min_val or value > max_val:
                        errors.append(f"{agent_name}: {field} must be between {min_val} and {max_val}")
        
        return len(errors) == 0, errors
    
    def get_agents_by_tag(self, tag: str) -> list:
        """Get list of agents with specific specialization tag"""
        matching_agents = []
        
        for agent_name, overrides in self.agent_overrides.items():
            if 'specialization_tags' in overrides:
                if tag in overrides['specialization_tags']:
                    matching_agents.append(agent_name)
        
        return matching_agents
    
    def export_json(self, output_path: Optional[str] = None) -> str:
        """Export configuration as JSON"""
        config_json = {
            'global_defaults': self.global_defaults,
            'agent_overrides': self.agent_overrides
        }
        
        json_str = json.dumps(config_json, indent=2)
        
        if output_path:
            Path(output_path).write_text(json_str)
        
        return json_str


def main():
    """Command-line interface for agent configuration parser"""
    parser = argparse.ArgumentParser(
        description='Parse and validate AGENTS.md configuration'
    )
    parser.add_argument(
        '--agent',
        help='Get settings for specific agent'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration file'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all configured agents'
    )
    parser.add_argument(
        '--tag',
        help='List agents with specific specialization tag'
    )
    parser.add_argument(
        '--export-json',
        help='Export configuration as JSON to specified file'
    )
    parser.add_argument(
        '--config',
        default='AGENTS.md',
        help='Path to AGENTS.md file (default: AGENTS.md)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_parser = AgentConfigParser(args.config)
    if not config_parser.load():
        sys.exit(1)
    
    # Execute requested operation
    if args.validate:
        is_valid, errors = config_parser.validate()
        if is_valid:
            print("✅ Configuration is valid")
            sys.exit(0)
        else:
            print("❌ Configuration has errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    
    elif args.list:
        agents = config_parser.list_agents()
        print(f"Configured agents ({len(agents)}):")
        for agent in agents:
            print(f"  - @{agent}")
    
    elif args.agent:
        settings = config_parser.get_agent_settings(args.agent)
        print(f"Settings for @{args.agent.lstrip('@')}:")
        print(json.dumps(settings, indent=2))
    
    elif args.tag:
        agents = config_parser.get_agents_by_tag(args.tag)
        print(f"Agents with tag '{args.tag}' ({len(agents)}):")
        for agent in agents:
            print(f"  - @{agent}")
    
    elif args.export_json:
        config_parser.export_json(args.export_json)
        print(f"✅ Configuration exported to {args.export_json}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
