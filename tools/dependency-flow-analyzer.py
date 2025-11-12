#!/usr/bin/env python3
"""
Dependency & Data Flow Analyzer for Chained

An analytical tool that investigates and visualizes:
- Code dependency graphs (imports, module relationships)
- Workflow orchestration patterns (triggers, schedules, dependencies)
- Data flow paths (metrics, artifacts, secrets)
- System bottlenecks and optimization opportunities

Created by: Liskov (Ada Lovelace), Investigate Champion
Purpose: Illuminate the invisible architecture of our autonomous system
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse


@dataclass
class DependencyNode:
    """Represents a node in the dependency graph"""
    name: str
    type: str  # 'module', 'workflow', 'agent'
    dependencies: List[str]
    dependents: List[str]
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DataFlow:
    """Represents a data flow path through the system"""
    source: str
    destination: str
    data_type: str  # 'metrics', 'artifact', 'secret', 'event'
    intermediate_nodes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisReport:
    """Complete analysis report"""
    timestamp: str
    summary: Dict[str, Any]
    dependency_graph: Dict[str, DependencyNode]
    data_flows: List[DataFlow]
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'summary': self.summary,
            'dependency_graph': {k: v.to_dict() for k, v in self.dependency_graph.items()},
            'data_flows': [df.to_dict() for df in self.data_flows],
            'bottlenecks': self.bottlenecks,
            'recommendations': self.recommendations
        }


class DependencyAnalyzer:
    """
    Core dependency and data flow analysis engine.
    
    Analyzes the Chained repository to understand:
    - Python module dependencies
    - Workflow orchestration patterns
    - Data flows between components
    - Potential bottlenecks and optimization opportunities
    """
    
    def __init__(self, repo_root: Optional[str] = None):
        """Initialize analyzer with repository root"""
        self.repo_root = Path(repo_root or os.getcwd())
        self.tools_dir = self.repo_root / "tools"
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.agent_system_dir = self.repo_root / ".github" / "agent-system"
        
        # Analysis results
        self.module_graph: Dict[str, DependencyNode] = {}
        self.workflow_graph: Dict[str, DependencyNode] = {}
        self.data_flows: List[DataFlow] = []
        
    def analyze_python_dependencies(self) -> Dict[str, DependencyNode]:
        """
        Analyze Python module dependencies.
        
        Returns:
            Dictionary mapping module names to dependency nodes
        """
        print("🔍 Analyzing Python dependencies...")
        
        # Collect all Python files
        python_files = list(self.tools_dir.glob("*.py")) + list(self.repo_root.glob("test_*.py"))
        
        module_graph = {}
        import_counts = Counter()
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    tree = ast.parse(f.read())
                
                module_name = py_file.stem
                dependencies = []
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dep = alias.name.split('.')[0]
                            dependencies.append(dep)
                            import_counts[dep] += 1
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dep = node.module.split('.')[0]
                            dependencies.append(dep)
                            import_counts[dep] += 1
                
                # Count lines of code
                with open(py_file, 'r') as f:
                    lines = len([l for l in f.readlines() if l.strip() and not l.strip().startswith('#')])
                
                # Create dependency node
                module_graph[module_name] = DependencyNode(
                    name=module_name,
                    type='module',
                    dependencies=list(set(dependencies)),
                    dependents=[],  # Will be filled in next pass
                    metrics={
                        'file_path': str(py_file.relative_to(self.repo_root)),
                        'lines_of_code': lines,
                        'num_dependencies': len(set(dependencies)),
                        'import_types': list(set(dependencies))
                    }
                )
            
            except Exception as e:
                print(f"⚠️  Error analyzing {py_file.name}: {e}")
        
        # Fill in dependents (reverse dependencies)
        for module_name, node in module_graph.items():
            for dep in node.dependencies:
                dep_normalized = dep.replace('_', '-')
                if dep_normalized in module_graph:
                    module_graph[dep_normalized].dependents.append(module_name)
        
        # Add popularity metrics
        for module_name, node in module_graph.items():
            node.metrics['popularity'] = len(node.dependents)
            node.metrics['centrality'] = len(node.dependencies) + len(node.dependents)
        
        self.module_graph = module_graph
        return module_graph
    
    def analyze_workflow_orchestration(self) -> Dict[str, DependencyNode]:
        """
        Analyze workflow orchestration patterns.
        
        Returns:
            Dictionary mapping workflow names to dependency nodes
        """
        print("🔄 Analyzing workflow orchestration...")
        
        workflow_files = list(self.workflows_dir.glob("*.yml"))
        workflow_graph = {}
        
        for wf in workflow_files:
            try:
                with open(wf, 'r') as f:
                    content = f.read()
                
                wf_name = wf.stem
                
                # Extract triggers
                triggers = []
                if 'workflow_dispatch:' in content:
                    triggers.append('manual')
                if 'schedule:' in content:
                    triggers.append('schedule')
                    # Extract cron patterns
                    cron_matches = re.findall(r"cron:\s*['\"]([^'\"]+)['\"]", content)
                    if cron_matches:
                        triggers.extend(cron_matches)
                if 'issues:' in content:
                    triggers.append('issues')
                if 'pull_request:' in content:
                    triggers.append('pull_request')
                if 'push:' in content:
                    triggers.append('push')
                
                # Extract workflow dependencies
                dependencies = []
                workflow_run_matches = re.findall(r'workflows:\s*\n\s*-\s*["\']([^"\']+)["\']', content)
                dependencies.extend(workflow_run_matches)
                
                # Extract secrets used
                secrets = set(re.findall(r'secrets\.(\w+)', content))
                
                # Extract tools/scripts called
                tools_called = []
                python_script_matches = re.findall(r'python3?\s+(?:tools/)?([a-z-]+\.py)', content)
                tools_called.extend(python_script_matches)
                
                # Count job steps
                job_count = len(re.findall(r'\n\s+[a-z-]+:\s*\n\s+(?:name|runs-on):', content))
                step_count = len(re.findall(r'\n\s+-\s+name:', content))
                
                workflow_graph[wf_name] = DependencyNode(
                    name=wf_name,
                    type='workflow',
                    dependencies=dependencies + tools_called,
                    dependents=[],  # Will be filled in next pass
                    metrics={
                        'file_path': str(wf.relative_to(self.repo_root)),
                        'triggers': triggers,
                        'secrets_used': list(secrets),
                        'tools_called': tools_called,
                        'job_count': job_count,
                        'step_count': step_count
                    }
                )
            
            except Exception as e:
                print(f"⚠️  Error analyzing {wf.name}: {e}")
        
        # Fill in workflow dependents
        for wf_name, node in workflow_graph.items():
            for dep in node.dependencies:
                if dep in workflow_graph:
                    workflow_graph[dep].dependents.append(wf_name)
        
        self.workflow_graph = workflow_graph
        return workflow_graph
    
    def trace_data_flows(self) -> List[DataFlow]:
        """
        Trace data flows through the system.
        
        Identifies how data moves between:
        - Workflows -> Tools
        - Tools -> Metrics storage
        - Agents -> Registry
        """
        print("📊 Tracing data flows...")
        
        data_flows = []
        
        # Trace metrics collection flow
        metrics_collectors = ['agent-metrics-collector.py', 'creativity-metrics-analyzer.py']
        metrics_storage = '.github/agent-system/metrics'
        
        for collector in metrics_collectors:
            if collector.replace('.py', '') in self.module_graph:
                data_flows.append(DataFlow(
                    source='GitHub API',
                    destination=collector,
                    data_type='metrics',
                    intermediate_nodes=['github_integration.py']
                ))
                
                data_flows.append(DataFlow(
                    source=collector,
                    destination=metrics_storage,
                    data_type='metrics',
                    intermediate_nodes=[]
                ))
        
        # Trace workflow -> tool flows
        for wf_name, wf_node in self.workflow_graph.items():
            for tool in wf_node.metrics.get('tools_called', []):
                data_flows.append(DataFlow(
                    source=wf_name,
                    destination=tool,
                    data_type='event',
                    intermediate_nodes=[]
                ))
        
        # Trace secret flows
        secret_users = defaultdict(list)
        for wf_name, wf_node in self.workflow_graph.items():
            for secret in wf_node.metrics.get('secrets_used', []):
                secret_users[secret].append(wf_name)
        
        for secret, workflows in secret_users.items():
            if len(workflows) > 1:
                data_flows.append(DataFlow(
                    source='GitHub Secrets',
                    destination=f"secret:{secret}",
                    data_type='secret',
                    intermediate_nodes=workflows
                ))
        
        self.data_flows = data_flows
        return data_flows
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Identify potential bottlenecks and issues.
        
        Looks for:
        - High-dependency modules (many dependents)
        - Complex workflows (many steps/tools)
        - Missing error handling
        - Circular dependencies
        """
        print("🎯 Identifying bottlenecks...")
        
        bottlenecks = []
        
        # Check for high-dependency modules
        high_dep_modules = [
            (name, node) for name, node in self.module_graph.items()
            if len(node.dependents) >= 4
        ]
        
        for name, node in sorted(high_dep_modules, key=lambda x: len(x[1].dependents), reverse=True):
            bottlenecks.append({
                'type': 'high_dependency_module',
                'severity': 'medium' if len(node.dependents) < 6 else 'high',
                'component': name,
                'description': f"Module '{name}' is used by {len(node.dependents)} other modules",
                'impact': 'Changes to this module could affect many components',
                'dependents': node.dependents
            })
        
        # Check for complex workflows
        complex_workflows = [
            (name, node) for name, node in self.workflow_graph.items()
            if node.metrics.get('step_count', 0) >= 10
        ]
        
        for name, node in sorted(complex_workflows, key=lambda x: x[1].metrics.get('step_count', 0), reverse=True):
            bottlenecks.append({
                'type': 'complex_workflow',
                'severity': 'low',
                'component': name,
                'description': f"Workflow '{name}' has {node.metrics['step_count']} steps",
                'impact': 'May be slow to execute or difficult to maintain',
                'metrics': {'steps': node.metrics['step_count'], 'jobs': node.metrics['job_count']}
            })
        
        # Check for potential circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_name: str, graph: Dict[str, DependencyNode]) -> Optional[List[str]]:
            """DFS to detect cycles"""
            visited.add(node_name)
            rec_stack.add(node_name)
            
            if node_name in graph:
                for dep in graph[node_name].dependencies:
                    if dep not in visited:
                        cycle = has_cycle(dep, graph)
                        if cycle:
                            return [node_name] + cycle
                    elif dep in rec_stack:
                        return [node_name, dep]
            
            rec_stack.remove(node_name)
            return None
        
        for node_name in self.module_graph:
            if node_name not in visited:
                cycle = has_cycle(node_name, self.module_graph)
                if cycle:
                    bottlenecks.append({
                        'type': 'circular_dependency',
                        'severity': 'high',
                        'component': ' -> '.join(cycle),
                        'description': 'Circular dependency detected',
                        'impact': 'Can cause import errors and make code harder to maintain',
                        'cycle': cycle
                    })
        
        return bottlenecks
    
    def generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """
        Generate actionable recommendations based on analysis.
        """
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # High-level architecture recommendations
        high_dep_count = len([b for b in bottlenecks if b['type'] == 'high_dependency_module'])
        if high_dep_count > 0:
            recommendations.append(
                f"🔧 Consider refactoring {high_dep_count} high-dependency modules to reduce coupling. "
                "Extract common interfaces or use dependency injection patterns."
            )
        
        # Workflow optimization
        complex_wf_count = len([b for b in bottlenecks if b['type'] == 'complex_workflow'])
        if complex_wf_count > 3:
            recommendations.append(
                f"⚡ {complex_wf_count} workflows have high complexity. Consider breaking them into "
                "smaller, reusable workflow components or composite actions."
            )
        
        # Circular dependency warnings
        circular_count = len([b for b in bottlenecks if b['type'] == 'circular_dependency'])
        if circular_count > 0:
            recommendations.append(
                f"❗ CRITICAL: {circular_count} circular dependencies detected. "
                "These should be resolved immediately to prevent import failures."
            )
        
        # Module-specific recommendations
        github_integration_node = self.module_graph.get('github_integration')
        if github_integration_node and len(github_integration_node.dependents) >= 4:
            recommendations.append(
                "📚 'github_integration' is a critical shared module. Consider adding "
                "comprehensive integration tests and documentation."
            )
        
        # Workflow trigger optimization
        scheduled_count = len([
            wf for wf in self.workflow_graph.values()
            if 'schedule' in wf.metrics.get('triggers', [])
        ])
        if scheduled_count > 10:
            recommendations.append(
                f"⏰ {scheduled_count} workflows run on schedules. Review cron patterns to "
                "avoid resource conflicts and ensure optimal timing."
            )
        
        # Data flow recommendations
        if len(self.data_flows) > 50:
            recommendations.append(
                "🌊 Complex data flow patterns detected. Consider documenting data flow "
                "diagrams and adding data validation at key boundaries."
            )
        
        # Agent system recommendations
        if (self.agent_system_dir / 'registry.json').exists():
            recommendations.append(
                "🤖 Agent system detected. Consider implementing agent performance "
                "dashboards and automated health checks."
            )
        
        return recommendations
    
    def run_full_analysis(self) -> AnalysisReport:
        """
        Run complete dependency and data flow analysis.
        
        Returns:
            Complete analysis report with findings and recommendations
        """
        print("=" * 80)
        print("🔬 DEPENDENCY & DATA FLOW ANALYSIS")
        print("=" * 80)
        print()
        
        # Run all analyses
        module_graph = self.analyze_python_dependencies()
        workflow_graph = self.analyze_workflow_orchestration()
        data_flows = self.trace_data_flows()
        bottlenecks = self.identify_bottlenecks()
        recommendations = self.generate_recommendations(bottlenecks)
        
        # Generate summary statistics
        summary = {
            'modules': {
                'total': len(module_graph),
                'with_dependencies': len([m for m in module_graph.values() if m.dependencies]),
                'with_dependents': len([m for m in module_graph.values() if m.dependents]),
                'avg_dependencies': sum(len(m.dependencies) for m in module_graph.values()) / len(module_graph) if module_graph else 0,
                'avg_lines': sum(m.metrics.get('lines_of_code', 0) for m in module_graph.values()) / len(module_graph) if module_graph else 0
            },
            'workflows': {
                'total': len(workflow_graph),
                'scheduled': len([w for w in workflow_graph.values() if 'schedule' in w.metrics.get('triggers', [])]),
                'manual': len([w for w in workflow_graph.values() if 'manual' in w.metrics.get('triggers', [])]),
                'event_triggered': len([w for w in workflow_graph.values() if any(t in w.metrics.get('triggers', []) for t in ['issues', 'pull_request', 'push'])]),
                'avg_steps': sum(w.metrics.get('step_count', 0) for w in workflow_graph.values()) / len(workflow_graph) if workflow_graph else 0
            },
            'data_flows': {
                'total': len(data_flows),
                'by_type': dict(Counter(df.data_type for df in data_flows))
            },
            'bottlenecks': {
                'total': len(bottlenecks),
                'by_severity': dict(Counter(b['severity'] for b in bottlenecks)),
                'by_type': dict(Counter(b['type'] for b in bottlenecks))
            }
        }
        
        # Create report
        report = AnalysisReport(
            timestamp=datetime.now().isoformat(),
            summary=summary,
            dependency_graph={**module_graph, **workflow_graph},
            data_flows=data_flows,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
        
        return report
    
    def print_report(self, report: AnalysisReport, verbose: bool = False):
        """Print analysis report to console"""
        print()
        print("=" * 80)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 80)
        
        # Module statistics
        print("\n🐍 Python Modules:")
        print(f"  Total modules:         {report.summary['modules']['total']}")
        print(f"  Avg dependencies:      {report.summary['modules']['avg_dependencies']:.1f}")
        print(f"  Avg lines of code:     {report.summary['modules']['avg_lines']:.0f}")
        
        # Workflow statistics
        print("\n⚙️  Workflows:")
        print(f"  Total workflows:       {report.summary['workflows']['total']}")
        print(f"  Scheduled:             {report.summary['workflows']['scheduled']}")
        print(f"  Manual dispatch:       {report.summary['workflows']['manual']}")
        print(f"  Event triggered:       {report.summary['workflows']['event_triggered']}")
        print(f"  Avg steps per workflow:{report.summary['workflows']['avg_steps']:.1f}")
        
        # Data flows
        print("\n🌊 Data Flows:")
        print(f"  Total flows:           {report.summary['data_flows']['total']}")
        for flow_type, count in report.summary['data_flows']['by_type'].items():
            print(f"    {flow_type:20s} {count}")
        
        # Bottlenecks
        print("\n⚠️  Bottlenecks:")
        print(f"  Total identified:      {report.summary['bottlenecks']['total']}")
        if report.summary['bottlenecks']['by_severity']:
            print("  By severity:")
            for severity, count in sorted(report.summary['bottlenecks']['by_severity'].items()):
                print(f"    {severity:20s} {count}")
        
        # Top bottlenecks
        if report.bottlenecks:
            print("\n  Top Issues:")
            for bottleneck in report.bottlenecks[:5]:
                severity_icon = '🔴' if bottleneck['severity'] == 'high' else '🟡' if bottleneck['severity'] == 'medium' else '🟢'
                print(f"    {severity_icon} {bottleneck['description']}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("=" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"\n{i}. {rec}")
        
        # Detailed bottlenecks in verbose mode
        if verbose and report.bottlenecks:
            print("\n" + "=" * 80)
            print("🔍 DETAILED BOTTLENECK ANALYSIS")
            print("=" * 80)
            for bottleneck in report.bottlenecks:
                print(f"\n{bottleneck['type'].upper()} - {bottleneck['severity']}")
                print(f"Component: {bottleneck['component']}")
                print(f"Description: {bottleneck['description']}")
                print(f"Impact: {bottleneck['impact']}")
                if 'dependents' in bottleneck:
                    print(f"Dependents: {', '.join(bottleneck['dependents'][:5])}")
                    if len(bottleneck['dependents']) > 5:
                        print(f"  ... and {len(bottleneck['dependents']) - 5} more")
        
        print("\n" + "=" * 80)
        print(f"✅ Analysis complete at {report.timestamp}")
        print("=" * 80)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Dependency & Data Flow Analyzer for Chained',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--repo',
        default='.',
        help='Repository root directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output JSON report to file'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output with detailed bottleneck analysis'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'both'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = DependencyAnalyzer(args.repo)
    
    # Run analysis
    report = analyzer.run_full_analysis()
    
    # Output results
    if args.format in ['text', 'both']:
        analyzer.print_report(report, verbose=args.verbose)
    
    if args.format in ['json', 'both'] or args.output:
        output_file = args.output or 'dependency-analysis-report.json'
        with open(output_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n📄 JSON report saved to: {output_file}")


if __name__ == '__main__':
    main()
