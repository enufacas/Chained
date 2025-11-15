#!/usr/bin/env python3
"""
GitHub Actions Pattern Analyzer

Analyzes repository patterns to detect common workflow needs and opportunities
for automation. Part of the Chained autonomous AI ecosystem.

Created by @engineer-master - Systematic analysis of repository patterns.
"""

import os
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime, timezone


class ActionsPatternAnalyzer:
    """
    Analyzes repository to detect patterns that could benefit from
    custom GitHub Actions.
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.patterns = defaultdict(list)
        self.file_types = Counter()
        self.existing_workflows = []
        self.common_operations = defaultdict(int)
        
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive pattern analysis.
        
        Returns:
            Dictionary containing detected patterns and recommendations.
        """
        print("🔍 Starting repository pattern analysis...")
        
        # Analyze repository structure
        self._analyze_file_structure()
        
        # Analyze existing workflows
        self._analyze_existing_workflows()
        
        # Detect repeated operations
        self._detect_repeated_operations()
        
        # Identify testing patterns
        self._analyze_testing_patterns()
        
        # Check for deployment patterns
        self._analyze_deployment_patterns()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo_path": str(self.repo_path),
            "file_statistics": dict(self.file_types),
            "existing_workflows_count": len(self.existing_workflows),
            "patterns_detected": len(self.patterns),
            "patterns": dict(self.patterns),
            "recommendations": recommendations,
            "common_operations": dict(self.common_operations)
        }
        
        print(f"✅ Analysis complete. Detected {len(self.patterns)} patterns.")
        return results
    
    def _analyze_file_structure(self):
        """Analyze repository file structure and types."""
        print("  📁 Analyzing file structure...")
        
        # Ignore common directories
        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 
                      'venv', 'env', '.venv', 'dist', 'build', '.next'}
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                # Skip ignored directories
                if any(ignored in file_path.parts for ignored in ignore_dirs):
                    continue
                    
                # Count file types
                suffix = file_path.suffix.lower()
                if suffix:
                    self.file_types[suffix] += 1
                    
                # Detect specific patterns
                if suffix == '.py':
                    self._analyze_python_file(file_path)
                elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    self._analyze_javascript_file(file_path)
                elif suffix in ['.yml', '.yaml']:
                    if '.github/workflows' in str(file_path):
                        self._analyze_workflow_file(file_path)
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze Python files for patterns."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for testing frameworks
            if 'import pytest' in content or 'import unittest' in content:
                self.patterns['testing_frameworks'].append({
                    'file': str(file_path),
                    'framework': 'pytest' if 'pytest' in content else 'unittest'
                })
                
            # Check for dependency management
            if 'requirements.txt' in str(file_path.parent):
                self.patterns['python_dependencies'].append(str(file_path))
                
            # Check for common operations
            if 're.compile' in content or 'import re' in content:
                self.common_operations['regex_operations'] += 1
            if 'requests.' in content or 'import requests' in content:
                self.common_operations['http_requests'] += 1
            if 'json.load' in content or 'json.dump' in content:
                self.common_operations['json_operations'] += 1
                
        except Exception as e:
            # Silently skip problematic files
            pass
    
    def _analyze_javascript_file(self, file_path: Path):
        """Analyze JavaScript/TypeScript files for patterns."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for testing frameworks
            if 'jest' in content or 'describe(' in content:
                self.patterns['testing_frameworks'].append({
                    'file': str(file_path),
                    'framework': 'jest'
                })
            
            # Check for build tools
            if 'webpack' in content:
                self.patterns['build_tools'].append('webpack')
            if 'rollup' in content:
                self.patterns['build_tools'].append('rollup')
                
        except Exception:
            pass
    
    def _analyze_workflow_file(self, file_path: Path):
        """Analyze existing workflow files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            workflow_data = yaml.safe_load(content)
            
            if workflow_data:
                self.existing_workflows.append({
                    'name': workflow_data.get('name', file_path.name),
                    'file': str(file_path),
                    'triggers': list(workflow_data.get('on', {}).keys()),
                    'jobs_count': len(workflow_data.get('jobs', {}))
                })
                
                # Analyze job steps for patterns
                jobs = workflow_data.get('jobs', {})
                for job_name, job_data in jobs.items():
                    steps = job_data.get('steps', [])
                    for step in steps:
                        # Track common operations
                        if 'uses' in step:
                            action_name = step['uses'].split('@')[0]
                            self.common_operations[f'action:{action_name}'] += 1
                        if 'run' in step:
                            run_cmd = step['run']
                            if 'python' in run_cmd:
                                self.common_operations['python_scripts'] += 1
                            if 'npm' in run_cmd or 'yarn' in run_cmd:
                                self.common_operations['npm_commands'] += 1
                            if 'gh ' in run_cmd or 'git ' in run_cmd:
                                self.common_operations['git_operations'] += 1
                                
        except Exception as e:
            print(f"  ⚠️  Could not parse workflow {file_path}: {e}")
    
    def _analyze_existing_workflows(self):
        """Analyze patterns in existing workflows."""
        print("  🔄 Analyzing existing workflows...")
        
        workflows_dir = self.repo_path / '.github' / 'workflows'
        if not workflows_dir.exists():
            return
            
        # Already analyzed in _analyze_file_structure
        # Just summarize findings
        if self.existing_workflows:
            trigger_types = defaultdict(int)
            for wf in self.existing_workflows:
                for trigger in wf['triggers']:
                    trigger_types[trigger] += 1
                    
            self.patterns['workflow_triggers'] = dict(trigger_types)
    
    def _detect_repeated_operations(self):
        """Detect repeated operations that could be abstracted."""
        print("  🔁 Detecting repeated operations...")
        
        # Find operations that appear frequently
        threshold = 3  # Appears in at least 3 workflows
        repeated = {
            op: count for op, count in self.common_operations.items()
            if count >= threshold
        }
        
        if repeated:
            self.patterns['repeated_operations'] = repeated
    
    def _analyze_testing_patterns(self):
        """Analyze testing patterns in the repository."""
        print("  🧪 Analyzing testing patterns...")
        
        # Check for test directories
        test_dirs = []
        for test_path in ['tests', 'test', '__tests__', 'spec']:
            test_dir = self.repo_path / test_path
            if test_dir.exists() and test_dir.is_dir():
                test_dirs.append(str(test_dir))
                
        if test_dirs:
            self.patterns['test_directories'] = test_dirs
            
        # Check for test files
        test_files = []
        for pattern in ['test_*.py', '*_test.py', '*.test.js', '*.spec.js']:
            test_files.extend(self.repo_path.rglob(pattern))
            
        if test_files:
            self.patterns['test_files_count'] = len(test_files)
    
    def _analyze_deployment_patterns(self):
        """Analyze deployment patterns."""
        print("  🚀 Analyzing deployment patterns...")
        
        # Check for common deployment files
        deployment_indicators = {
            'Dockerfile': 'docker',
            'docker-compose.yml': 'docker-compose',
            'vercel.json': 'vercel',
            'netlify.toml': 'netlify',
            'package.json': 'npm',
            'requirements.txt': 'pip',
            'Gemfile': 'ruby',
            'go.mod': 'go'
        }
        
        found_deployments = []
        for filename, deployment_type in deployment_indicators.items():
            if (self.repo_path / filename).exists():
                found_deployments.append(deployment_type)
                
        if found_deployments:
            self.patterns['deployment_types'] = found_deployments
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for custom GitHub Actions."""
        print("  💡 Generating recommendations...")
        
        recommendations = []
        
        # Recommend based on repeated operations
        if 'repeated_operations' in self.patterns:
            for op, count in self.patterns['repeated_operations'].items():
                if op.startswith('action:'):
                    continue  # Skip existing actions
                    
                recommendations.append({
                    'priority': 'high' if count > 5 else 'medium',
                    'title': f'Abstract repeated {op} operation',
                    'description': f'The operation "{op}" appears {count} times. Consider creating a reusable action.',
                    'pattern': op,
                    'occurrences': count,
                    'action_type': 'composite'
                })
        
        # Recommend testing automation
        if 'test_files_count' in self.patterns:
            test_count = self.patterns['test_files_count']
            if test_count > 10:
                recommendations.append({
                    'priority': 'high',
                    'title': 'Automated testing action',
                    'description': f'Found {test_count} test files. Create a comprehensive testing action.',
                    'pattern': 'testing',
                    'action_type': 'composite'
                })
        
        # Recommend deployment automation
        if 'deployment_types' in self.patterns:
            for deploy_type in self.patterns['deployment_types']:
                recommendations.append({
                    'priority': 'medium',
                    'title': f'Deployment action for {deploy_type}',
                    'description': f'Automate {deploy_type} deployment process.',
                    'pattern': f'deployment_{deploy_type}',
                    'action_type': 'composite'
                })
        
        # Recommend pattern-specific actions
        if self.file_types.get('.py', 0) > 20:
            recommendations.append({
                'priority': 'high',
                'title': 'Python project automation',
                'description': 'Create actions for Python linting, testing, and packaging.',
                'pattern': 'python_automation',
                'action_type': 'composite'
            })
        
        if self.file_types.get('.js', 0) + self.file_types.get('.ts', 0) > 20:
            recommendations.append({
                'priority': 'high',
                'title': 'JavaScript/TypeScript automation',
                'description': 'Create actions for JS/TS building, testing, and deployment.',
                'pattern': 'javascript_automation',
                'action_type': 'composite'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    def save_analysis(self, output_path: str = "analysis/actions-patterns.json"):
        """Save analysis results to file."""
        results = self.analyze()
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Analysis saved to {output_path}")
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze repository patterns for GitHub Actions generation'
    )
    parser.add_argument(
        '--repo-path',
        default='.',
        help='Path to repository (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='analysis/actions-patterns.json',
        help='Output file path (default: analysis/actions-patterns.json)'
    )
    
    args = parser.parse_args()
    
    analyzer = ActionsPatternAnalyzer(args.repo_path)
    results = analyzer.save_analysis(args.output)
    
    print("\n📊 Analysis Summary:")
    print(f"  Total file types: {len(results['file_statistics'])}")
    print(f"  Existing workflows: {results['existing_workflows_count']}")
    print(f"  Patterns detected: {results['patterns_detected']}")
    print(f"  Recommendations: {len(results['recommendations'])}")
    
    if results['recommendations']:
        print("\n🎯 Top Recommendations:")
        for i, rec in enumerate(results['recommendations'][:5], 1):
            print(f"  {i}. [{rec['priority'].upper()}] {rec['title']}")
            print(f"     {rec['description']}")


if __name__ == '__main__':
    main()
