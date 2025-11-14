#!/usr/bin/env python3
"""
Agent Registry Security Validator

A security-focused validation tool for the agent registry system.
Ensures data integrity, prevents corruption, and validates agent data.

Created by: @secure-ninja (Moxie Marlinspike)
Focus: Security, data integrity, and access control

Features:
- Schema validation for registry.json
- Data integrity checks
- Duplicate detection
- Metric bounds validation
- Timestamp validation
- Agent ID format validation
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

# Import validation utilities
try:
    from validation_utils import (
        ValidationError,
        validate_agent_name,
        validate_non_empty_string,
        validate_numeric_range,
        validate_percentage
    )
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, str(Path(__file__).parent))
    from validation_utils import (
        ValidationError,
        validate_agent_name,
        validate_non_empty_string,
        validate_numeric_range,
        validate_percentage
    )


class RegistryValidationError(Exception):
    """Custom exception for registry validation failures."""
    pass


class RegistryValidator:
    """
    Validates the agent registry for security and data integrity.
    
    Performs comprehensive checks to prevent:
    - Data corruption
    - Invalid agent entries
    - Metric manipulation
    - Duplicate agent IDs
    - Schema violations
    """
    
    def __init__(self, registry_path: Path):
        """
        Initialize the validator.
        
        Args:
            registry_path: Path to the registry.json file
        """
        self.registry_path = registry_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self) -> bool:
        """
        Perform complete validation of the registry.
        
        Returns:
            True if validation passes, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Step 1: Load and parse JSON
            registry_data = self._load_registry()
            
            # Step 2: Validate schema
            self._validate_schema(registry_data)
            
            # Step 3: Validate version
            self._validate_version(registry_data)
            
            # Step 4: Validate agents array
            self._validate_agents(registry_data.get('agents', []))
            
            # Step 5: Validate configuration
            self._validate_config(registry_data.get('config', {}))
            
            # Step 6: Validate timestamps
            self._validate_timestamps(registry_data)
            
            # Step 7: Check for duplicates
            self._check_duplicates(registry_data.get('agents', []))
            
            # Step 8: Validate hall of fame
            self._validate_hall_of_fame(registry_data.get('hall_of_fame', []))
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Critical validation error: {str(e)}")
            return False
    
    def _load_registry(self) -> Dict[str, Any]:
        """
        Load and parse the registry JSON file.
        
        Returns:
            The parsed registry data
            
        Raises:
            RegistryValidationError: If file cannot be loaded or parsed
        """
        if not self.registry_path.exists():
            raise RegistryValidationError(f"Registry file not found: {self.registry_path}")
        
        if not self.registry_path.is_file():
            raise RegistryValidationError(f"Registry path is not a file: {self.registry_path}")
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise RegistryValidationError("Registry must be a JSON object")
            
            return data
            
        except json.JSONDecodeError as e:
            raise RegistryValidationError(f"Invalid JSON in registry: {e}")
        except IOError as e:
            raise RegistryValidationError(f"Failed to read registry: {e}")
    
    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """
        Validate that the registry has the required schema.
        
        Args:
            data: The registry data to validate
        """
        required_fields = ['version', 'agents', 'config']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            self.errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check field types
        if 'version' in data and not isinstance(data['version'], str):
            self.errors.append(f"version must be a string, got {type(data['version']).__name__}")
        
        if 'agents' in data and not isinstance(data['agents'], list):
            self.errors.append(f"agents must be a list, got {type(data['agents']).__name__}")
        
        if 'config' in data and not isinstance(data['config'], dict):
            self.errors.append(f"config must be an object, got {type(data['config']).__name__}")
    
    def _validate_version(self, data: Dict[str, Any]) -> None:
        """
        Validate the registry version.
        
        Args:
            data: The registry data to validate
        """
        version = data.get('version', '')
        
        # Version format: X.Y.Z
        version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        
        if not version_pattern.match(version):
            self.errors.append(f"Invalid version format: {version} (expected X.Y.Z)")
    
    def _validate_agents(self, agents: List[Dict[str, Any]]) -> None:
        """
        Validate all agent entries.
        
        Args:
            agents: List of agent entries to validate
        """
        if not isinstance(agents, list):
            self.errors.append("agents must be a list")
            return
        
        for i, agent in enumerate(agents):
            if not isinstance(agent, dict):
                self.errors.append(f"Agent at index {i} must be an object")
                continue
            
            self._validate_agent(agent, i)
    
    def _validate_agent(self, agent: Dict[str, Any], index: int) -> None:
        """
        Validate a single agent entry.
        
        Args:
            agent: The agent data to validate
            index: Index of the agent in the list (for error messages)
        """
        prefix = f"Agent[{index}]"
        
        # Required fields
        required_fields = [
            'id', 'name', 'human_name', 'specialization', 
            'status', 'spawned_at', 'personality', 'communication_style',
            'traits', 'metrics', 'contributions'
        ]
        
        missing_fields = [field for field in required_fields if field not in agent]
        if missing_fields:
            self.errors.append(f"{prefix}: Missing fields: {', '.join(missing_fields)}")
            return
        
        # Validate agent ID format
        agent_id = agent.get('id', '')
        if not re.match(r'^agent-\d+$', agent_id):
            self.errors.append(f"{prefix}: Invalid agent ID format: {agent_id}")
        
        # Validate name
        try:
            name = agent.get('name', '')
            if not name or not isinstance(name, str):
                self.errors.append(f"{prefix}: name must be a non-empty string")
        except Exception as e:
            self.errors.append(f"{prefix}: name validation failed: {e}")
        
        # Validate specialization
        try:
            spec = agent.get('specialization', '')
            validate_agent_name(spec)
        except ValidationError as e:
            self.errors.append(f"{prefix}: specialization validation failed: {e}")
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'eliminated', 'hall_of_fame']
        status = agent.get('status', '')
        if status not in valid_statuses:
            self.errors.append(f"{prefix}: Invalid status '{status}', must be one of: {', '.join(valid_statuses)}")
        
        # Validate spawned_at timestamp
        self._validate_timestamp(agent.get('spawned_at', ''), f"{prefix}: spawned_at")
        
        # Validate traits
        self._validate_traits(agent.get('traits', {}), prefix)
        
        # Validate metrics
        self._validate_metrics(agent.get('metrics', {}), prefix)
        
        # Validate contributions
        if not isinstance(agent.get('contributions', []), list):
            self.errors.append(f"{prefix}: contributions must be a list")
    
    def _validate_traits(self, traits: Dict[str, Any], prefix: str) -> None:
        """
        Validate agent personality traits.
        
        Args:
            traits: The traits dict to validate
            prefix: Prefix for error messages
        """
        if not isinstance(traits, dict):
            self.errors.append(f"{prefix}: traits must be an object")
            return
        
        required_traits = ['creativity', 'caution', 'speed']
        for trait in required_traits:
            if trait not in traits:
                self.errors.append(f"{prefix}.traits: Missing trait: {trait}")
                continue
            
            value = traits[trait]
            try:
                validate_numeric_range(value, 0, 100, f"{prefix}.traits.{trait}")
            except ValidationError as e:
                self.errors.append(str(e))
    
    def _validate_metrics(self, metrics: Dict[str, Any], prefix: str) -> None:
        """
        Validate agent performance metrics.
        
        Args:
            metrics: The metrics dict to validate
            prefix: Prefix for error messages
        """
        if not isinstance(metrics, dict):
            self.errors.append(f"{prefix}: metrics must be an object")
            return
        
        # Required metric fields
        required_metrics = [
            'issues_resolved', 'prs_merged', 'reviews_given',
            'code_quality_score', 'overall_score'
        ]
        
        for metric in required_metrics:
            if metric not in metrics:
                self.errors.append(f"{prefix}.metrics: Missing metric: {metric}")
                continue
            
            value = metrics[metric]
            
            # Count metrics must be non-negative integers
            if metric in ['issues_resolved', 'prs_merged', 'reviews_given']:
                if not isinstance(value, int) or value < 0:
                    self.errors.append(
                        f"{prefix}.metrics.{metric}: Must be non-negative integer, got {value}"
                    )
            
            # Score metrics must be 0-1
            elif metric in ['code_quality_score', 'overall_score']:
                try:
                    validate_numeric_range(value, 0.0, 1.0, f"{prefix}.metrics.{metric}")
                except ValidationError as e:
                    self.errors.append(str(e))
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate the registry configuration.
        
        Args:
            config: The config dict to validate
        """
        if not isinstance(config, dict):
            self.errors.append("config must be an object")
            return
        
        # Required config fields
        required_fields = [
            'spawn_interval_hours', 'max_active_agents',
            'elimination_threshold', 'promotion_threshold',
            'metrics_weight'
        ]
        
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            self.warnings.append(f"Config missing optional fields: {', '.join(missing_fields)}")
        
        # Validate numeric configs
        if 'spawn_interval_hours' in config:
            try:
                validate_numeric_range(config['spawn_interval_hours'], 0, 168, 'spawn_interval_hours')
            except ValidationError as e:
                self.errors.append(f"config.{e}")
        
        if 'max_active_agents' in config:
            try:
                validate_numeric_range(config['max_active_agents'], 1, 100, 'max_active_agents')
            except ValidationError as e:
                self.errors.append(f"config.{e}")
        
        # Validate thresholds (0-1)
        for threshold in ['elimination_threshold', 'promotion_threshold']:
            if threshold in config:
                try:
                    validate_numeric_range(config[threshold], 0.0, 1.0, threshold)
                except ValidationError as e:
                    self.errors.append(f"config.{e}")
        
        # Validate metrics_weight
        if 'metrics_weight' in config:
            self._validate_metrics_weight(config['metrics_weight'])
    
    def _validate_metrics_weight(self, weights: Dict[str, Any]) -> None:
        """
        Validate metrics weight configuration.
        
        Args:
            weights: The metrics weight dict to validate
        """
        if not isinstance(weights, dict):
            self.errors.append("config.metrics_weight must be an object")
            return
        
        # All weights should sum to approximately 1.0
        total_weight = sum(w for w in weights.values() if isinstance(w, (int, float)))
        
        if abs(total_weight - 1.0) > 0.01:
            self.warnings.append(
                f"config.metrics_weight: Total weight is {total_weight:.2f}, "
                "should sum to 1.0"
            )
        
        # Each weight should be 0-1
        for key, value in weights.items():
            try:
                validate_numeric_range(value, 0.0, 1.0, f"metrics_weight.{key}")
            except ValidationError as e:
                self.errors.append(f"config.{e}")
    
    def _validate_timestamps(self, data: Dict[str, Any]) -> None:
        """
        Validate registry timestamps.
        
        Args:
            data: The registry data to validate
        """
        if 'last_spawn' in data:
            self._validate_timestamp(data['last_spawn'], 'last_spawn')
        
        if 'last_evaluation' in data:
            self._validate_timestamp(data['last_evaluation'], 'last_evaluation')
    
    def _validate_timestamp(self, timestamp: str, field_name: str) -> None:
        """
        Validate an ISO 8601 timestamp.
        
        Args:
            timestamp: The timestamp string to validate
            field_name: Name of the field for error messages
        """
        if not timestamp:
            return
        
        if not isinstance(timestamp, str):
            self.errors.append(f"{field_name}: Must be a string, got {type(timestamp).__name__}")
            return
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Check if timestamp is reasonable (not in future, not too old)
            now = datetime.now(timezone.utc)
            
            if dt > now + timedelta(minutes=5):  # Allow 5 min clock skew
                self.warnings.append(f"{field_name}: Timestamp is in the future: {timestamp}")
            
            # Check if timestamp is older than 1 year
            if dt < now - timedelta(days=365):
                self.warnings.append(f"{field_name}: Timestamp is older than 1 year: {timestamp}")
                
        except (ValueError, AttributeError) as e:
            self.errors.append(f"{field_name}: Invalid timestamp format: {timestamp} ({e})")
    
    def _check_duplicates(self, agents: List[Dict[str, Any]]) -> None:
        """
        Check for duplicate agent IDs.
        
        Args:
            agents: List of agent entries to check
        """
        agent_ids = [agent.get('id', '') for agent in agents]
        seen_ids = set()
        duplicates = set()
        
        for agent_id in agent_ids:
            if agent_id in seen_ids:
                duplicates.add(agent_id)
            seen_ids.add(agent_id)
        
        if duplicates:
            self.errors.append(f"Duplicate agent IDs found: {', '.join(sorted(duplicates))}")
    
    def _validate_hall_of_fame(self, hall_of_fame: List[Any]) -> None:
        """
        Validate the hall of fame entries.
        
        Args:
            hall_of_fame: List of hall of fame entries
        """
        if not isinstance(hall_of_fame, list):
            self.errors.append("hall_of_fame must be a list")
            return
        
        # If not empty, validate structure
        for i, entry in enumerate(hall_of_fame):
            if not isinstance(entry, dict):
                self.errors.append(f"hall_of_fame[{i}]: Must be an object")
                continue
            
            # Hall of fame entries should have similar structure to agents
            if 'id' not in entry:
                self.errors.append(f"hall_of_fame[{i}]: Missing agent ID")
    
    def get_report(self) -> str:
        """
        Generate a validation report.
        
        Returns:
            A formatted report string
        """
        report = ["=" * 70, "🔒 Agent Registry Security Validation Report", "=" * 70, ""]
        
        report.append(f"Registry: {self.registry_path}")
        report.append("")
        
        if not self.errors and not self.warnings:
            report.append("✅ All validation checks passed!")
            report.append("")
            report.append("The registry is secure and data integrity is verified.")
        else:
            if self.errors:
                report.append(f"❌ Errors: {len(self.errors)}")
                for i, error in enumerate(self.errors, 1):
                    report.append(f"  {i}. {error}")
                report.append("")
            
            if self.warnings:
                report.append(f"⚠️  Warnings: {len(self.warnings)}")
                for i, warning in enumerate(self.warnings, 1):
                    report.append(f"  {i}. {warning}")
                report.append("")
        
        report.append("=" * 70)
        return "\n".join(report)


def main():
    """Main entry point for the validator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate agent registry for security and data integrity"
    )
    parser.add_argument(
        '--registry',
        type=Path,
        default=Path('.github/agent-system/registry.json'),
        help='Path to registry.json file'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    
    args = parser.parse_args()
    
    # Create and run validator
    validator = RegistryValidator(args.registry)
    is_valid = validator.validate()
    
    # Print report
    print(validator.get_report())
    
    # Exit with appropriate code
    if not is_valid:
        sys.exit(1)
    elif args.strict and validator.warnings:
        print("\n⚠️  Strict mode: Exiting with error due to warnings")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
