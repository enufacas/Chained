#!/usr/bin/env python3
"""
Workflow Input Validator

Validates inputs for GitHub Actions workflows to ensure data integrity
and prevent invalid configurations from causing workflow failures.

This tool demonstrates comprehensive validation practices for the Chained project.
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import validation utilities
try:
    from validation_utils import (
        ValidationError,
        validate_non_empty_string,
        validate_list_of_strings,
        validate_list_non_empty,
        validate_dict_schema,
        validate_numeric_range,
        validate_percentage,
        safe_file_read,
        validate_json_safe
    )
except ImportError:
    print("Error: validation_utils module not found", file=sys.stderr)
    print("Make sure you are running from the tools directory", file=sys.stderr)
    sys.exit(1)


class WorkflowValidator:
    """Validates GitHub Actions workflow inputs and configurations."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_workflow_file(self, filepath: Path) -> bool:
        """
        Validate a GitHub Actions workflow file.
        
        Args:
            filepath: Path to the workflow YAML file
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Read and parse workflow file
            content = safe_file_read(filepath)
            workflow = yaml.safe_load(content)
            
            if not isinstance(workflow, dict):
                self.errors.append(f"Workflow file must be a YAML object")
                return False
            
            # Validate workflow structure
            self._validate_workflow_structure(workflow, filepath.name)
            
            # Validate workflow inputs if present
            # Note: YAML parsers may convert 'on' to True (boolean)
            trigger_key = True if True in workflow else 'on'
            if trigger_key in workflow and isinstance(workflow[trigger_key], dict):
                if 'workflow_dispatch' in workflow[trigger_key]:
                    dispatch = workflow[trigger_key]['workflow_dispatch']
                    if isinstance(dispatch, dict) and 'inputs' in dispatch:
                        self._validate_workflow_inputs(dispatch['inputs'])
            
            return len(self.errors) == 0
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except ValidationError as e:
            self.errors.append(str(e))
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error: {e}")
            return False
    
    def _validate_workflow_structure(self, workflow: Dict, filename: str) -> None:
        """Validate basic workflow structure."""
        # Check for required top-level keys
        if 'name' not in workflow:
            self.warnings.append(f"Workflow '{filename}' missing 'name' field")
        
        # Note: YAML parsers may convert 'on' to True (boolean)
        # Check for both 'on' and True as keys
        has_trigger = 'on' in workflow or True in workflow
        if not has_trigger:
            self.errors.append(f"Workflow '{filename}' missing 'on' trigger field")
        
        if 'jobs' not in workflow:
            self.errors.append(f"Workflow '{filename}' missing 'jobs' field")
        elif not isinstance(workflow['jobs'], dict):
            self.errors.append(f"Workflow 'jobs' must be an object")
        elif len(workflow['jobs']) == 0:
            self.errors.append(f"Workflow has no jobs defined")
    
    def _validate_workflow_inputs(self, inputs: Dict) -> None:
        """Validate workflow_dispatch inputs."""
        if not isinstance(inputs, dict):
            self.errors.append("workflow_dispatch inputs must be an object")
            return
        
        for input_name, input_spec in inputs.items():
            try:
                # Validate input name
                validate_non_empty_string(input_name, "input name")
                
                # Validate input specification
                if not isinstance(input_spec, dict):
                    self.errors.append(
                        f"Input '{input_name}' specification must be an object"
                    )
                    continue
                
                # Check for required fields
                if 'description' not in input_spec:
                    self.warnings.append(
                        f"Input '{input_name}' missing description"
                    )
                
                if 'required' not in input_spec:
                    self.warnings.append(
                        f"Input '{input_name}' missing 'required' field"
                    )
                
                # Validate type if specified
                if 'type' in input_spec:
                    input_type = input_spec['type']
                    valid_types = ['string', 'boolean', 'choice', 'environment', 'number']
                    if input_type not in valid_types:
                        self.errors.append(
                            f"Input '{input_name}' has invalid type '{input_type}'. "
                            f"Must be one of: {', '.join(valid_types)}"
                        )
                
                # Validate choice options
                if input_spec.get('type') == 'choice':
                    if 'options' not in input_spec:
                        self.errors.append(
                            f"Input '{input_name}' of type 'choice' must have 'options'"
                        )
                    elif not isinstance(input_spec['options'], list):
                        self.errors.append(
                            f"Input '{input_name}' options must be a list"
                        )
                    elif len(input_spec['options']) == 0:
                        self.errors.append(
                            f"Input '{input_name}' options list is empty"
                        )
                
            except ValidationError as e:
                self.errors.append(str(e))
    
    def validate_agent_spawn_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate inputs for agent spawner workflow.
        
        Args:
            inputs: Dictionary of workflow inputs
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Validate spawn mode
            if 'spawn_mode' in inputs:
                spawn_mode = validate_non_empty_string(inputs['spawn_mode'], "spawn_mode")
                valid_modes = ['random', 'specific', 'balanced']
                if spawn_mode not in valid_modes:
                    raise ValidationError(
                        f"spawn_mode must be one of: {', '.join(valid_modes)}"
                    )
            
            # Validate agent name if in specific mode
            if inputs.get('spawn_mode') == 'specific' and 'agent_name' in inputs:
                validate_non_empty_string(inputs['agent_name'], "agent_name")
            
            # Validate count
            if 'count' in inputs:
                count = validate_numeric_range(
                    int(inputs['count']),
                    min_value=1,
                    max_value=10,
                    field_name="count"
                )
            
            return True
            
        except (ValidationError, ValueError) as e:
            self.errors.append(str(e))
            return False
    
    def validate_performance_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Validate agent performance metrics.
        
        Args:
            metrics: Dictionary of performance metrics
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Define expected schema
            schema = {
                'code_quality': (int, float),
                'issue_resolution': (int, float),
                'pr_success': (int, float),
                'peer_review': (int, float)
            }
            
            # Validate each metric
            for metric_name, expected_types in schema.items():
                if metric_name not in metrics:
                    raise ValidationError(f"Missing required metric: {metric_name}")
                
                value = metrics[metric_name]
                if not isinstance(value, expected_types):
                    raise ValidationError(
                        f"Metric '{metric_name}' must be numeric, got {type(value).__name__}"
                    )
                
                # Validate percentage range
                validate_percentage(value, field_name=metric_name)
            
            # Validate weights sum to 100
            total = sum(metrics.values())
            if abs(total - 100.0) > 0.01:
                raise ValidationError(
                    f"Metric weights must sum to 100%, got {total}%"
                )
            
            return True
            
        except ValidationError as e:
            self.errors.append(str(e))
            return False
    
    def get_validation_report(self) -> str:
        """Get a formatted validation report."""
        report = []
        
        if self.errors:
            report.append("❌ Validation Errors:")
            for error in self.errors:
                report.append(f"  - {error}")
        
        if self.warnings:
            report.append("\n⚠️  Warnings:")
            for warning in self.warnings:
                report.append(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            report.append("✅ All validations passed!")
        
        return "\n".join(report)


def main():
    """Main entry point for workflow validator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate GitHub Actions workflow files"
    )
    parser.add_argument(
        'workflow_file',
        type=Path,
        help='Path to workflow YAML file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show verbose output'
    )
    
    args = parser.parse_args()
    
    if not args.workflow_file.exists():
        print(f"Error: File not found: {args.workflow_file}", file=sys.stderr)
        return 1
    
    validator = WorkflowValidator()
    
    if args.verbose:
        print(f"Validating workflow: {args.workflow_file}")
    
    is_valid = validator.validate_workflow_file(args.workflow_file)
    
    print(validator.get_validation_report())
    
    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())
