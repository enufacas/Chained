#!/usr/bin/env python3
"""
Helper script for autonomous refactoring workflow.
Parses refactoring report JSON and extracts key metrics.

Usage:
    python3 tools/parse-refactoring-report.py analysis/refactoring_report.json [metric]

Metrics:
    high_priority  - Number of high priority files
    total_files    - Total files analyzed
    total_suggestions - Total refactoring suggestions
"""

import sys
import json
import os


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse-refactoring-report.py <report-file> [metric]", file=sys.stderr)
        sys.exit(1)
    
    report_file = sys.argv[1]
    metric = sys.argv[2] if len(sys.argv) > 2 else "high_priority"
    
    if not os.path.exists(report_file):
        print(f"0")  # Return 0 if file doesn't exist
        sys.exit(0)
    
    try:
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        if metric == "high_priority":
            print(len(report.get('high_priority_files', [])))
        elif metric == "total_files":
            print(report.get('files_analyzed', 0))
        elif metric == "total_suggestions":
            print(report.get('total_suggestions', 0))
        else:
            print(f"Unknown metric: {metric}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error parsing report: {e}", file=sys.stderr)
        print("0")  # Return 0 on error
        sys.exit(0)


if __name__ == "__main__":
    main()
