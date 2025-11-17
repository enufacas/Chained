#!/usr/bin/env python3
"""
Autonomous A/B Testing Engine for Workflow Configurations

This module implements a rigorous A/B testing system for evaluating different
workflow configurations in the Chained autonomous system. It follows Margaret
Hamilton's principles of systematic design and defensive programming.

Author: @engineer-master
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class ABTestingEngine:
    """
    Core engine for managing A/B tests of workflow configurations.
    
    Responsibilities:
    - Create and manage experiments
    - Track variant performance
    - Determine statistical winners
    - Integrate with existing metrics infrastructure
    """
    
    def __init__(self, registry_path: str = ".github/agent-system/ab_tests_registry.json"):
        """
        Initialize the A/B testing engine.
        
        Args:
            registry_path: Path to the A/B tests registry file
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_registry_exists()
    
    def _ensure_registry_exists(self) -> None:
        """Ensure the registry file exists with proper structure."""
        if not self.registry_path.exists():
            initial_registry = {
                "version": "1.0.0",
                "experiments": [],
                "config": {
                    "min_samples_per_variant": 10,
                    "confidence_threshold": 0.95,
                    "min_improvement_threshold": 0.05,
                    "max_experiment_duration_days": 14
                }
            }
            self._write_registry(initial_registry)
    
    def _read_registry(self) -> Dict[str, Any]:
        """Read the experiments registry."""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Defensive: if registry is corrupted, reinitialize
            self._ensure_registry_exists()
            with open(self.registry_path, 'r') as f:
                return json.load(f)
    
    def _write_registry(self, registry: Dict[str, Any]) -> None:
        """Write the experiments registry atomically."""
        # Write to temp file first, then rename for atomicity
        temp_path = self.registry_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(registry, f, indent=2)
        temp_path.replace(self.registry_path)
    
    def create_experiment(
        self,
        name: str,
        description: str,
        variants: Dict[str, Dict[str, Any]],
        metrics: List[str],
        workflow_name: Optional[str] = None
    ) -> str:
        """
        Create a new A/B testing experiment.
        
        Args:
            name: Human-readable experiment name
            description: Detailed description of what's being tested
            variants: Dictionary of variant configurations
                     Each variant should have a unique key and configuration dict
            metrics: List of metric names to track (e.g., 'execution_time', 'success_rate')
            workflow_name: Optional workflow this experiment applies to
        
        Returns:
            experiment_id: Unique identifier for this experiment
        
        Raises:
            ValueError: If variants are invalid or experiment already exists
        """
        if len(variants) < 2:
            raise ValueError("Experiment must have at least 2 variants")
        
        registry = self._read_registry()
        
        # Check for duplicate experiment names
        for exp in registry["experiments"]:
            if exp["name"] == name and exp["status"] == "active":
                raise ValueError(f"Active experiment with name '{name}' already exists")
        
        # Generate unique experiment ID
        experiment_id = self._generate_experiment_id(name)
        
        # Create experiment structure
        experiment = {
            "id": experiment_id,
            "name": name,
            "description": description,
            "workflow_name": workflow_name,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": "active",
            "variants": {},
            "metrics": metrics,
            "results": None
        }
        
        # Initialize each variant
        for variant_name, config in variants.items():
            experiment["variants"][variant_name] = {
                "config": config,
                "samples": [],
                "metrics": {metric: [] for metric in metrics},
                "total_samples": 0
            }
        
        registry["experiments"].append(experiment)
        self._write_registry(registry)
        
        return experiment_id
    
    def _generate_experiment_id(self, name: str) -> str:
        """Generate a unique experiment ID based on name and timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        content = f"{name}-{timestamp}"
        return f"exp-{hashlib.sha256(content.encode()).hexdigest()[:12]}"
    
    def record_sample(
        self,
        experiment_id: str,
        variant_name: str,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a sample data point for a variant.
        
        Args:
            experiment_id: Unique experiment identifier
            variant_name: Name of the variant being tested
            metrics: Dictionary of metric values for this sample
            metadata: Optional additional context about this sample
        
        Raises:
            ValueError: If experiment or variant doesn't exist
        """
        registry = self._read_registry()
        
        # Find the experiment
        experiment = self._find_experiment(registry, experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if experiment["status"] != "active":
            raise ValueError(f"Experiment {experiment_id} is not active")
        
        if variant_name not in experiment["variants"]:
            raise ValueError(f"Variant {variant_name} not found in experiment")
        
        # Record the sample
        variant = experiment["variants"][variant_name]
        sample = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "metrics": metrics,
            "metadata": metadata or {}
        }
        
        variant["samples"].append(sample)
        variant["total_samples"] += 1
        
        # Update aggregated metrics
        for metric_name, value in metrics.items():
            if metric_name in variant["metrics"]:
                variant["metrics"][metric_name].append(value)
        
        self._write_registry(registry)
    
    def _find_experiment(self, registry: Dict[str, Any], experiment_id: str) -> Optional[Dict[str, Any]]:
        """Find an experiment by ID in the registry."""
        for exp in registry["experiments"]:
            if exp["id"] == experiment_id:
                return exp
        return None
    
    def analyze_experiment(self, experiment_id: str, use_advanced: bool = True) -> Dict[str, Any]:
        """
        Analyze an experiment and determine if there's a clear winner.
        
        Args:
            experiment_id: Unique experiment identifier
            use_advanced: Use advanced statistical methods (Bayesian, sequential testing)
        
        Returns:
            Analysis results including statistical significance and recommendations
        """
        registry = self._read_registry()
        experiment = self._find_experiment(registry, experiment_id)
        
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        config = registry["config"]
        min_samples = config["min_samples_per_variant"]
        
        # Check if we have enough data
        all_variants_ready = all(
            v["total_samples"] >= min_samples
            for v in experiment["variants"].values()
        )
        
        if not all_variants_ready:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {min_samples} samples per variant",
                "current_samples": {
                    name: v["total_samples"]
                    for name, v in experiment["variants"].items()
                }
            }
        
        # Calculate statistics for each variant
        variant_stats = {}
        for variant_name, variant_data in experiment["variants"].items():
            variant_stats[variant_name] = self._calculate_variant_statistics(
                variant_data, experiment["metrics"]
            )
        
        # Determine winner (simple comparison for now, can be enhanced with proper statistical tests)
        winner = self._determine_winner(variant_stats, config["min_improvement_threshold"])
        
        result = {
            "status": "analyzed",
            "variant_statistics": variant_stats,
            "winner": winner,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        # Add advanced analysis if requested
        if use_advanced:
            try:
                from ab_testing_advanced import integrate_advanced_analysis
                advanced_results = integrate_advanced_analysis(experiment)
                result["advanced_analysis"] = advanced_results
            except ImportError:
                # Advanced analysis module not available
                result["advanced_analysis"] = {"error": "Advanced analysis module not available"}
        
        return result
    
    def _calculate_variant_statistics(
        self,
        variant_data: Dict[str, Any],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Calculate statistical summary for a variant."""
        stats = {}
        
        for metric in metrics:
            values = variant_data["metrics"].get(metric, [])
            if values:
                stats[metric] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
            else:
                stats[metric] = {
                    "mean": 0,
                    "min": 0,
                    "max": 0,
                    "count": 0
                }
        
        return stats
    
    def _determine_winner(
        self,
        variant_stats: Dict[str, Dict[str, Any]],
        min_improvement: float
    ) -> Optional[Dict[str, Any]]:
        """
        Determine if there's a clear winner among variants.
        
        For now, uses a simple comparison. In production, would use proper
        statistical hypothesis testing (t-test, chi-square, etc.)
        """
        if not variant_stats:
            return None
        
        # Compare based on primary metric (assume first metric or 'success_rate')
        # This is a simplified approach; real implementation would be more sophisticated
        
        # For now, return the variant with best average across all metrics
        variant_scores = {}
        for variant_name, stats in variant_stats.items():
            # Calculate overall score (normalized average across metrics)
            scores = [metric_stats.get("mean", 0) for metric_stats in stats.values()]
            variant_scores[variant_name] = sum(scores) / len(scores) if scores else 0
        
        if not variant_scores:
            return None
        
        best_variant = max(variant_scores.keys(), key=lambda k: variant_scores[k])
        best_score = variant_scores[best_variant]
        
        # Check if improvement is significant
        other_scores = [s for v, s in variant_scores.items() if v != best_variant]
        if other_scores:
            avg_other = sum(other_scores) / len(other_scores)
            improvement = (best_score - avg_other) / avg_other if avg_other > 0 else 0
            
            if improvement >= min_improvement:
                return {
                    "variant": best_variant,
                    "score": best_score,
                    "improvement": improvement,
                    "confidence": "medium"  # Would be calculated from statistical test
                }
        
        return None
    
    def complete_experiment(
        self,
        experiment_id: str,
        winner: Optional[str] = None,
        notes: Optional[str] = None
    ) -> None:
        """
        Mark an experiment as complete.
        
        Args:
            experiment_id: Unique experiment identifier
            winner: Optional winner variant name
            notes: Optional notes about the experiment conclusion
        """
        registry = self._read_registry()
        experiment = self._find_experiment(registry, experiment_id)
        
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment["status"] = "completed"
        experiment["completed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        experiment["results"] = {
            "winner": winner,
            "notes": notes or "",
            "final_analysis": self.analyze_experiment(experiment_id)
        }
        
        self._write_registry(registry)
    
    def list_experiments(
        self,
        status: Optional[str] = None,
        workflow_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List experiments with optional filtering.
        
        Args:
            status: Filter by status ('active', 'completed', 'archived')
            workflow_name: Filter by workflow name
        
        Returns:
            List of experiment summaries
        """
        registry = self._read_registry()
        experiments = registry["experiments"]
        
        # Apply filters
        if status:
            experiments = [e for e in experiments if e["status"] == status]
        
        if workflow_name:
            experiments = [e for e in experiments if e.get("workflow_name") == workflow_name]
        
        # Return summaries (not full data)
        return [
            {
                "id": exp["id"],
                "name": exp["name"],
                "status": exp["status"],
                "workflow_name": exp.get("workflow_name"),
                "created_at": exp["created_at"],
                "variant_count": len(exp["variants"]),
                "total_samples": sum(v["total_samples"] for v in exp["variants"].values())
            }
            for exp in experiments
        ]
    
    def get_experiment_details(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get full details of an experiment."""
        registry = self._read_registry()
        return self._find_experiment(registry, experiment_id)


def main():
    """CLI interface for A/B testing engine."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: ab_testing_engine.py <command> [args...]")
        print("\nCommands:")
        print("  list [status] - List experiments")
        print("  analyze <experiment_id> - Analyze an experiment")
        print("  details <experiment_id> - Show experiment details")
        sys.exit(1)
    
    engine = ABTestingEngine()
    command = sys.argv[1]
    
    if command == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        experiments = engine.list_experiments(status=status)
        print(json.dumps(experiments, indent=2))
    
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Error: experiment_id required")
            sys.exit(1)
        experiment_id = sys.argv[2]
        analysis = engine.analyze_experiment(experiment_id)
        print(json.dumps(analysis, indent=2))
    
    elif command == "details":
        if len(sys.argv) < 3:
            print("Error: experiment_id required")
            sys.exit(1)
        experiment_id = sys.argv[2]
        details = engine.get_experiment_details(experiment_id)
        print(json.dumps(details, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
