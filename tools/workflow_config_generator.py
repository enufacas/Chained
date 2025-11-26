#!/usr/bin/env python3
"""
Workflow Configuration Variant Generator

Automatically generates workflow configuration variants for A/B testing.
Focuses on common optimization patterns like schedule, timeout, concurrency.

Author: @create-guru
Inspired by: Nikola Tesla - Inventive configuration optimization
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone


class WorkflowConfigGenerator:
    """
    Generates workflow configuration variants for A/B testing.
    
    Features:
    - Schedule optimization variants
    - Timeout/retry configuration variants
    - Concurrency setting variants
    - Resource allocation variants
    - Caching strategy variants
    """
    
    # Pre-defined optimization templates
    SCHEDULE_VARIANTS = {
        "less_frequent": {
            "description": "Run less frequently to reduce load",
            "multiplier": 2.0  # 2x the interval
        },
        "more_frequent": {
            "description": "Run more frequently for faster feedback",
            "multiplier": 0.5  # Half the interval
        },
        "optimal_timing": {
            "description": "Run at optimal times (off-peak hours)",
            "shift_hours": 4  # Shift to different time
        }
    }
    
    TIMEOUT_VARIANTS = {
        "conservative": {
            "description": "Longer timeout for reliability",
            "multiplier": 1.5
        },
        "aggressive": {
            "description": "Shorter timeout for faster feedback",
            "multiplier": 0.7
        },
        "adaptive": {
            "description": "Dynamically adjust based on history",
            "strategy": "percentile_95"
        }
    }
    
    CONCURRENCY_VARIANTS = {
        "sequential": {
            "description": "One at a time (safest)",
            "group": "workflow",
            "cancel_in_progress": False
        },
        "parallel": {
            "description": "Allow parallel execution",
            "group": None,
            "cancel_in_progress": False
        },
        "cancel_old": {
            "description": "Cancel old runs when new starts",
            "group": "workflow",
            "cancel_in_progress": True
        }
    }
    
    CACHING_VARIANTS = {
        "no_cache": {
            "description": "Disable caching for fresh builds",
            "enabled": False
        },
        "basic_cache": {
            "description": "Basic dependency caching",
            "enabled": True,
            "paths": ["~/.cache", "node_modules", ".pip"]
        },
        "aggressive_cache": {
            "description": "Aggressive multi-layer caching",
            "enabled": True,
            "paths": ["~/.cache", "node_modules", ".pip", ".github/cache"]
        }
    }
    
    def __init__(self):
        """Initialize the configuration generator."""
        self.generated_configs = []
    
    def generate_schedule_variants(
        self, 
        current_schedule: str,
        workflow_name: str
    ) -> Dict[str, Any]:
        """
        Generate schedule configuration variants.
        
        Args:
            current_schedule: Current cron schedule
            workflow_name: Name of the workflow
        
        Returns:
            Dictionary of variant configurations
        """
        variants = {
            "control": {
                "name": "Current Schedule",
                "description": "Existing schedule configuration",
                "config": {
                    "schedule": current_schedule
                }
            }
        }
        
        # Parse cron schedule
        cron_parts = current_schedule.strip().split()
        if len(cron_parts) == 5:
            minute, hour, day, month, weekday = cron_parts
            
            # Variant 1: Less frequent (double the interval)
            variants["less_frequent"] = {
                "name": "Less Frequent",
                "description": "Run half as often to reduce load",
                "config": {
                    "schedule": self._adjust_schedule_frequency(
                        current_schedule, 
                        multiplier=2.0
                    )
                }
            }
            
            # Variant 2: More frequent (half the interval)
            if hour != "*":  # Only if not already running every hour
                variants["more_frequent"] = {
                    "name": "More Frequent",
                    "description": "Run twice as often for faster feedback",
                    "config": {
                        "schedule": self._adjust_schedule_frequency(
                            current_schedule,
                            multiplier=0.5
                        )
                    }
                }
            
            # Variant 3: Shift to off-peak hours
            if hour not in ["*", "*/1", "*/2"]:
                variants["off_peak"] = {
                    "name": "Off-Peak Hours",
                    "description": "Run during off-peak hours",
                    "config": {
                        "schedule": self._shift_schedule_time(
                            current_schedule,
                            shift_hours=4
                        )
                    }
                }
        
        return variants
    
    def generate_timeout_variants(
        self,
        current_timeout: Optional[int],
        workflow_name: str,
        job_name: str
    ) -> Dict[str, Any]:
        """
        Generate timeout configuration variants.
        
        Args:
            current_timeout: Current timeout in minutes (None if not set)
            workflow_name: Name of the workflow
            job_name: Name of the job
        
        Returns:
            Dictionary of variant configurations
        """
        # Default timeout if not set
        base_timeout = current_timeout if current_timeout else 360  # 6 hours default
        
        variants = {
            "control": {
                "name": "Current Timeout",
                "description": f"Current timeout: {base_timeout} minutes",
                "config": {
                    "timeout-minutes": base_timeout
                }
            },
            "conservative": {
                "name": "Conservative Timeout",
                "description": "50% longer timeout for reliability",
                "config": {
                    "timeout-minutes": int(base_timeout * 1.5)
                }
            },
            "aggressive": {
                "name": "Aggressive Timeout",
                "description": "30% shorter timeout for faster feedback",
                "config": {
                    "timeout-minutes": int(base_timeout * 0.7)
                }
            }
        }
        
        return variants
    
    def generate_concurrency_variants(
        self,
        workflow_name: str,
        current_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate concurrency configuration variants.
        
        Args:
            workflow_name: Name of the workflow
            current_config: Current concurrency configuration
        
        Returns:
            Dictionary of variant configurations
        """
        variants = {
            "control": {
                "name": "Current Concurrency",
                "description": "Existing concurrency setup",
                "config": current_config if current_config else {
                    "group": None,
                    "cancel-in-progress": False
                }
            },
            "sequential": {
                "name": "Sequential Execution",
                "description": "One run at a time (safest)",
                "config": {
                    "group": f"{workflow_name}-sequential",
                    "cancel-in-progress": False
                }
            },
            "cancel_old": {
                "name": "Cancel Old Runs",
                "description": "Cancel old runs when new starts",
                "config": {
                    "group": f"{workflow_name}-cancel",
                    "cancel-in-progress": True
                }
            }
        }
        
        return variants
    
    def generate_retry_variants(
        self,
        workflow_name: str,
        current_retries: int = 0
    ) -> Dict[str, Any]:
        """
        Generate retry configuration variants.
        
        Args:
            workflow_name: Name of the workflow
            current_retries: Current retry count
        
        Returns:
            Dictionary of variant configurations
        """
        variants = {
            "control": {
                "name": "Current Retries",
                "description": f"{current_retries} retries",
                "config": {
                    "max_attempts": current_retries
                }
            },
            "no_retry": {
                "name": "No Retries",
                "description": "Fail fast without retries",
                "config": {
                    "max_attempts": 1
                }
            },
            "moderate_retry": {
                "name": "Moderate Retries",
                "description": "2 retry attempts",
                "config": {
                    "max_attempts": 3
                }
            },
            "aggressive_retry": {
                "name": "Aggressive Retries",
                "description": "5 retry attempts for reliability",
                "config": {
                    "max_attempts": 6
                }
            }
        }
        
        return variants
    
    def generate_experiment_from_workflow(
        self,
        workflow_path: Path,
        optimization_type: str
    ) -> Dict[str, Any]:
        """
        Generate a complete A/B testing experiment from a workflow file.
        
        Args:
            workflow_path: Path to workflow YAML file
            optimization_type: Type of optimization (schedule, timeout, concurrency, retry)
        
        Returns:
            Experiment configuration dictionary
        """
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        workflow_name = workflow_path.stem
        
        # Generate variants based on optimization type
        if optimization_type == "schedule":
            schedule = workflow_data.get('on', {}).get('schedule', [{}])[0].get('cron', '0 0 * * *')
            variants = self.generate_schedule_variants(schedule, workflow_name)
        
        elif optimization_type == "timeout":
            # Get first job's timeout
            jobs = workflow_data.get('jobs', {})
            first_job = list(jobs.values())[0] if jobs else {}
            current_timeout = first_job.get('timeout-minutes')
            variants = self.generate_timeout_variants(
                current_timeout,
                workflow_name,
                list(jobs.keys())[0] if jobs else "job"
            )
        
        elif optimization_type == "concurrency":
            current_config = workflow_data.get('concurrency')
            variants = self.generate_concurrency_variants(workflow_name, current_config)
        
        elif optimization_type == "retry":
            variants = self.generate_retry_variants(workflow_name)
        
        else:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
        
        # Create experiment configuration
        experiment = {
            "name": f"{workflow_name} - {optimization_type.title()} Optimization",
            "description": f"A/B test different {optimization_type} configurations for {workflow_name}",
            "workflow_name": workflow_name,
            "optimization_type": optimization_type,
            "variants": variants,
            "metrics": [
                "execution_time",
                "success_rate",
                "resource_usage",
                "failure_rate"
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "recommended_duration_days": 7,
            "minimum_samples": 20
        }
        
        return experiment
    
    def _adjust_schedule_frequency(
        self,
        cron_schedule: str,
        multiplier: float
    ) -> str:
        """
        Adjust cron schedule frequency by multiplier.
        
        Args:
            cron_schedule: Original cron schedule
            multiplier: Frequency multiplier (2.0 = half as often, 0.5 = twice as often)
        
        Returns:
            Adjusted cron schedule
        """
        parts = cron_schedule.strip().split()
        if len(parts) != 5:
            return cron_schedule
        
        minute, hour, day, month, weekday = parts
        
        # Handle */N patterns
        if hour.startswith("*/"):
            interval = int(hour[2:])
            new_interval = max(1, min(23, int(interval * multiplier)))
            return f"{minute} */{new_interval} {day} {month} {weekday}"
        
        # For specific hours, adjust differently
        elif hour.isdigit():
            # Can't easily adjust, return original
            return cron_schedule
        
        return cron_schedule
    
    def _shift_schedule_time(
        self,
        cron_schedule: str,
        shift_hours: int
    ) -> str:
        """
        Shift cron schedule by hours.
        
        Args:
            cron_schedule: Original cron schedule
            shift_hours: Hours to shift
        
        Returns:
            Shifted cron schedule
        """
        parts = cron_schedule.strip().split()
        if len(parts) != 5:
            return cron_schedule
        
        minute, hour, day, month, weekday = parts
        
        if hour.isdigit():
            original_hour = int(hour)
            new_hour = (original_hour + shift_hours) % 24
            return f"{minute} {new_hour} {day} {month} {weekday}"
        
        return cron_schedule


def main():
    """CLI interface for workflow config generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate workflow configuration variants for A/B testing"
    )
    parser.add_argument(
        "workflow",
        help="Path to workflow YAML file"
    )
    parser.add_argument(
        "optimization_type",
        choices=["schedule", "timeout", "concurrency", "retry"],
        help="Type of optimization to generate"
    )
    parser.add_argument(
        "--output",
        help="Output file for experiment configuration (JSON)",
        default=None
    )
    
    args = parser.parse_args()
    
    generator = WorkflowConfigGenerator()
    workflow_path = Path(args.workflow)
    
    if not workflow_path.exists():
        print(f"Error: Workflow file not found: {workflow_path}")
        return 1
    
    experiment = generator.generate_experiment_from_workflow(
        workflow_path,
        args.optimization_type
    )
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(experiment, f, indent=2)
        print(f"✅ Experiment configuration saved to: {args.output}")
    else:
        print(json.dumps(experiment, indent=2))
    
    return 0


if __name__ == "__main__":
    exit(main())
