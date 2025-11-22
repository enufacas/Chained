#!/usr/bin/env python3
"""
A/B Testing REST API

Provides a comprehensive REST API for managing autonomous A/B testing experiments.
This API enables programmatic access to all A/B testing functionality.

Author: @APIs-architect
Inspired by: Margaret Hamilton - Rigorous and systematic API design
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from http import HTTPStatus

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))
from ab_testing_engine import ABTestingEngine
from ab_testing_workflow_analyzer import WorkflowAnalyzer
from autonomous_experiment_creator import AutonomousExperimentCreator


class ABTestingAPI:
    """
    Programmatic API for A/B testing operations.
    
    Provides a clean interface for:
    - Experiment lifecycle management (create, read, update, complete)
    - Metrics collection and recording
    - Analysis and winner determination
    - Opportunity detection and experiment generation
    """
    
    def __init__(self, registry_path: str = ".github/agent-system/ab_tests_registry.json"):
        """
        Initialize the A/B Testing API.
        
        Args:
            registry_path: Path to the experiment registry
        """
        self.engine = ABTestingEngine(registry_path=registry_path)
        self.analyzer = WorkflowAnalyzer()
        self.creator = AutonomousExperimentCreator()
        self.registry_path = registry_path
    
    # ==================== Experiment Management ====================
    
    def create_experiment(
        self,
        name: str,
        description: str,
        variants: Dict[str, Dict[str, Any]],
        metrics: List[str],
        workflow_name: Optional[str] = None,
        priority: str = "medium"
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Create a new A/B testing experiment.
        
        Args:
            name: Human-readable experiment name
            description: Detailed description
            variants: Dictionary of variant configurations
            metrics: List of metrics to track
            workflow_name: Optional workflow identifier
            priority: Experiment priority (high, medium, low)
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            # Validate inputs
            if not name or not name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Experiment name is required",
                    "code": "INVALID_NAME"
                })
            
            if not variants or len(variants) < 2:
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "At least 2 variants are required",
                    "code": "INSUFFICIENT_VARIANTS"
                })
            
            if not metrics:
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "At least one metric must be specified",
                    "code": "NO_METRICS"
                })
            
            # Create the experiment
            experiment_id = self.engine.create_experiment(
                name=name.strip(),
                description=description.strip(),
                variants=variants,
                metrics=metrics,
                workflow_name=workflow_name
            )
            
            return (HTTPStatus.CREATED, {
                "success": True,
                "experiment_id": experiment_id,
                "message": f"Experiment '{name}' created successfully",
                "details": {
                    "name": name,
                    "workflow": workflow_name,
                    "variant_count": len(variants),
                    "metrics": metrics,
                    "priority": priority
                }
            })
        
        except ValueError as e:
            return (HTTPStatus.CONFLICT, {
                "error": str(e),
                "code": "CREATION_FAILED"
            })
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Internal error creating experiment",
                "code": "INTERNAL_ERROR",
                "details": str(e)
            })
    
    def get_experiment(self, experiment_id: str) -> Tuple[int, Dict[str, Any]]:
        """
        Retrieve details for a specific experiment.
        
        Args:
            experiment_id: Unique experiment identifier
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            details = self.engine.get_experiment_details(experiment_id)
            
            if not details:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Experiment '{experiment_id}' not found",
                    "code": "EXPERIMENT_NOT_FOUND"
                })
            
            return (HTTPStatus.OK, {
                "success": True,
                "experiment": details
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error retrieving experiment",
                "code": "RETRIEVAL_ERROR",
                "details": str(e)
            })
    
    def list_experiments(
        self,
        status: Optional[str] = None,
        workflow_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[int, Dict[str, Any]]:
        """
        List experiments with optional filtering.
        
        Args:
            status: Filter by status (active, completed, archived)
            workflow_name: Filter by workflow
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            # Get all experiments matching status
            experiments = self.engine.list_experiments(status=status)
            
            # Apply workflow filter if specified
            if workflow_name:
                experiments = [
                    exp for exp in experiments
                    if exp.get("workflow_name") == workflow_name
                ]
            
            # Apply pagination
            total = len(experiments)
            experiments = experiments[offset:offset+limit]
            
            return (HTTPStatus.OK, {
                "success": True,
                "experiments": experiments,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "returned": len(experiments)
                }
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error listing experiments",
                "code": "LIST_ERROR",
                "details": str(e)
            })
    
    def complete_experiment(
        self,
        experiment_id: str,
        winner: str,
        notes: Optional[str] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Mark an experiment as complete with a declared winner.
        
        Args:
            experiment_id: Experiment identifier
            winner: Name of the winning variant
            notes: Optional completion notes
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            self.engine.complete_experiment(
                experiment_id=experiment_id,
                winner=winner,
                notes=notes or f"Completed via API at {datetime.now(timezone.utc).isoformat()}"
            )
            
            return (HTTPStatus.OK, {
                "success": True,
                "message": f"Experiment '{experiment_id}' completed",
                "winner": winner
            })
        
        except ValueError as e:
            return (HTTPStatus.BAD_REQUEST, {
                "error": str(e),
                "code": "COMPLETION_FAILED"
            })
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error completing experiment",
                "code": "COMPLETION_ERROR",
                "details": str(e)
            })
    
    # ==================== Metrics Management ====================
    
    def record_sample(
        self,
        experiment_id: str,
        variant_name: str,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Record a performance sample for a variant.
        
        Args:
            experiment_id: Experiment identifier
            variant_name: Name of the variant
            metrics: Dictionary of metric values
            metadata: Optional metadata for the sample
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            # Validate experiment exists
            details = self.engine.get_experiment_details(experiment_id)
            if not details:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Experiment '{experiment_id}' not found",
                    "code": "EXPERIMENT_NOT_FOUND"
                })
            
            # Validate variant exists
            if variant_name not in details["variants"]:
                return (HTTPStatus.BAD_REQUEST, {
                    "error": f"Variant '{variant_name}' not found in experiment",
                    "code": "INVALID_VARIANT",
                    "available_variants": list(details["variants"].keys())
                })
            
            # Record the sample
            self.engine.record_sample(
                experiment_id=experiment_id,
                variant_name=variant_name,
                metrics=metrics,
                metadata=metadata or {}
            )
            
            return (HTTPStatus.CREATED, {
                "success": True,
                "message": "Sample recorded successfully",
                "experiment_id": experiment_id,
                "variant": variant_name,
                "metrics": metrics
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error recording sample",
                "code": "RECORDING_ERROR",
                "details": str(e)
            })
    
    def get_metrics(
        self,
        experiment_id: str,
        variant_name: Optional[str] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Retrieve metrics for an experiment or specific variant.
        
        Args:
            experiment_id: Experiment identifier
            variant_name: Optional variant filter
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            details = self.engine.get_experiment_details(experiment_id)
            
            if not details:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Experiment '{experiment_id}' not found",
                    "code": "EXPERIMENT_NOT_FOUND"
                })
            
            if variant_name:
                if variant_name not in details["variants"]:
                    return (HTTPStatus.BAD_REQUEST, {
                        "error": f"Variant '{variant_name}' not found",
                        "code": "INVALID_VARIANT"
                    })
                
                variant_data = details["variants"][variant_name]
                return (HTTPStatus.OK, {
                    "success": True,
                    "experiment_id": experiment_id,
                    "variant": variant_name,
                    "metrics": variant_data.get("metrics", {}),
                    "sample_count": variant_data.get("total_samples", 0)
                })
            
            # Return all variants
            metrics_summary = {}
            for var_name, var_data in details["variants"].items():
                metrics_summary[var_name] = {
                    "metrics": var_data.get("metrics", {}),
                    "sample_count": var_data.get("total_samples", 0)
                }
            
            return (HTTPStatus.OK, {
                "success": True,
                "experiment_id": experiment_id,
                "variants": metrics_summary
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error retrieving metrics",
                "code": "METRICS_ERROR",
                "details": str(e)
            })
    
    # ==================== Analysis ====================
    
    def analyze_experiment(self, experiment_id: str) -> Tuple[int, Dict[str, Any]]:
        """
        Perform statistical analysis on an experiment.
        
        Args:
            experiment_id: Experiment identifier
        
        Returns:
            Tuple of (status_code, response_dict with analysis results)
        """
        try:
            analysis = self.engine.analyze_experiment(experiment_id)
            
            if not analysis:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Experiment '{experiment_id}' not found or has no data",
                    "code": "ANALYSIS_UNAVAILABLE"
                })
            
            return (HTTPStatus.OK, {
                "success": True,
                "experiment_id": experiment_id,
                "analysis": analysis
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error analyzing experiment",
                "code": "ANALYSIS_ERROR",
                "details": str(e)
            })
    
    # ==================== Autonomous Operations ====================
    
    def discover_opportunities(self) -> Tuple[int, Dict[str, Any]]:
        """
        Scan workflows for A/B testing opportunities.
        
        Returns:
            Tuple of (status_code, response with opportunities)
        """
        try:
            opportunities = self.analyzer.analyze_all_workflows()
            
            return (HTTPStatus.OK, {
                "success": True,
                "opportunities_found": len(opportunities),
                "opportunities": opportunities
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error discovering opportunities",
                "code": "DISCOVERY_ERROR",
                "details": str(e)
            })
    
    def auto_create_experiments(
        self,
        max_concurrent: int = 5,
        dry_run: bool = False
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Automatically create experiments from detected opportunities.
        
        Args:
            max_concurrent: Maximum concurrent experiments
            dry_run: If True, only simulate creation
        
        Returns:
            Tuple of (status_code, response with creation results)
        """
        try:
            if dry_run:
                opportunities = self.analyzer.analyze_all_workflows()
                active_experiments = self.engine.list_experiments(status="active")
                
                return (HTTPStatus.OK, {
                    "success": True,
                    "dry_run": True,
                    "opportunities_found": len(opportunities),
                    "active_experiments": len(active_experiments),
                    "available_slots": max(0, max_concurrent - len(active_experiments)),
                    "opportunities": opportunities[:max_concurrent - len(active_experiments)]
                })
            
            # Run actual creation cycle
            results = self.creator.run_autonomous_cycle()
            
            return (HTTPStatus.OK, {
                "success": True,
                "cycle_results": results
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error in autonomous creation",
                "code": "AUTO_CREATE_ERROR",
                "details": str(e)
            })
    
    # ==================== System Status ====================
    
    def get_system_status(self) -> Tuple[int, Dict[str, Any]]:
        """
        Get overall A/B testing system status.
        
        Returns:
            Tuple of (status_code, status information)
        """
        try:
            all_experiments = self.engine.list_experiments()
            active = [e for e in all_experiments if e["status"] == "active"]
            completed = [e for e in all_experiments if e["status"] == "completed"]
            
            return (HTTPStatus.OK, {
                "success": True,
                "status": "operational",
                "statistics": {
                    "total_experiments": len(all_experiments),
                    "active_experiments": len(active),
                    "completed_experiments": len(completed),
                    "registry_path": self.registry_path
                },
                "active_experiments": [
                    {
                        "id": exp["id"],
                        "name": exp["name"],
                        "workflow": exp.get("workflow_name"),
                        "created_at": exp["created_at"]
                    }
                    for exp in active
                ]
            })
        
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "Error retrieving system status",
                "code": "STATUS_ERROR",
                "details": str(e)
            })


