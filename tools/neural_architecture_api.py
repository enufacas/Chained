#!/usr/bin/env python3
"""
Neural Architecture API

Provides a programmatic REST-style API for the self-evolving neural architecture
system. Enables easy integration with workflows, external systems, and automation.

Author: @APIs-architect
Inspired by: Margaret Hamilton - Rigorous and reliable API design

Features:
- Experiment lifecycle management
- Architecture evolution control
- Pattern recognition queries
- Recommendations retrieval
- Status and health monitoring
- Batch operations support

Example:
    from neural_architecture_api import NeuralArchitectureAPI
    
    api = NeuralArchitectureAPI()
    
    # Create new architecture
    status, response = api.create_architecture("ci-build")
    
    # Record execution
    status, response = api.record_execution("ci-build", success=True)
    
    # Get recommendations
    status, response = api.get_recommendations("ci-build")
"""

import json
import sys
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from self_evolving_neural_architecture import (
    ArchitectureEvolutionConfig,
    EvolvingArchitectureManager,
    SelfEvolvingNeuralArchitecture,
)


class NeuralArchitectureAPI:
    """
    Programmatic API for neural architecture operations.
    
    Provides a clean interface for:
    - Architecture lifecycle management (create, read, delete)
    - Execution recording and success tracking
    - Evolution control and triggers
    - Recommendations retrieval
    - Pattern analysis and queries
    - System health and status monitoring
    
    All methods return a tuple of (status_code, response_dict) for
    consistent API behavior.
    """
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the Neural Architecture API.
        
        Args:
            repo_root: Repository root path (auto-detected if not provided)
        """
        self.manager = EvolvingArchitectureManager(repo_root=repo_root)
        self.repo_root = self.manager.repo_root
    
    # ==================== Architecture Management ====================
    
    def create_architecture(
        self,
        workflow_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Create a new neural architecture for a workflow.
        
        Args:
            workflow_name: Name of the workflow to optimize
            config: Optional configuration overrides
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            # Validate inputs
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            # Check if architecture already exists
            if workflow_name in self.manager.architectures:
                return (HTTPStatus.CONFLICT, {
                    "error": f"Architecture for '{workflow_name}' already exists",
                    "code": "ARCHITECTURE_EXISTS",
                    "workflow_name": workflow_name
                })
            
            # Create the architecture
            arch = self.manager.get_or_create(workflow_name)
            
            # Apply custom config if provided
            if config:
                if 'base_learning_rate' in config:
                    arch.config.base_learning_rate = float(config['base_learning_rate'])
                if 'success_rate_threshold' in config:
                    arch.config.success_rate_threshold = float(config['success_rate_threshold'])
                if 'min_hidden_neurons' in config:
                    arch.config.min_hidden_neurons = int(config['min_hidden_neurons'])
                if 'max_hidden_neurons' in config:
                    arch.config.max_hidden_neurons = int(config['max_hidden_neurons'])
            
            # Save the architecture
            arch.save_architecture()
            
            return (HTTPStatus.CREATED, {
                "message": f"Architecture created for '{workflow_name}'",
                "workflow_name": workflow_name,
                "architecture_summary": arch._get_architecture_summary(),
                "config": {
                    "base_learning_rate": arch.config.base_learning_rate,
                    "success_rate_threshold": arch.config.success_rate_threshold,
                    "min_hidden_neurons": arch.config.min_hidden_neurons,
                    "max_hidden_neurons": arch.config.max_hidden_neurons
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "CREATION_FAILED"
            })
    
    def get_architecture(
        self,
        workflow_name: str
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Get details of a neural architecture.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            if workflow_name not in self.manager.architectures:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Architecture for '{workflow_name}' not found",
                    "code": "ARCHITECTURE_NOT_FOUND",
                    "workflow_name": workflow_name
                })
            
            arch = self.manager.architectures[workflow_name]
            status = arch.get_status()
            
            return (HTTPStatus.OK, {
                "workflow_name": workflow_name,
                "status": status,
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "pattern_type": p.pattern_type,
                        "confidence": p.confidence,
                        "occurrences": p.occurrences
                    }
                    for p in arch.recognized_patterns.values()
                ]
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "GET_FAILED"
            })
    
    def delete_architecture(
        self,
        workflow_name: str
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Delete a neural architecture.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            if workflow_name not in self.manager.architectures:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Architecture for '{workflow_name}' not found",
                    "code": "ARCHITECTURE_NOT_FOUND",
                    "workflow_name": workflow_name
                })
            
            # Remove from manager
            del self.manager.architectures[workflow_name]
            
            # Remove storage file
            arch_file = self.manager.storage_path / f"{self._safe_filename(workflow_name)}.json"
            if arch_file.exists():
                arch_file.unlink()
            
            return (HTTPStatus.OK, {
                "message": f"Architecture for '{workflow_name}' deleted",
                "workflow_name": workflow_name,
                "deleted_at": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "DELETE_FAILED"
            })
    
    def list_architectures(self) -> Tuple[int, Dict[str, Any]]:
        """
        List all neural architectures.
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            architectures = []
            for name, arch in self.manager.architectures.items():
                architectures.append({
                    "workflow_name": name,
                    "success_rate": arch.get_success_rate(),
                    "execution_count": arch.execution_count,
                    "evolution_count": arch.evolution_count,
                    "architecture_summary": arch._get_architecture_summary()
                })
            
            return (HTTPStatus.OK, {
                "count": len(architectures),
                "architectures": architectures
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "LIST_FAILED"
            })
    
    # ==================== Execution Recording ====================
    
    def record_execution(
        self,
        workflow_name: str,
        success: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Record a workflow execution result.
        
        Args:
            workflow_name: Name of the workflow
            success: Whether the execution was successful
            context: Optional execution context
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            # Get or create architecture
            arch = self.manager.get_or_create(workflow_name)
            
            # Record execution
            arch.record_execution(success, context)
            
            # Save architecture
            arch.save_architecture()
            
            return (HTTPStatus.OK, {
                "message": f"Execution recorded for '{workflow_name}'",
                "workflow_name": workflow_name,
                "success": success,
                "execution_count": arch.execution_count,
                "current_success_rate": arch.get_success_rate(),
                "evolution_triggered": arch.evolution_count > 0 and arch._should_evolve()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "RECORD_FAILED"
            })
    
    def batch_record_executions(
        self,
        executions: List[Dict[str, Any]]
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Record multiple workflow executions in batch.
        
        Args:
            executions: List of execution records with workflow_name, success, and optional context
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not executions:
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "At least one execution is required",
                    "code": "EMPTY_BATCH"
                })
            
            results = []
            errors = []
            
            for idx, execution in enumerate(executions):
                workflow_name = execution.get('workflow_name')
                success = execution.get('success')
                context = execution.get('context')
                
                if not workflow_name:
                    errors.append({
                        "index": idx,
                        "error": "Missing workflow_name"
                    })
                    continue
                
                if success is None:
                    errors.append({
                        "index": idx,
                        "error": "Missing success field"
                    })
                    continue
                
                # Record the execution
                arch = self.manager.get_or_create(workflow_name)
                arch.record_execution(bool(success), context)
                arch.save_architecture()
                
                results.append({
                    "workflow_name": workflow_name,
                    "success": bool(success),
                    "execution_count": arch.execution_count
                })
            
            return (HTTPStatus.OK, {
                "message": f"Batch recording complete",
                "recorded": len(results),
                "errors": len(errors),
                "results": results,
                "error_details": errors if errors else None
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "BATCH_RECORD_FAILED"
            })
    
    # ==================== Evolution Control ====================
    
    def trigger_evolution(
        self,
        workflow_name: str,
        force: bool = False
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Trigger evolution for a neural architecture.
        
        Args:
            workflow_name: Name of the workflow
            force: Whether to force evolution even if not needed
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            if workflow_name not in self.manager.architectures:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Architecture for '{workflow_name}' not found",
                    "code": "ARCHITECTURE_NOT_FOUND",
                    "workflow_name": workflow_name
                })
            
            arch = self.manager.architectures[workflow_name]
            
            # Check if evolution is needed
            if not force and not arch._should_evolve():
                return (HTTPStatus.OK, {
                    "message": "Evolution not needed",
                    "workflow_name": workflow_name,
                    "evolved": False,
                    "reason": "Success rate above threshold or insufficient data",
                    "success_rate": arch.get_success_rate(),
                    "threshold": arch.config.success_rate_threshold
                })
            
            # Capture before state
            before_fitness = arch.architecture_fitness
            before_summary = arch._get_architecture_summary()
            before_learning_rate = arch.current_learning_rate
            
            # Perform evolution
            arch.evolve()
            
            return (HTTPStatus.OK, {
                "message": f"Evolution completed for '{workflow_name}'",
                "workflow_name": workflow_name,
                "evolved": True,
                "evolution_number": arch.evolution_count,
                "before": {
                    "architecture": before_summary,
                    "fitness": before_fitness,
                    "learning_rate": before_learning_rate
                },
                "after": {
                    "architecture": arch._get_architecture_summary(),
                    "fitness": arch.architecture_fitness,
                    "learning_rate": arch.current_learning_rate
                }
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "EVOLUTION_FAILED"
            })
    
    def evolve_all(self) -> Tuple[int, Dict[str, Any]]:
        """
        Trigger evolution check for all architectures.
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            results = []
            evolved_count = 0
            
            for workflow_name, arch in self.manager.architectures.items():
                evolved = False
                if arch._should_evolve():
                    arch.evolve()
                    evolved = True
                    evolved_count += 1
                
                results.append({
                    "workflow_name": workflow_name,
                    "evolved": evolved,
                    "success_rate": arch.get_success_rate(),
                    "evolution_count": arch.evolution_count
                })
            
            return (HTTPStatus.OK, {
                "message": "Evolution cycle complete",
                "total_architectures": len(self.manager.architectures),
                "evolved_count": evolved_count,
                "results": results
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "EVOLVE_ALL_FAILED"
            })
    
    # ==================== Recommendations ====================
    
    def get_recommendations(
        self,
        workflow_name: str,
        context: Optional[Dict[str, float]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Get workflow parameter recommendations.
        
        Args:
            workflow_name: Name of the workflow
            context: Optional execution context
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            # Get or create architecture (will create with defaults if new)
            arch = self.manager.get_or_create(workflow_name)
            
            # Get recommendations
            recommendations = arch.get_recommendations(context)
            
            return (HTTPStatus.OK, {
                "workflow_name": workflow_name,
                "recommendations": recommendations,
                "confidence": arch.architecture_fitness,
                "based_on_executions": arch.execution_count,
                "success_rate": arch.get_success_rate()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "RECOMMENDATIONS_FAILED"
            })
    
    # ==================== Pattern Analysis ====================
    
    def get_patterns(
        self,
        workflow_name: str,
        pattern_type: Optional[str] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Get recognized patterns for a workflow.
        
        Args:
            workflow_name: Name of the workflow
            pattern_type: Optional filter by pattern type
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            if not workflow_name or not workflow_name.strip():
                return (HTTPStatus.BAD_REQUEST, {
                    "error": "Workflow name is required",
                    "code": "INVALID_WORKFLOW_NAME"
                })
            
            workflow_name = workflow_name.strip()
            
            if workflow_name not in self.manager.architectures:
                return (HTTPStatus.NOT_FOUND, {
                    "error": f"Architecture for '{workflow_name}' not found",
                    "code": "ARCHITECTURE_NOT_FOUND",
                    "workflow_name": workflow_name
                })
            
            arch = self.manager.architectures[workflow_name]
            
            patterns = []
            for pattern in arch.recognized_patterns.values():
                if pattern_type and pattern.pattern_type != pattern_type:
                    continue
                patterns.append({
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "pattern_data": pattern.pattern_data,
                    "confidence": pattern.confidence,
                    "occurrences": pattern.occurrences,
                    "last_seen": pattern.last_seen
                })
            
            return (HTTPStatus.OK, {
                "workflow_name": workflow_name,
                "count": len(patterns),
                "patterns": patterns,
                "filter": pattern_type
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "PATTERNS_FAILED"
            })
    
    # ==================== System Health ====================
    
    def get_system_summary(self) -> Tuple[int, Dict[str, Any]]:
        """
        Get summary of all neural architectures.
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            summary = self.manager.get_summary()
            
            return (HTTPStatus.OK, {
                **summary,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "SUMMARY_FAILED"
            })
    
    def get_health_status(self) -> Tuple[int, Dict[str, Any]]:
        """
        Get health status of the neural architecture system.
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            total_architectures = len(self.manager.architectures)
            
            if total_architectures == 0:
                return (HTTPStatus.OK, {
                    "status": "healthy",
                    "message": "System operational, no architectures registered",
                    "architectures": 0
                })
            
            # Calculate health metrics
            success_rates = [arch.get_success_rate() for arch in self.manager.architectures.values()]
            avg_success_rate = sum(success_rates) / len(success_rates)
            
            low_performing = sum(1 for rate in success_rates if rate < 0.5)
            critical = sum(1 for rate in success_rates if rate < 0.3)
            
            # Determine overall health
            if critical > 0:
                status = "critical"
            elif low_performing > total_architectures * 0.3:
                status = "degraded"
            elif avg_success_rate < 0.7:
                status = "warning"
            else:
                status = "healthy"
            
            return (HTTPStatus.OK, {
                "status": status,
                "total_architectures": total_architectures,
                "average_success_rate": avg_success_rate,
                "low_performing_count": low_performing,
                "critical_count": critical,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "HEALTH_CHECK_FAILED"
            })
    
    def generate_report(self) -> Tuple[int, Dict[str, Any]]:
        """
        Generate a comprehensive report.
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        try:
            report = self.manager.generate_full_report()
            
            return (HTTPStatus.OK, {
                "report": report,
                "generated_at": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            return (HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": str(e),
                "code": "REPORT_FAILED"
            })
    
    # ==================== Utility Methods ====================
    
    def _safe_filename(self, name: str) -> str:
        """Convert workflow name to safe filename."""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Neural Architecture API - @APIs-architect"
    )
    parser.add_argument(
        '--create',
        metavar='WORKFLOW',
        help='Create architecture for workflow'
    )
    parser.add_argument(
        '--get',
        metavar='WORKFLOW',
        help='Get architecture details'
    )
    parser.add_argument(
        '--delete',
        metavar='WORKFLOW',
        help='Delete architecture'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all architectures'
    )
    parser.add_argument(
        '--record',
        metavar='WORKFLOW',
        help='Record execution for workflow'
    )
    parser.add_argument(
        '--success',
        action='store_true',
        help='Execution was successful (use with --record)'
    )
    parser.add_argument(
        '--evolve',
        metavar='WORKFLOW',
        help='Trigger evolution for workflow'
    )
    parser.add_argument(
        '--evolve-all',
        action='store_true',
        help='Evolve all architectures'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force evolution even if not needed'
    )
    parser.add_argument(
        '--recommend',
        metavar='WORKFLOW',
        help='Get recommendations for workflow'
    )
    parser.add_argument(
        '--patterns',
        metavar='WORKFLOW',
        help='Get patterns for workflow'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Get system summary'
    )
    parser.add_argument(
        '--health',
        action='store_true',
        help='Get health status'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive report'
    )
    
    args = parser.parse_args()
    
    api = NeuralArchitectureAPI()
    
    result = None
    
    if args.create:
        status, result = api.create_architecture(args.create)
    elif args.get:
        status, result = api.get_architecture(args.get)
    elif args.delete:
        status, result = api.delete_architecture(args.delete)
    elif args.list:
        status, result = api.list_architectures()
    elif args.record:
        status, result = api.record_execution(args.record, args.success)
    elif args.evolve:
        status, result = api.trigger_evolution(args.evolve, force=args.force)
    elif args.evolve_all:
        status, result = api.evolve_all()
    elif args.recommend:
        status, result = api.get_recommendations(args.recommend)
    elif args.patterns:
        status, result = api.get_patterns(args.patterns)
    elif args.summary:
        status, result = api.get_system_summary()
    elif args.health:
        status, result = api.get_health_status()
    elif args.report:
        status, result = api.generate_report()
    else:
        parser.print_help()
        return 1
    
    if result:
        print(json.dumps(result, indent=2))
    
    return 0 if status < 400 else 1


if __name__ == '__main__':
    sys.exit(main())
