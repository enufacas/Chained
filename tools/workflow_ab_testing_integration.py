#!/usr/bin/env python3
"""
Workflow A/B Testing Integration Tool

Integrates workflow configuration generation with the A/B testing engine.
Provides end-to-end workflow for creating and managing workflow experiments.

Author: @create-guru
Inspired by: Nikola Tesla - Seamless system integration
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))
from workflow_config_generator import WorkflowConfigGenerator
from ab_testing_engine import ABTestingEngine
from ab_testing_workflow_analyzer import WorkflowAnalyzer


class WorkflowABTestingIntegration:
    """
    Integrates workflow configuration generation with A/B testing.
    
    Features:
    - Automatically create experiments from workflow analysis
    - Generate configuration variants
    - Register experiments with A/B testing engine
    - Track and analyze results
    - Provide recommendations
    """
    
    def __init__(self):
        """Initialize the integration tool."""
        self.config_generator = WorkflowConfigGenerator()
        self.ab_engine = ABTestingEngine()
        self.workflow_analyzer = WorkflowAnalyzer()
    
    def create_experiment_for_workflow(
        self,
        workflow_path: Path,
        optimization_type: str,
        auto_start: bool = False
    ) -> str:
        """
        Create a complete A/B testing experiment for a workflow.
        
        Args:
            workflow_path: Path to workflow YAML file
            optimization_type: Type of optimization (schedule, timeout, concurrency, retry)
            auto_start: Whether to start experiment immediately
        
        Returns:
            experiment_id: ID of created experiment
        """
        # Generate experiment configuration
        experiment_config = self.config_generator.generate_experiment_from_workflow(
            workflow_path,
            optimization_type
        )
        
        # Create experiment in A/B testing engine
        experiment_id = self.ab_engine.create_experiment(
            name=experiment_config["name"],
            description=experiment_config["description"],
            variants={
                variant_name: variant_data["config"]
                for variant_name, variant_data in experiment_config["variants"].items()
            },
            metrics=experiment_config["metrics"],
            workflow_name=experiment_config["workflow_name"]
        )
        
        print(f"✅ Created experiment: {experiment_id}")
        print(f"   Name: {experiment_config['name']}")
        print(f"   Variants: {len(experiment_config['variants'])}")
        print(f"   Metrics: {', '.join(experiment_config['metrics'])}")
        
        return experiment_id
    
    def create_experiments_from_opportunities(
        self,
        max_experiments: int = 5,
        priority_threshold: str = "medium"
    ) -> List[str]:
        """
        Automatically create experiments from workflow analysis opportunities.
        
        Args:
            max_experiments: Maximum number of experiments to create
            priority_threshold: Minimum priority level (low, medium, high)
        
        Returns:
            List of created experiment IDs
        """
        # Analyze workflows for opportunities
        opportunities = self.workflow_analyzer.analyze_all_workflows()
        
        # Filter by priority
        priority_levels = {"low": 0, "medium": 1, "high": 2}
        min_priority = priority_levels.get(priority_threshold, 0)
        
        filtered_opportunities = [
            opp for opp in opportunities
            if priority_levels.get(opp.get("priority", "low"), 0) >= min_priority
        ]
        
        print(f"🔍 Found {len(filtered_opportunities)} opportunities matching criteria")
        
        # Sort by priority and take top N
        filtered_opportunities.sort(
            key=lambda x: priority_levels.get(x.get("priority", "low"), 0),
            reverse=True
        )
        
        selected_opportunities = filtered_opportunities[:max_experiments]
        
        # Create experiments
        created_experiments = []
        
        for opp in selected_opportunities:
            try:
                # Map opportunity to workflow file
                workflow_name = opp.get("workflow_name") or opp.get("workflow")
                if not workflow_name:
                    print(f"⚠️  Opportunity missing workflow name")
                    continue
                
                workflow_path = Path(f".github/workflows/{workflow_name}.yml")
                
                if not workflow_path.exists():
                    print(f"⚠️  Workflow not found: {workflow_path}")
                    continue
                
                # Determine optimization type from opportunity
                optimization_type = opp.get("type", "timeout").replace("_optimization", "")
                
                # Create experiment
                experiment_id = self.create_experiment_for_workflow(
                    workflow_path,
                    optimization_type,
                    auto_start=False
                )
                
                created_experiments.append({
                    "experiment_id": experiment_id,
                    "workflow_name": workflow_name,
                    "optimization_type": optimization_type,
                    "priority": opp.get("priority", "medium")
                })
                
            except Exception as e:
                print(f"❌ Failed to create experiment for {opp['workflow_name']}: {e}")
        
        print(f"\n✨ Created {len(created_experiments)} experiments")
        
        return created_experiments
    
    def generate_experiment_report(
        self,
        experiment_id: str,
        output_format: str = "text"
    ) -> str:
        """
        Generate a comprehensive report for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            output_format: Output format (text, json, markdown)
        
        Returns:
            Report content as string
        """
        # Get experiment details
        details = self.ab_engine.get_experiment_details(experiment_id)
        
        if not details:
            return f"❌ Experiment not found: {experiment_id}"
        
        # Analyze if enough data
        if details["status"] == "active":
            analysis = self.ab_engine.analyze_experiment(experiment_id)
        else:
            analysis = details.get("results", {})
        
        if output_format == "text":
            return self._format_report_text(details, analysis)
        elif output_format == "json":
            return json.dumps({
                "details": details,
                "analysis": analysis
            }, indent=2)
        elif output_format == "markdown":
            return self._format_report_markdown(details, analysis)
        else:
            raise ValueError(f"Unknown output format: {output_format}")
    
    def _format_report_text(
        self,
        details: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Format report as plain text."""
        lines = []
        lines.append(f"📊 Experiment Report: {details['name']}")
        lines.append("=" * 60)
        lines.append(f"ID: {details['id']}")
        lines.append(f"Status: {details['status']}")
        lines.append(f"Workflow: {details.get('workflow_name', 'N/A')}")
        lines.append(f"Created: {details['created_at']}")
        lines.append("")
        
        lines.append("Variants:")
        for variant_name, variant_data in details["variants"].items():
            lines.append(f"  - {variant_name}: {variant_data['total_samples']} samples")
        lines.append("")
        
        if analysis:
            lines.append("Analysis:")
            if "status" in analysis:
                lines.append(f"  Status: {analysis['status']}")
            if "winner" in analysis and analysis["winner"]:
                lines.append(f"  Winner: {analysis['winner']}")
            if "confidence" in analysis:
                lines.append(f"  Confidence: {analysis['confidence']:.2%}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_report_markdown(
        self,
        details: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Format report as markdown."""
        lines = []
        lines.append(f"# 📊 Experiment Report: {details['name']}")
        lines.append("")
        lines.append("## Experiment Details")
        lines.append("")
        lines.append(f"- **ID**: `{details['id']}`")
        lines.append(f"- **Status**: {details['status']}")
        lines.append(f"- **Workflow**: {details.get('workflow_name', 'N/A')}")
        lines.append(f"- **Created**: {details['created_at']}")
        lines.append("")
        
        lines.append("## Variants")
        lines.append("")
        for variant_name, variant_data in details["variants"].items():
            lines.append(f"### {variant_name}")
            lines.append(f"- Samples: {variant_data['total_samples']}")
            lines.append("")
        
        if analysis:
            lines.append("## Analysis Results")
            lines.append("")
            if "status" in analysis:
                lines.append(f"- **Status**: {analysis['status']}")
            if "winner" in analysis and analysis["winner"]:
                lines.append(f"- **Winner**: {analysis['winner']}")
            if "confidence" in analysis:
                lines.append(f"- **Confidence**: {analysis['confidence']:.2%}")
            lines.append("")
        
        return "\n".join(lines)
    
    def recommend_next_experiments(
        self,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend next experiments to run based on workflow analysis.
        
        Args:
            limit: Maximum number of recommendations
        
        Returns:
            List of recommended experiments
        """
        # Analyze all workflows
        opportunities = self.workflow_analyzer.analyze_all_workflows()
        
        # Get active experiments
        active_experiments = self.ab_engine.list_experiments(status="active")
        active_workflows = {exp["workflow_name"] for exp in active_experiments}
        
        # Filter out workflows with active experiments
        available_opportunities = [
            opp for opp in opportunities
            if (opp.get("workflow_name") or opp.get("workflow")) not in active_workflows
        ]
        
        # Sort by priority
        priority_levels = {"low": 0, "medium": 1, "high": 2}
        available_opportunities.sort(
            key=lambda x: priority_levels.get(x.get("priority", "low"), 0),
            reverse=True
        )
        
        recommendations = []
        for opp in available_opportunities[:limit]:
            workflow_name = opp.get("workflow_name") or opp.get("workflow", "unknown")
            recommendations.append({
                "workflow_name": workflow_name,
                "optimization_type": opp.get("type", "unknown").replace("_optimization", ""),
                "priority": opp.get("priority", "medium"),
                "description": opp.get("description", "No description"),
                "expected_impact": opp.get("expected_impact", "medium")
            })
        
        return recommendations


def main():
    """CLI interface for workflow A/B testing integration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Workflow A/B Testing Integration Tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create experiment command
    create_parser = subparsers.add_parser(
        "create",
        help="Create an experiment for a workflow"
    )
    create_parser.add_argument(
        "workflow",
        help="Path to workflow YAML file"
    )
    create_parser.add_argument(
        "optimization_type",
        choices=["schedule", "timeout", "concurrency", "retry"],
        help="Type of optimization"
    )
    
    # Auto-create command
    auto_parser = subparsers.add_parser(
        "auto-create",
        help="Automatically create experiments from opportunities"
    )
    auto_parser.add_argument(
        "--max",
        type=int,
        default=5,
        help="Maximum experiments to create"
    )
    auto_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Minimum priority level"
    )
    
    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate experiment report"
    )
    report_parser.add_argument(
        "experiment_id",
        help="Experiment ID"
    )
    report_parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format"
    )
    
    # Recommend command
    recommend_parser = subparsers.add_parser(
        "recommend",
        help="Get experiment recommendations"
    )
    recommend_parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of recommendations"
    )
    
    args = parser.parse_args()
    
    integration = WorkflowABTestingIntegration()
    
    if args.command == "create":
        workflow_path = Path(args.workflow)
        if not workflow_path.exists():
            print(f"❌ Workflow not found: {workflow_path}")
            return 1
        
        experiment_id = integration.create_experiment_for_workflow(
            workflow_path,
            args.optimization_type
        )
        print(f"\n✨ Experiment created: {experiment_id}")
    
    elif args.command == "auto-create":
        experiments = integration.create_experiments_from_opportunities(
            max_experiments=args.max,
            priority_threshold=args.priority
        )
        
        print("\n📋 Summary:")
        for exp in experiments:
            print(f"  - {exp['workflow_name']} ({exp['optimization_type']}): {exp['experiment_id']}")
    
    elif args.command == "report":
        report = integration.generate_experiment_report(
            args.experiment_id,
            output_format=args.format
        )
        print(report)
    
    elif args.command == "recommend":
        recommendations = integration.recommend_next_experiments(limit=args.limit)
        
        print(f"💡 Top {len(recommendations)} Experiment Recommendations:\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['workflow_name']} - {rec['optimization_type']}")
            print(f"   Priority: {rec['priority']} | Impact: {rec['expected_impact']}")
            print(f"   {rec['description']}")
            print()
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