# ==================== CLI Interface ====================

def main():
    """CLI interface for the A/B Testing API."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="A/B Testing API - Programmatic interface for experiment management"
    )
    subparsers = parser.add_subparsers(dest="command", help="API commands")
    
    # Status command
    subparsers.add_parser("status", help="Get system status")
    
    # List experiments
    list_parser = subparsers.add_parser("list", help="List experiments")
    list_parser.add_argument("--status", choices=["active", "completed"], help="Filter by status")
    list_parser.add_argument("--workflow", help="Filter by workflow name")
    
    # Get experiment
    get_parser = subparsers.add_parser("get", help="Get experiment details")
    get_parser.add_argument("experiment_id", help="Experiment ID")
    
    # Analyze experiment
    analyze_parser = subparsers.add_parser("analyze", help="Analyze experiment")
    analyze_parser.add_argument("experiment_id", help="Experiment ID")
    
    # Discover opportunities
    subparsers.add_parser("discover", help="Discover optimization opportunities")
    
    # Auto-create experiments
    auto_parser = subparsers.add_parser("auto-create", help="Auto-create experiments")
    auto_parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    auto_parser.add_argument("--max-concurrent", type=int, default=5, help="Max concurrent experiments")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize API
    api = ABTestingAPI()
    
    # Execute command
    if args.command == "status":
        status_code, response = api.get_system_status()
    elif args.command == "list":
        status_code, response = api.list_experiments(
            status=args.status,
            workflow_name=args.workflow
        )
    elif args.command == "get":
        status_code, response = api.get_experiment(args.experiment_id)
    elif args.command == "analyze":
        status_code, response = api.analyze_experiment(args.experiment_id)
    elif args.command == "discover":
        status_code, response = api.discover_opportunities()
    elif args.command == "auto-create":
        status_code, response = api.auto_create_experiments(
            max_concurrent=args.max_concurrent,
            dry_run=args.dry_run
        )
    else:
        print(f"Unknown command: {args.command}")
        return 1
    
    # Output response
    print(json.dumps(response, indent=2))
    return 0 if status_code < 400 else 1


if __name__ == "__main__":
    exit(main())
