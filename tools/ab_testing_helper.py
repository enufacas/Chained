#!/usr/bin/env python3
"""
A/B Testing Integration Helper

This script helps existing workflows record samples for A/B testing experiments.
It can be called from any workflow to track performance metrics.

Usage:
    python3 ab_testing_helper.py record <experiment_id> <variant_name> \
        --metric execution_time=45.2 \
        --metric success_rate=0.95 \
        --metadata run_id=12345

Author: @engineer-master
"""

import argparse
import json
import os
import sys
from typing import Dict, Any

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))
from ab_testing_engine import ABTestingEngine


def record_sample_cli(args):
    """Record a sample from CLI arguments."""
    engine = ABTestingEngine()
    
    # Parse metrics
    metrics = {}
    for metric_str in args.metric:
        if '=' not in metric_str:
            print(f"Error: Metric must be in format name=value, got: {metric_str}")
            sys.exit(1)
        
        name, value = metric_str.split('=', 1)
        try:
            metrics[name] = float(value)
        except ValueError:
            print(f"Error: Metric value must be numeric, got: {value}")
            sys.exit(1)
    
    # Parse metadata
    metadata = {}
    if args.metadata:
        for meta_str in args.metadata:
            if '=' not in meta_str:
                print(f"Error: Metadata must be in format name=value, got: {meta_str}")
                sys.exit(1)
            
            name, value = meta_str.split('=', 1)
            metadata[name] = value
    
    try:
        engine.record_sample(
            experiment_id=args.experiment_id,
            variant_name=args.variant_name,
            metrics=metrics,
            metadata=metadata
        )
        print(f"✅ Recorded sample for experiment {args.experiment_id}, variant {args.variant_name}")
        print(f"   Metrics: {metrics}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def get_active_variant_cli(args):
    """Get the active variant for a workflow's experiment."""
    engine = ABTestingEngine()
    
    # Find active experiment for this workflow
    experiments = engine.list_experiments(
        status="active",
        workflow_name=args.workflow_name
    )
    
    if not experiments:
        # No active experiment for this workflow
        print(json.dumps({
            "has_experiment": False,
            "variant": "control",
            "message": f"No active experiment for {args.workflow_name}"
        }))
        return
    
    # For simplicity, use the first active experiment
    experiment = experiments[0]
    exp_id = experiment["id"]
    
    # Get full experiment details
    details = engine.get_experiment_details(exp_id)
    
    # Select variant (for now, round-robin based on time)
    # In production, could use more sophisticated assignment logic
    import time
    variant_names = list(details["variants"].keys())
    selected_index = int(time.time()) % len(variant_names)
    selected_variant = variant_names[selected_index]
    
    print(json.dumps({
        "has_experiment": True,
        "experiment_id": exp_id,
        "experiment_name": details["name"],
        "variant": selected_variant,
        "variant_config": details["variants"][selected_variant]["config"],
        "message": f"Using variant {selected_variant} for experiment {details['name']}"
    }))


def create_experiment_cli(args):
    """Create a new experiment from CLI arguments."""
    engine = ABTestingEngine()
    
    # Parse variants from JSON file or string
    if os.path.isfile(args.variants):
        with open(args.variants, 'r') as f:
            variants = json.load(f)
    else:
        try:
            variants = json.loads(args.variants)
        except json.JSONDecodeError:
            print(f"Error: Variants must be valid JSON file or string")
            sys.exit(1)
    
    # Parse metrics
    metrics = args.metrics.split(',') if args.metrics else []
    
    try:
        exp_id = engine.create_experiment(
            name=args.name,
            description=args.description,
            variants=variants,
            metrics=metrics,
            workflow_name=args.workflow_name if hasattr(args, 'workflow_name') else None
        )
        
        print(f"✅ Created experiment: {exp_id}")
        print(f"   Name: {args.name}")
        print(f"   Variants: {len(variants)}")
        print(f"   Metrics: {', '.join(metrics)}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def analyze_experiment_cli(args):
    """Analyze an experiment from CLI."""
    engine = ABTestingEngine()
    
    try:
        analysis = engine.analyze_experiment(args.experiment_id)
        print(json.dumps(analysis, indent=2))
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="A/B Testing Integration Helper"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Record sample command
    record_parser = subparsers.add_parser('record', help='Record a sample for an experiment')
    record_parser.add_argument('experiment_id', help='Experiment ID')
    record_parser.add_argument('variant_name', help='Variant name')
    record_parser.add_argument('--metric', action='append', required=True,
                              help='Metric in format name=value (can be specified multiple times)')
    record_parser.add_argument('--metadata', action='append',
                              help='Metadata in format name=value (can be specified multiple times)')
    
    # Get variant command
    variant_parser = subparsers.add_parser('get-variant', 
                                          help='Get active variant for a workflow')
    variant_parser.add_argument('workflow_name', help='Workflow name')
    
    # Create experiment command
    create_parser = subparsers.add_parser('create', help='Create a new experiment')
    create_parser.add_argument('name', help='Experiment name')
    create_parser.add_argument('description', help='Experiment description')
    create_parser.add_argument('variants', help='Variants JSON (file path or JSON string)')
    create_parser.add_argument('--metrics', help='Comma-separated list of metrics')
    create_parser.add_argument('--workflow-name', help='Optional workflow name')
    
    # Analyze experiment command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze an experiment')
    analyze_parser.add_argument('experiment_id', help='Experiment ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'record':
        record_sample_cli(args)
    elif args.command == 'get-variant':
        get_active_variant_cli(args)
    elif args.command == 'create':
        create_experiment_cli(args)
    elif args.command == 'analyze':
        analyze_experiment_cli(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
