#!/usr/bin/env python3
"""
A/B Testing Workflow Integration Helper

Simplifies integration of GitHub Actions workflows with the A/B testing system.
Provides easy-to-use utilities for workflows to participate in experiments.

Author: @APIs-architect
Designed for: Seamless workflow integration with minimal configuration
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))
from ab_testing_api import ABTestingAPI


class WorkflowIntegration:
    """
    Helper class for integrating workflows with A/B testing.
    
    Provides:
    - Automatic variant selection
    - Simplified metrics recording
    - Configuration retrieval
    - Error handling with fallbacks
    """
    
    def __init__(
        self, 
        workflow_name: str, 
        experiment_id: Optional[str] = None,
        registry_path: str = ".github/agent-system/ab_tests_registry.json"
    ):
        """
        Initialize workflow integration.
        
        Args:
            workflow_name: Name of the workflow
            experiment_id: Optional explicit experiment ID
            registry_path: Path to experiment registry
        """
        self.workflow_name = workflow_name
        self.experiment_id = experiment_id
        self.api = ABTestingAPI(registry_path=registry_path)
        self.variant_name = None
        self.config = None
        self._is_participating = False
    
    def participate(self, default_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Participate in an A/B test if one exists for this workflow.
        
        Args:
            default_config: Default configuration to use if not in an experiment
        
        Returns:
            Configuration to use (either from experiment or default)
        """
        try:
            # Find active experiment for this workflow
            if not self.experiment_id:
                self.experiment_id = self._find_experiment()
            
            if not self.experiment_id:
                # No experiment - use default config
                self._is_participating = False
                self.variant_name = "default"
                self.config = default_config
                return default_config
            
            # Get experiment details
            status_code, response = self.api.get_experiment(self.experiment_id)
            
            if status_code != 200:
                # Experiment not found or error - use default
                self._is_participating = False
                self.variant_name = "default"
                self.config = default_config
                return default_config
            
            experiment = response["experiment"]
            
            # Select variant (simple round-robin for now)
            variant_name = self._select_variant(experiment)
            self.variant_name = variant_name
            self._is_participating = True
            
            # Get configuration for this variant
            variant_config = experiment["variants"][variant_name]["config"]
            self.config = variant_config
            
            print(f"🧪 A/B Test: Using variant '{variant_name}' from experiment '{experiment['name']}'")
            print(f"   Config: {json.dumps(variant_config, indent=2)}")
            
            return variant_config
        
        except Exception as e:
            print(f"⚠️  Error participating in A/B test: {e}")
            print(f"   Falling back to default configuration")
            self._is_participating = False
            self.variant_name = "default"
            self.config = default_config
            return default_config
    
    def record_success(
        self,
        execution_time: float,
        metrics: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Record a successful run with metrics.
        
        Args:
            execution_time: Execution time in seconds
            metrics: Additional metrics to record
        
        Returns:
            True if recorded successfully, False otherwise
        """
        if not self._is_participating:
            return False
        
        try:
            all_metrics = {
                "execution_time": execution_time,
                "success_rate": 1.0,  # This run succeeded
                **(metrics or {})
            }
            
            status_code, response = self.api.record_sample(
                experiment_id=self.experiment_id,
                variant_name=self.variant_name,
                metrics=all_metrics,
                metadata={
                    "workflow": self.workflow_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "outcome": "success"
                }
            )
            
            if status_code == 201:
                print(f"✅ Recorded metrics for variant '{self.variant_name}'")
                return True
            else:
                print(f"⚠️  Failed to record metrics: {response.get('error', 'Unknown error')}")
                return False
        
        except Exception as e:
            print(f"⚠️  Error recording metrics: {e}")
            return False
    
    def record_failure(
        self,
        execution_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Record a failed run.
        
        Args:
            execution_time: Execution time before failure (if available)
            error: Error message or description
        
        Returns:
            True if recorded successfully, False otherwise
        """
        if not self._is_participating:
            return False
        
        try:
            metrics = {
                "success_rate": 0.0,  # This run failed
            }
            
            if execution_time is not None:
                metrics["execution_time"] = execution_time
            
            status_code, response = self.api.record_sample(
                experiment_id=self.experiment_id,
                variant_name=self.variant_name,
                metrics=metrics,
                metadata={
                    "workflow": self.workflow_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "outcome": "failure",
                    "error": error or "Unknown error"
                }
            )
            
            if status_code == 201:
                print(f"📊 Recorded failure for variant '{self.variant_name}'")
                return True
            else:
                print(f"⚠️  Failed to record failure metrics: {response.get('error', 'Unknown error')}")
                return False
        
        except Exception as e:
            print(f"⚠️  Error recording failure: {e}")
            return False
    
    def _find_experiment(self) -> Optional[str]:
        """
        Find an active experiment for this workflow.
        
        Returns:
            Experiment ID if found, None otherwise
        """
        try:
            status_code, response = self.api.list_experiments(
                status="active",
                workflow_name=self.workflow_name
            )
            
            if status_code != 200 or not response.get("experiments"):
                return None
            
            # Return the first active experiment
            experiments = response["experiments"]
            if experiments:
                return experiments[0]["id"]
            
            return None
        
        except Exception as e:
            print(f"⚠️  Error finding experiment: {e}")
            return None
    
    def _select_variant(self, experiment: Dict[str, Any]) -> str:
        """
        Select which variant to use for this run.
        
        For now, uses simple round-robin based on sample counts.
        Future enhancement: Thompson Sampling for better exploration/exploitation.
        
        Args:
            experiment: Experiment details
        
        Returns:
            Name of selected variant
        """
        variants = experiment["variants"]
        
        # Simple strategy: Pick variant with fewest samples
        min_samples = float('inf')
        selected_variant = None
        
        for variant_name, variant_data in variants.items():
            sample_count = variant_data.get("total_samples", 0)
            if sample_count < min_samples:
                min_samples = sample_count
                selected_variant = variant_name
        
        return selected_variant or list(variants.keys())[0]


# ==================== GitHub Actions Helper Functions ====================

def get_config_from_env(
    env_var: str = "AB_TEST_CONFIG",
    default_config: Optional[Dict[str, Any]] = None,
    max_size: int = 10240  # 10KB limit
) -> Dict[str, Any]:
    """
    Get A/B test configuration from environment variable.
    
    Useful for GitHub Actions where config is set via env vars.
    
    Args:
        env_var: Environment variable name
        default_config: Default configuration if env var not set
        max_size: Maximum allowed size in bytes (default 10KB)
    
    Returns:
        Configuration dictionary
    """
    config_json = os.environ.get(env_var)
    
    if config_json:
        # Check size limit to prevent DoS
        if len(config_json) > max_size:
            print(f"⚠️  {env_var} exceeds size limit ({len(config_json)} > {max_size} bytes)")
            return default_config or {}
        
        try:
            return json.loads(config_json)
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing {env_var}: {e}")
    
    return default_config or {}


def setup_workflow_testing(
    workflow_name: str,
    default_config: Dict[str, Any],
    experiment_id: Optional[str] = None,
    registry_path: str = ".github/agent-system/ab_tests_registry.json"
) -> tuple[WorkflowIntegration, Dict[str, Any]]:
    """
    Quick setup for A/B testing in a workflow.
    
    Args:
        workflow_name: Name of the workflow
        default_config: Default configuration
        experiment_id: Optional explicit experiment ID
        registry_path: Path to experiment registry
    
    Returns:
        Tuple of (integration object, config to use)
    """
    integration = WorkflowIntegration(workflow_name, experiment_id, registry_path)
    config = integration.participate(default_config)
    return integration, config


# ==================== CLI Interface ====================

def main():
    """CLI for workflow integration testing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="A/B Testing Workflow Integration Helper"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Participate command
    participate_parser = subparsers.add_parser(
        "participate",
        help="Participate in A/B test for a workflow"
    )
    participate_parser.add_argument("workflow", help="Workflow name")
    participate_parser.add_argument(
        "--default-config",
        help="Default config (JSON)",
        default="{}"
    )
    participate_parser.add_argument(
        "--experiment-id",
        help="Explicit experiment ID"
    )
    
    # Record metrics command
    record_parser = subparsers.add_parser(
        "record",
        help="Record metrics for a workflow run"
    )
    record_parser.add_argument("workflow", help="Workflow name")
    record_parser.add_argument("--experiment-id", required=True, help="Experiment ID")
    record_parser.add_argument("--variant", required=True, help="Variant name")
    record_parser.add_argument("--execution-time", type=float, required=True, help="Execution time (seconds)")
    record_parser.add_argument("--success", action="store_true", help="Run was successful")
    record_parser.add_argument("--error", help="Error message if failed")
    record_parser.add_argument("--metrics", help="Additional metrics (JSON)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "participate":
        try:
            default_config = json.loads(args.default_config)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --default-config")
            return 1
        
        integration = WorkflowIntegration(args.workflow, args.experiment_id)
        config = integration.participate(default_config)
        
        print("\n📋 Configuration to use:")
        print(json.dumps(config, indent=2))
        
        if integration._is_participating:
            print(f"\n✅ Participating in experiment {integration.experiment_id}")
            print(f"   Variant: {integration.variant_name}")
        else:
            print("\n📌 Not participating in any experiment - using default config")
        
        return 0
    
    elif args.command == "record":
        api = ABTestingAPI()
        
        metrics = {"execution_time": args.execution_time}
        
        if args.success:
            metrics["success_rate"] = 1.0
        else:
            metrics["success_rate"] = 0.0
        
        if args.metrics:
            try:
                additional_metrics = json.loads(args.metrics)
                metrics.update(additional_metrics)
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in --metrics, ignoring")
        
        metadata = {
            "workflow": args.workflow,
            "outcome": "success" if args.success else "failure"
        }
        
        if args.error:
            metadata["error"] = args.error
        
        status_code, response = api.record_sample(
            experiment_id=args.experiment_id,
            variant_name=args.variant,
            metrics=metrics,
            metadata=metadata
        )
        
        print(json.dumps(response, indent=2))
        return 0 if status_code < 400 else 1
    
    return 0


if __name__ == "__main__":
    exit(main())
