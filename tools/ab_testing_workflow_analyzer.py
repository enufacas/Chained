#!/usr/bin/env python3
"""
Workflow Configuration Analyzer for A/B Testing

This module analyzes GitHub Actions workflows to identify optimization opportunities
and automatically suggest A/B testing experiments.

Author: @workflows-tech-lead
Inspired by: Martha Graham - Choreographic precision in workflow analysis
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class WorkflowAnalyzer:
    """
    Analyzes GitHub Actions workflows to identify A/B testing opportunities.
    
    Focuses on:
    - Schedule optimization (frequency, timing)
    - Timeout and retry configurations
    - Concurrency settings
    - Resource allocation
    - Caching strategies
    """
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        """
        Initialize the workflow analyzer.
        
        Args:
            workflows_dir: Path to workflows directory
        """
        self.workflows_dir = Path(workflows_dir)
        self.opportunities = []
    
    def analyze_all_workflows(self) -> List[Dict[str, Any]]:
        """
        Analyze all workflows and identify optimization opportunities.
        
        Returns:
            List of optimization opportunities with suggested experiments
        """
        opportunities = []
        
        for workflow_file in self.workflows_dir.glob("*.yml"):
            try:
                opp = self.analyze_workflow(workflow_file)
                if opp:
                    opportunities.extend(opp)
            except Exception as e:
                print(f"Warning: Could not analyze {workflow_file.name}: {e}")
        
        return opportunities
    
    def analyze_workflow(self, workflow_path: Path) -> List[Dict[str, Any]]:
        """
        Analyze a single workflow file for optimization opportunities.
        
        Args:
            workflow_path: Path to workflow YAML file
        
        Returns:
            List of opportunities found in this workflow
        """
        opportunities = []
        
        try:
            with open(workflow_path, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            if not workflow_data:
                return opportunities
            
            workflow_name = workflow_path.stem
            
            # Skip ab-testing and test workflows
            if 'ab-testing' in workflow_name or 'test' in workflow_name:
                return opportunities
            
            # Check for schedule optimization opportunities
            if 'on' in workflow_data:
                triggers = workflow_data['on']
                if isinstance(triggers, dict) and 'schedule' in triggers:
                    schedule_opp = self._analyze_schedule(workflow_name, triggers['schedule'])
                    if schedule_opp:
                        opportunities.append(schedule_opp)
            
            # Check for timeout optimization opportunities
            if 'jobs' in workflow_data:
                timeout_opp = self._analyze_timeouts(workflow_name, workflow_data['jobs'])
                if timeout_opp:
                    opportunities.append(timeout_opp)
                
                # Check for concurrency optimization
                concurrency_opp = self._analyze_concurrency(workflow_name, workflow_data)
                if concurrency_opp:
                    opportunities.append(concurrency_opp)
        
        except Exception as e:
            print(f"Error parsing {workflow_path}: {e}")
        
        return opportunities
    
    def _analyze_schedule(
        self, 
        workflow_name: str, 
        schedule: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze schedule configuration for optimization.
        
        Args:
            workflow_name: Name of the workflow
            schedule: Schedule configuration from workflow
        
        Returns:
            Optimization opportunity or None
        """
        if not isinstance(schedule, list) or not schedule:
            return None
        
        for schedule_item in schedule:
            if 'cron' in schedule_item:
                cron = schedule_item['cron']
                
                # Parse cron to understand frequency
                frequency_info = self._parse_cron_frequency(cron)
                
                if frequency_info:
                    return {
                        "workflow": workflow_name,
                        "type": "schedule_optimization",
                        "current_config": {
                            "cron": cron,
                            "frequency_minutes": frequency_info["minutes"]
                        },
                        "description": f"Test different schedule frequencies for {workflow_name}",
                        "priority": self._calculate_priority(frequency_info),
                        "suggested_variants": self._suggest_schedule_variants(frequency_info)
                    }
        
        return None
    
    def _parse_cron_frequency(self, cron: str) -> Optional[Dict[str, Any]]:
        """
        Parse cron expression to determine frequency.
        
        Args:
            cron: Cron expression string
        
        Returns:
            Frequency information or None
        """
        # Parse cron: minute hour day month weekday
        parts = cron.split()
        
        if len(parts) != 5:
            return None
        
        minute, hour, day, month, weekday = parts
        
        # Estimate frequency in minutes
        frequency_minutes = None
        
        # Check for hourly patterns: */N * * * *
        if minute.startswith('*/'):
            try:
                interval = int(minute[2:])
                frequency_minutes = interval
            except ValueError:
                pass
        
        # Check for every N hours: 0 */N * * *
        elif hour.startswith('*/'):
            try:
                interval = int(hour[2:])
                frequency_minutes = interval * 60
            except ValueError:
                pass
        
        # Check for daily: 0 N * * *
        elif day == '*' and month == '*' and weekday == '*':
            frequency_minutes = 24 * 60
        
        if frequency_minutes:
            return {
                "minutes": frequency_minutes,
                "type": "periodic",
                "cron": cron
            }
        
        return None
    
    def _calculate_priority(self, frequency_info: Dict[str, Any]) -> str:
        """
        Calculate optimization priority based on frequency.
        
        Frequent workflows have higher priority for optimization.
        
        Args:
            frequency_info: Parsed frequency information
        
        Returns:
            Priority level: high, medium, or low
        """
        minutes = frequency_info["minutes"]
        
        if minutes <= 15:
            return "high"  # Very frequent, high optimization potential
        elif minutes <= 120:
            return "medium"  # Moderately frequent
        else:
            return "low"  # Less frequent
    
    def _suggest_schedule_variants(
        self, 
        frequency_info: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Suggest schedule variants to test.
        
        Args:
            frequency_info: Current frequency information
        
        Returns:
            Dictionary of variant configurations
        """
        current_minutes = frequency_info["minutes"]
        cron = frequency_info["cron"]
        
        variants = {
            "control": {
                "cron": cron,
                "description": f"Current schedule (every {current_minutes} minutes)",
                "frequency_minutes": current_minutes
            }
        }
        
        # Suggest more frequent variant (25% faster)
        faster_minutes = max(5, int(current_minutes * 0.75))
        if faster_minutes != current_minutes:
            variants["more_frequent"] = {
                "cron": self._generate_cron(faster_minutes),
                "description": f"More frequent (every {faster_minutes} minutes)",
                "frequency_minutes": faster_minutes
            }
        
        # Suggest less frequent variant (33% slower)
        slower_minutes = int(current_minutes * 1.33)
        if slower_minutes != current_minutes and slower_minutes <= 1440:
            variants["less_frequent"] = {
                "cron": self._generate_cron(slower_minutes),
                "description": f"Less frequent (every {slower_minutes} minutes)",
                "frequency_minutes": slower_minutes
            }
        
        return variants
    
    def _generate_cron(self, minutes: int) -> str:
        """
        Generate cron expression for given frequency in minutes.
        
        Args:
            minutes: Frequency in minutes
        
        Returns:
            Cron expression string
        """
        if minutes < 60:
            return f"*/{minutes} * * * *"
        else:
            hours = minutes // 60
            return f"0 */{hours} * * *"
    
    def _analyze_timeouts(
        self, 
        workflow_name: str, 
        jobs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze timeout configurations.
        
        Args:
            workflow_name: Name of the workflow
            jobs: Jobs configuration from workflow
        
        Returns:
            Optimization opportunity or None
        """
        # Check if any jobs have explicit timeout settings
        has_timeouts = False
        timeout_values = []
        
        for job_name, job_config in jobs.items():
            if isinstance(job_config, dict) and 'timeout-minutes' in job_config:
                has_timeouts = True
                timeout_values.append(job_config['timeout-minutes'])
        
        if has_timeouts and timeout_values:
            avg_timeout = sum(timeout_values) / len(timeout_values)
            
            return {
                "workflow": workflow_name,
                "type": "timeout_optimization",
                "current_config": {
                    "average_timeout": avg_timeout,
                    "timeout_values": timeout_values
                },
                "description": f"Test different timeout configurations for {workflow_name}",
                "priority": "medium",
                "suggested_variants": self._suggest_timeout_variants(avg_timeout)
            }
        
        return None
    
    def _suggest_timeout_variants(
        self, 
        current_timeout: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        Suggest timeout variants to test.
        
        Args:
            current_timeout: Current timeout in minutes
        
        Returns:
            Dictionary of variant configurations
        """
        return {
            "control": {
                "timeout_minutes": current_timeout,
                "description": f"Current timeout ({current_timeout} minutes)"
            },
            "increased": {
                "timeout_minutes": int(current_timeout * 1.5),
                "description": f"Increased timeout ({int(current_timeout * 1.5)} minutes)"
            },
            "decreased": {
                "timeout_minutes": max(5, int(current_timeout * 0.75)),
                "description": f"Decreased timeout ({max(5, int(current_timeout * 0.75))} minutes)"
            }
        }
    
    def _analyze_concurrency(
        self, 
        workflow_name: str, 
        workflow_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze concurrency configuration.
        
        Args:
            workflow_name: Name of the workflow
            workflow_data: Full workflow configuration
        
        Returns:
            Optimization opportunity or None
        """
        if 'concurrency' in workflow_data:
            concurrency = workflow_data['concurrency']
            
            # Check if cancel-in-progress is set
            if isinstance(concurrency, dict):
                cancel_in_progress = concurrency.get('cancel-in-progress', False)
                
                return {
                    "workflow": workflow_name,
                    "type": "concurrency_optimization",
                    "current_config": {
                        "cancel_in_progress": cancel_in_progress
                    },
                    "description": f"Test concurrency settings for {workflow_name}",
                    "priority": "low",
                    "suggested_variants": {
                        "control": {
                            "cancel_in_progress": cancel_in_progress,
                            "description": f"Current setting (cancel: {cancel_in_progress})"
                        },
                        "alternative": {
                            "cancel_in_progress": not cancel_in_progress,
                            "description": f"Alternative (cancel: {not cancel_in_progress})"
                        }
                    }
                }
        
        return None
    
    def generate_experiment_proposal(
        self, 
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an A/B testing experiment proposal from an opportunity.
        
        Args:
            opportunity: Optimization opportunity
        
        Returns:
            Experiment proposal ready for creation
        """
        workflow = opportunity["workflow"]
        opp_type = opportunity["type"]
        
        return {
            "name": f"{opp_type.replace('_', ' ').title()}: {workflow}",
            "description": opportunity["description"],
            "workflow_name": workflow,
            "variants": opportunity["suggested_variants"],
            "metrics": self._suggest_metrics(opp_type),
            "priority": opportunity.get("priority", "medium")
        }
    
    def _suggest_metrics(self, optimization_type: str) -> List[str]:
        """
        Suggest relevant metrics based on optimization type.
        
        Args:
            optimization_type: Type of optimization
        
        Returns:
            List of metric names
        """
        metrics_map = {
            "schedule_optimization": [
                "execution_time",
                "success_rate",
                "resource_usage",
                "api_calls"
            ],
            "timeout_optimization": [
                "execution_time",
                "success_rate",
                "timeout_rate"
            ],
            "concurrency_optimization": [
                "execution_time",
                "queue_time",
                "success_rate"
            ]
        }
        
        return metrics_map.get(optimization_type, ["execution_time", "success_rate"])


def main():
    """CLI entry point for workflow analysis."""
    import sys
    
    analyzer = WorkflowAnalyzer()
    opportunities = analyzer.analyze_all_workflows()
    
    print(f"🔍 Found {len(opportunities)} optimization opportunities\n")
    
    for opp in opportunities:
        print(f"**{opp['workflow']}** ({opp['type']})")
        print(f"  Priority: {opp.get('priority', 'medium')}")
        print(f"  {opp['description']}")
        print(f"  Variants: {len(opp['suggested_variants'])}")
        print()
    
    # Output as JSON
    if '--json' in sys.argv:
        print(json.dumps(opportunities, indent=2))
    
    return 0


if __name__ == "__main__":
    exit(main())
