#!/usr/bin/env python3
"""
Knowledge Graph Builder - Enhanced Data Collection for Intelligent Connections

Analyzes the codebase to extract:
- Code-level relationships (imports, function calls, dependencies)
- Agent-code relationships (git history analysis)
- Semantic relationships (issues, PRs, refactoring history)
"""

import ast
import json
import os
import subprocess
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime


class CodeAnalyzer:
    """Analyzes Python files to extract code relationships"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.files_analyzed = []
        
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(filepath))
            
            imports = []
            functions = []
            classes = []
            function_calls = []
            
            for node in ast.walk(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'alias': alias.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'type': 'from_import',
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname
                        })
                
                # Extract functions
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                    })
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [self._get_name(base) for base in node.bases],
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                
                # Extract function calls
                elif isinstance(node, ast.Call):
                    func_name = self._get_name(node.func)
                    if func_name:
                        function_calls.append(func_name)
            
            return {
                'filepath': str(filepath.relative_to(self.repo_path)),
                'imports': imports,
                'functions': functions,
                'classes': classes,
                'function_calls': list(set(function_calls)),
                'lines_of_code': len(content.split('\n'))
            }
        
        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}")
            return None
    
    def _get_name(self, node) -> str:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return ''
    
    def _get_decorator_name(self, node) -> str:
        """Extract decorator name"""
        return self._get_name(node)
    
    def analyze_repository(self) -> List[Dict[str, Any]]:
        """Analyze all Python files in repository"""
        results = []
        
        for py_file in self.repo_path.rglob('*.py'):
            # Skip virtual environments and build directories
            if any(part in py_file.parts for part in ['.venv', 'venv', '__pycache__', 'build', 'dist', '.git']):
                continue
            
            result = self.analyze_file(py_file)
            if result:
                results.append(result)
                self.files_analyzed.append(str(py_file.relative_to(self.repo_path)))
        
        return results


class GitAnalyzer:
    """Analyzes git history to extract agent and collaboration patterns"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def get_file_history(self, filepath: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get git history for a specific file"""
        try:
            cmd = [
                'git', '-C', str(self.repo_path), 'log',
                f'--max-count={limit}',
                '--format=%H|%an|%ae|%aI|%s',
                '--', filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
            
            return commits
        
        except Exception as e:
            print(f"Warning: Could not get git history for {filepath}: {e}")
            return []
    
    def extract_agent_from_commit(self, commit_message: str) -> str:
        """Extract agent name from commit message"""
        # Look for agent mentions in commit messages
        # All agents are inspired by legendary computer scientists
        agents = [
            'accelerate-master', 'assert-specialist', 'coach-master',
            'construct-specialist', 'create-guru', 'engineer-master', 
            'engineer-wizard', 'investigate-champion', 'meta-coordinator',
            'monitor-champion', 'organize-guru', 'secure-ninja',
            'secure-specialist', 'support-master', 'troubleshoot-expert'
        ]
        
        msg_lower = commit_message.lower()
        for agent in agents:
            if agent in msg_lower:
                return agent
        
        # Also look for @agent mentions
        import re
        match = re.search(r'@([\w-]+(?:master|specialist|champion|guru|wizard|ninja|expert|coordinator))', msg_lower)
        if match:
            agent_name = match.group(1)
            if agent_name in agents:
                return agent_name
        
        return 'unknown'
    
    def analyze_file_contributors(self, files: List[str]) -> Dict[str, Any]:
        """Analyze who worked on which files"""
        file_contributors = defaultdict(lambda: defaultdict(int))
        agent_contributions = defaultdict(set)
        
        for filepath in files:
            history = self.get_file_history(filepath)
            
            for commit in history:
                author = commit['author']
                file_contributors[filepath][author] += 1
                
                agent = self.extract_agent_from_commit(commit['message'])
                if agent != 'unknown':
                    agent_contributions[agent].add(filepath)
        
        return {
            'file_contributors': dict(file_contributors),
            'agent_contributions': {agent: list(files) for agent, files in agent_contributions.items()}
        }
    
    def find_frequently_changed_together(self, files: List[str], min_count: int = 3) -> List[Tuple[str, str, int]]:
        """Find files that frequently change together"""
        try:
            # Get all commits
            cmd = ['git', '-C', str(self.repo_path), 'log', '--format=%H', '--all']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            commits = result.stdout.strip().split('\n')[:200]  # Limit to recent commits
            
            # Track file pairs in commits
            file_pairs = defaultdict(int)
            
            for commit_hash in commits:
                if not commit_hash:
                    continue
                
                # Get files in this commit
                cmd = ['git', '-C', str(self.repo_path), 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    continue
                
                commit_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
                
                # Count pairs
                for i, f1 in enumerate(commit_files):
                    for f2 in commit_files[i+1:]:
                        pair = tuple(sorted([f1, f2]))
                        file_pairs[pair] += 1
            
            # Filter by minimum count
            frequent_pairs = [(f1, f2, count) for (f1, f2), count in file_pairs.items() if count >= min_count]
            frequent_pairs.sort(key=lambda x: x[2], reverse=True)
            
            return frequent_pairs
        
        except Exception as e:
            print(f"Warning: Could not analyze file change patterns: {e}")
            return []


class PatternAnalyzer:
    """Analyzes code patterns, quality metrics, and error patterns"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.git_analyzer = GitAnalyzer(repo_path)
    
    def analyze_error_fix_patterns(self, files: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze patterns in error fixes from git history"""
        error_patterns = defaultdict(list)
        
        for filepath in files[:20]:  # Limit to avoid long processing
            try:
                history = self.git_analyzer.get_file_history(filepath, limit=30)
                
                for commit in history:
                    msg = commit['message'].lower()
                    
                    # Detect error-related commits
                    if any(keyword in msg for keyword in ['fix', 'bug', 'error', 'issue', 'crash', 'fail']):
                        error_type = self._classify_error(msg)
                        error_patterns[filepath].append({
                            'date': commit['date'],
                            'type': error_type,
                            'message': commit['message'][:100],
                            'hash': commit['hash'][:8]
                        })
            except Exception as e:
                continue
        
        return dict(error_patterns)
    
    def _classify_error(self, commit_message: str) -> str:
        """Classify the type of error from commit message"""
        msg = commit_message.lower()
        
        if any(kw in msg for kw in ['security', 'vulnerability', 'exploit', 'injection']):
            return 'security'
        elif any(kw in msg for kw in ['performance', 'slow', 'optimize', 'speed']):
            return 'performance'
        elif any(kw in msg for kw in ['crash', 'exception', 'null', 'undefined']):
            return 'runtime_error'
        elif any(kw in msg for kw in ['syntax', 'typo', 'lint']):
            return 'syntax'
        elif any(kw in msg for kw in ['test', 'failing']):
            return 'test_failure'
        else:
            return 'general_bug'
    
    def analyze_refactoring_history(self, files: List[str]) -> Dict[str, int]:
        """Track refactoring patterns across files"""
        refactoring_counts = defaultdict(int)
        
        for filepath in files[:20]:  # Limit for performance
            try:
                history = self.git_analyzer.get_file_history(filepath, limit=30)
                
                for commit in history:
                    msg = commit['message'].lower()
                    if any(kw in msg for kw in ['refactor', 'restructure', 'reorganize', 'cleanup', 'improve']):
                        refactoring_counts[filepath] += 1
            except Exception as e:
                continue
        
        return dict(refactoring_counts)
    
    def calculate_code_complexity(self, code_analysis: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate complexity metrics for files"""
        complexity = {}
        
        for item in code_analysis:
            filepath = item['filepath']
            
            # Simple complexity metrics
            num_functions = len(item['functions'])
            num_classes = len(item['classes'])
            lines = item['lines_of_code']
            num_imports = len(item['imports'])
            
            # Complexity score (higher = more complex)
            if lines > 0:
                complexity_score = (
                    (num_functions * 2 + num_classes * 5 + num_imports) / lines * 100
                )
            else:
                complexity_score = 0
            
            complexity[filepath] = {
                'complexity_score': round(complexity_score, 2),
                'functions': num_functions,
                'classes': num_classes,
                'lines': lines,
                'avg_function_size': round(lines / num_functions, 1) if num_functions > 0 else 0
            }
        
        return complexity
    
    def identify_code_smells(self, code_analysis: List[Dict]) -> Dict[str, List[str]]:
        """Identify potential code smells"""
        smells = {}
        
        for item in code_analysis:
            filepath = item['filepath']
            file_smells = []
            
            # Large file
            if item['lines_of_code'] > 500:
                file_smells.append('large_file')
            
            # Too many functions
            if len(item['functions']) > 20:
                file_smells.append('too_many_functions')
            
            # God class (many methods)
            for cls in item['classes']:
                if len(cls.get('methods', [])) > 15:
                    file_smells.append('god_class')
                    break
            
            # Low cohesion (many imports relative to size)
            if item['lines_of_code'] > 0:
                import_ratio = len(item['imports']) / item['lines_of_code'] * 100
                if import_ratio > 10:
                    file_smells.append('high_coupling')
            
            if file_smells:
                smells[filepath] = file_smells
        
        return smells


class TestCoverageAnalyzer:
    """Analyzes test coverage and maps tests to code"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def find_test_files(self) -> List[str]:
        """Find all test files"""
        test_files = []
        for py_file in self.repo_path.rglob('*.py'):
            if py_file.name.startswith('test_') or py_file.name.endswith('_test.py'):
                test_files.append(str(py_file.relative_to(self.repo_path)))
        return test_files
    
    def map_tests_to_code(self, test_files: List[str], code_analysis: List[Dict]) -> Dict[str, List[str]]:
        """Map test files to the code they test"""
        test_mapping = {}
        
        for test_file in test_files:
            # Extract likely module name from test file
            if test_file.startswith('test_'):
                module_name = test_file[5:].replace('.py', '')
            elif test_file.endswith('_test.py'):
                module_name = test_file[:-8]
            else:
                module_name = test_file.replace('.py', '')
            
            # Find matching code files
            related_files = []
            for code_file in code_analysis:
                filepath = code_file['filepath']
                # Avoid self-references
                if filepath == test_file:
                    continue
                if module_name in filepath or filepath.replace('.py', '') in test_file:
                    related_files.append(filepath)
            
            test_mapping[test_file] = related_files
        
        return test_mapping


class KnowledgeGraphBuilder:
    """Main builder that coordinates all analysis"""
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path).resolve()
        self.code_analyzer = CodeAnalyzer(self.repo_path)
        self.git_analyzer = GitAnalyzer(self.repo_path)
        self.test_analyzer = TestCoverageAnalyzer(self.repo_path)
        self.pattern_analyzer = PatternAnalyzer(self.repo_path)
    
    def build_graph(self) -> Dict[str, Any]:
        """Build complete knowledge graph"""
        print("🔍 Analyzing codebase structure...")
        code_analysis = self.code_analyzer.analyze_repository()
        
        print("📊 Analyzing git history...")
        files = [item['filepath'] for item in code_analysis]
        contributor_analysis = self.git_analyzer.analyze_file_contributors(files)
        
        print("🔗 Finding frequently changed file pairs...")
        frequent_pairs = self.git_analyzer.find_frequently_changed_together(files)
        
        print("🧪 Mapping test coverage...")
        test_files = self.test_analyzer.find_test_files()
        test_mapping = self.test_analyzer.map_tests_to_code(test_files, code_analysis)
        
        print("🏗️ Building dependency graph...")
        dependencies = self._build_dependency_graph(code_analysis)
        
        print("🎯 Analyzing error patterns...")
        error_patterns = self.pattern_analyzer.analyze_error_fix_patterns(files)
        
        print("🔄 Tracking refactoring history...")
        refactoring_history = self.pattern_analyzer.analyze_refactoring_history(files)
        
        print("📈 Calculating complexity metrics...")
        complexity_metrics = self.pattern_analyzer.calculate_code_complexity(code_analysis)
        
        print("🔎 Identifying code smells...")
        code_smells = self.pattern_analyzer.identify_code_smells(code_analysis)
        
        print("✨ Generating relationships...")
        relationships = self._generate_relationships(
            code_analysis, dependencies, test_mapping, 
            contributor_analysis, frequent_pairs
        )
        
        # Build final graph structure
        graph = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'repo_path': str(self.repo_path),
                'total_files': len(code_analysis),
                'total_test_files': len(test_files),
                'total_relationships': len(relationships)
            },
            'nodes': self._create_nodes(code_analysis, test_files, contributor_analysis, 
                                       complexity_metrics, code_smells, refactoring_history),
            'relationships': relationships,
            'statistics': self._generate_statistics(code_analysis, relationships, contributor_analysis),
            'patterns': {
                'error_fixes': error_patterns,
                'refactorings': refactoring_history,
                'code_smells': code_smells
            },
            'metrics': {
                'complexity': complexity_metrics
            }
        }
        
        return graph
    
    def _build_dependency_graph(self, code_analysis: List[Dict]) -> Dict[str, Set[str]]:
        """Build file dependency graph based on imports"""
        dependencies = defaultdict(set)
        file_to_modules = {}
        
        # Map file paths to their module names
        for item in code_analysis:
            filepath = item['filepath']
            module_name = filepath.replace('/', '.').replace('.py', '')
            file_to_modules[module_name] = filepath
        
        # Build dependency relationships
        for item in code_analysis:
            filepath = item['filepath']
            
            for imp in item['imports']:
                module = imp.get('module', '')
                
                # Check if this is an internal import
                for internal_module, internal_path in file_to_modules.items():
                    if module.startswith(internal_module.replace('.', '/')) or module in internal_module:
                        if internal_path != filepath:
                            dependencies[filepath].add(internal_path)
        
        return {k: list(v) for k, v in dependencies.items()}
    
    def _create_nodes(self, code_analysis: List[Dict], test_files: List[str], 
                     contributor_analysis: Dict, complexity_metrics: Dict = None,
                     code_smells: Dict = None, refactoring_history: Dict = None) -> List[Dict[str, Any]]:
        """Create graph nodes"""
        nodes = []
        
        complexity_metrics = complexity_metrics or {}
        code_smells = code_smells or {}
        refactoring_history = refactoring_history or {}
        
        # File nodes
        for item in code_analysis:
            filepath = item['filepath']
            is_test = filepath in test_files
            
            # Get contributors
            contributors = list(contributor_analysis['file_contributors'].get(filepath, {}).keys())
            
            # Get complexity and quality metrics
            complexity = complexity_metrics.get(filepath, {})
            smells = code_smells.get(filepath, [])
            refactor_count = refactoring_history.get(filepath, 0)
            
            node = {
                'id': filepath,
                'type': 'test_file' if is_test else 'code_file',
                'label': Path(filepath).name,
                'filepath': filepath,
                'functions': len(item['functions']),
                'classes': len(item['classes']),
                'lines_of_code': item['lines_of_code'],
                'imports': len(item['imports']),
                'contributors': contributors[:5]  # Top 5 contributors
            }
            
            # Add complexity metrics if available
            if complexity:
                node['complexity_score'] = complexity.get('complexity_score', 0)
                node['avg_function_size'] = complexity.get('avg_function_size', 0)
            
            # Add quality indicators
            if smells:
                node['code_smells'] = smells
                node['quality_issues'] = len(smells)
            
            # Add refactoring history
            if refactor_count > 0:
                node['refactoring_count'] = refactor_count
            
            nodes.append(node)
        
        # Agent nodes
        for agent, files in contributor_analysis['agent_contributions'].items():
            if agent != 'unknown':
                nodes.append({
                    'id': f'agent:{agent}',
                    'type': 'agent',
                    'label': agent,
                    'files_worked_on': len(files),
                    'expertise': self._categorize_files(files)
                })
        
        return nodes
    
    def _categorize_files(self, files: List[str]) -> List[str]:
        """Categorize files to determine agent expertise"""
        categories = set()
        
        for filepath in files:
            if 'test' in filepath:
                categories.add('testing')
            if 'tools' in filepath:
                categories.add('tooling')
            if 'docs' in filepath or '.md' in filepath:
                categories.add('documentation')
            if 'workflow' in filepath or '.github' in filepath:
                categories.add('automation')
            if 'agent' in filepath:
                categories.add('agent-system')
        
        return list(categories) if categories else ['general']
    
    def _generate_relationships(self, code_analysis: List[Dict], 
                                dependencies: Dict[str, List[str]],
                                test_mapping: Dict[str, List[str]],
                                contributor_analysis: Dict,
                                frequent_pairs: List[Tuple[str, str, int]]) -> List[Dict[str, Any]]:
        """Generate all relationship types"""
        relationships = []
        
        # Import dependencies
        for source, targets in dependencies.items():
            for target in targets:
                relationships.append({
                    'source': source,
                    'target': target,
                    'type': 'imports',
                    'weight': 1
                })
        
        # Test coverage
        for test_file, code_files in test_mapping.items():
            for code_file in code_files:
                relationships.append({
                    'source': test_file,
                    'target': code_file,
                    'type': 'tests',
                    'weight': 1
                })
        
        # Agent contributions
        for agent, files in contributor_analysis['agent_contributions'].items():
            if agent != 'unknown':
                for filepath in files:
                    relationships.append({
                        'source': f'agent:{agent}',
                        'target': filepath,
                        'type': 'worked_on',
                        'weight': 1
                    })
        
        # Frequently changed together
        for file1, file2, count in frequent_pairs:
            relationships.append({
                'source': file1,
                'target': file2,
                'type': 'changes_with',
                'weight': count
            })
        
        return relationships
    
    def _generate_statistics(self, code_analysis: List[Dict], 
                            relationships: List[Dict],
                            contributor_analysis: Dict) -> Dict[str, Any]:
        """Generate graph statistics"""
        relationship_types = defaultdict(int)
        for rel in relationships:
            relationship_types[rel['type']] += 1
        
        return {
            'total_nodes': len(code_analysis),
            'total_relationships': len(relationships),
            'relationship_types': dict(relationship_types),
            'total_agents': len([a for a in contributor_analysis['agent_contributions'].keys() if a != 'unknown']),
            'avg_file_size': sum(item['lines_of_code'] for item in code_analysis) / len(code_analysis) if code_analysis else 0,
            'total_functions': sum(len(item['functions']) for item in code_analysis),
            'total_classes': sum(len(item['classes']) for item in code_analysis)
        }
    
    def save_graph(self, output_path: str = 'docs/data/codebase-graph.json'):
        """Build and save the knowledge graph"""
        graph = self.build_graph()
        
        output_file = self.repo_path / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2)
        
        print(f"\n✅ Knowledge graph saved to {output_path}")
        print(f"📊 Statistics:")
        stats = graph['statistics']
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
        
        return graph


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build knowledge graph from codebase')
    parser.add_argument('--repo-path', default='.', help='Path to repository')
    parser.add_argument('--output', default='docs/data/codebase-graph.json', help='Output file path')
    
    args = parser.parse_args()
    
    builder = KnowledgeGraphBuilder(args.repo_path)
    builder.save_graph(args.output)


if __name__ == '__main__':
    main()
