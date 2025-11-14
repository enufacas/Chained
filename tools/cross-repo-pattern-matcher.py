#!/usr/bin/env python3
"""
Cross-Repository Pattern Matcher for Best Practices

An analytical tool by @investigate-champion that identifies, scores, and tracks
best practices across repositories. Inspired by Ada Lovelace's analytical rigor
combined with modern pattern recognition.

Features:
- Multi-repository pattern analysis
- Extensible pattern library
- Best practice scoring and recommendations
- Integration with existing analyzer tools
- Cross-reference with learnings book

Created by: @investigate-champion (Ada Lovelace)
Purpose: Illuminate best practices across repositories and drive continuous improvement
"""

import os
import sys
import json
import re
import ast
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
from abc import ABC, abstractmethod
import argparse


@dataclass
class Pattern:
    """Represents a single pattern to match"""
    id: str
    name: str
    category: str  # 'code', 'workflow', 'documentation', 'security', 'architecture'
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    type: str  # 'good_practice', 'anti_pattern', 'improvement_opportunity'
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PatternMatch:
    """Represents a matched pattern instance"""
    pattern_id: str
    pattern_name: str
    category: str
    file_path: str
    line_number: int
    matched_content: str
    context: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RepositoryAnalysis:
    """Complete repository analysis results"""
    repository_name: str
    timestamp: str
    patterns_matched: List[PatternMatch]
    summary: Dict[str, Any]
    recommendations: List[str]
    score: float  # Overall best practices score 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'repository_name': self.repository_name,
            'timestamp': self.timestamp,
            'patterns_matched': [pm.to_dict() for pm in self.patterns_matched],
            'summary': self.summary,
            'recommendations': self.recommendations,
            'score': self.score
        }


class PatternDetector(ABC):
    """Abstract base class for pattern detectors"""
    
    @abstractmethod
    def detect(self, file_path: Path, content: str) -> List[PatternMatch]:
        """Detect patterns in the given file content"""
        pass
    
    @abstractmethod
    def get_patterns(self) -> List[Pattern]:
        """Get the list of patterns this detector handles"""
        pass


class CodePatternDetector(PatternDetector):
    """Detects code patterns in Python files"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[Pattern]:
        """Initialize code patterns to detect"""
        return [
            Pattern(
                id='CP001',
                name='Type Hints Present',
                category='code',
                description='Functions have type hints for parameters and return values',
                severity='medium',
                type='good_practice',
                tags=['python', 'type-safety', 'maintainability'],
                examples=['def process(data: Dict[str, Any]) -> bool:']
            ),
            Pattern(
                id='CP002',
                name='Comprehensive Docstrings',
                category='code',
                description='Functions have detailed docstrings with descriptions',
                severity='medium',
                type='good_practice',
                tags=['python', 'documentation', 'clarity'],
                examples=['"""Process data with error handling"""']
            ),
            Pattern(
                id='CP003',
                name='Error Handling',
                category='code',
                description='Code includes proper try/except blocks',
                severity='high',
                type='good_practice',
                tags=['python', 'reliability', 'error-handling'],
                examples=['try:\n    process()\nexcept Exception as e:\n    handle(e)']
            ),
            Pattern(
                id='CP004',
                name='Long Functions',
                category='code',
                description='Function exceeds 50 lines (consider refactoring)',
                severity='low',
                type='anti_pattern',
                tags=['python', 'complexity', 'maintainability'],
                examples=['def long_function():\n    # 60+ lines of code']
            ),
            Pattern(
                id='CP005',
                name='Magic Numbers',
                category='code',
                description='Numeric literals without named constants',
                severity='low',
                type='anti_pattern',
                tags=['python', 'maintainability', 'clarity'],
                examples=['if count > 42:  # What is 42?']
            ),
            Pattern(
                id='CP006',
                name='Deep Nesting',
                category='code',
                description='Code has excessive nesting depth (>4 levels)',
                severity='medium',
                type='anti_pattern',
                tags=['python', 'complexity', 'readability'],
                examples=['if a:\n    if b:\n        if c:\n            if d:\n                if e:']
            ),
            Pattern(
                id='CP007',
                name='Dataclass Usage',
                category='code',
                description='Uses dataclasses for structured data',
                severity='info',
                type='good_practice',
                tags=['python', 'structure', 'modern'],
                examples=['@dataclass\nclass Config:']
            ),
            Pattern(
                id='CP008',
                name='Context Managers',
                category='code',
                description='Uses context managers for resource management',
                severity='medium',
                type='good_practice',
                tags=['python', 'resources', 'safety'],
                examples=['with open(file) as f:']
            ),
        ]
    
    def detect(self, file_path: Path, content: str) -> List[PatternMatch]:
        """Detect code patterns in Python files"""
        matches = []
        
        if not file_path.suffix == '.py':
            return matches
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Detect patterns by walking the AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    matches.extend(self._check_function(node, file_path, lines))
                elif isinstance(node, ast.ClassDef):
                    matches.extend(self._check_class(node, file_path, lines))
                elif isinstance(node, ast.With):
                    matches.append(self._create_match(
                        'CP008', file_path, node.lineno,
                        lines[node.lineno - 1] if node.lineno <= len(lines) else '',
                        'Uses with statement for resource management',
                        0.9
                    ))
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        except Exception as e:
            print(f"Warning: Error analyzing {file_path}: {e}", file=sys.stderr)
        
        return matches
    
    def _check_function(self, node: ast.FunctionDef, file_path: Path, lines: List[str]) -> List[PatternMatch]:
        """Check function-level patterns"""
        matches = []
        
        # Check for type hints
        has_type_hints = (
            node.returns is not None or
            any(arg.annotation is not None for arg in node.args.args)
        )
        if has_type_hints:
            matches.append(self._create_match(
                'CP001', file_path, node.lineno,
                lines[node.lineno - 1] if node.lineno <= len(lines) else '',
                f'Function {node.name} has type hints',
                0.95
            ))
        
        # Check for docstring
        docstring = ast.get_docstring(node)
        if docstring and len(docstring) > 20:
            matches.append(self._create_match(
                'CP002', file_path, node.lineno,
                docstring[:100],
                f'Function {node.name} has comprehensive docstring',
                0.9
            ))
        
        # Check for error handling
        has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
        if has_try:
            matches.append(self._create_match(
                'CP003', file_path, node.lineno,
                f'Function {node.name}',
                'Includes error handling',
                0.85
            ))
        
        # Check function length
        if hasattr(node, 'end_lineno'):
            func_lines = node.end_lineno - node.lineno
            if func_lines > 50:
                matches.append(self._create_match(
                    'CP004', file_path, node.lineno,
                    f'Function {node.name} ({func_lines} lines)',
                    f'Consider refactoring - function is {func_lines} lines long',
                    0.8,
                    {'lines': func_lines}
                ))
        
        # Check nesting depth
        max_depth = self._get_max_depth(node)
        if max_depth > 4:
            matches.append(self._create_match(
                'CP006', file_path, node.lineno,
                f'Function {node.name}',
                f'Deep nesting detected (depth: {max_depth})',
                0.85,
                {'depth': max_depth}
            ))
        
        return matches
    
    def _check_class(self, node: ast.ClassDef, file_path: Path, lines: List[str]) -> List[PatternMatch]:
        """Check class-level patterns"""
        matches = []
        
        # Check for dataclass decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
                matches.append(self._create_match(
                    'CP007', file_path, node.lineno,
                    lines[node.lineno - 1] if node.lineno <= len(lines) else '',
                    f'Class {node.name} uses dataclass',
                    0.9
                ))
        
        return matches
    
    def _get_max_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_max_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _create_match(
        self,
        pattern_id: str,
        file_path: Path,
        line_number: int,
        content: str,
        context: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PatternMatch:
        """Helper to create PatternMatch object"""
        pattern = next(p for p in self.patterns if p.id == pattern_id)
        return PatternMatch(
            pattern_id=pattern_id,
            pattern_name=pattern.name,
            category=pattern.category,
            file_path=str(file_path),
            line_number=line_number,
            matched_content=content,
            context=context,
            confidence=confidence,
            metadata=metadata or {}
        )
    
    def get_patterns(self) -> List[Pattern]:
        """Get all code patterns"""
        return self.patterns


class WorkflowPatternDetector(PatternDetector):
    """Detects patterns in GitHub Actions workflow files"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[Pattern]:
        """Initialize workflow patterns"""
        return [
            Pattern(
                id='WF001',
                name='Error Handling in Workflows',
                category='workflow',
                description='Workflow steps include error handling with continue-on-error or if conditions',
                severity='high',
                type='good_practice',
                tags=['github-actions', 'reliability', 'error-handling'],
                examples=['continue-on-error: true', 'if: failure()']
            ),
            Pattern(
                id='WF002',
                name='Secrets Management',
                category='workflow',
                description='Secrets are properly referenced with ${{ secrets.* }}',
                severity='critical',
                type='good_practice',
                tags=['github-actions', 'security', 'secrets'],
                examples=['${{ secrets.GITHUB_TOKEN }}']
            ),
            Pattern(
                id='WF003',
                name='Pinned Action Versions',
                category='workflow',
                description='Actions use pinned versions instead of @main or @master',
                severity='medium',
                type='good_practice',
                tags=['github-actions', 'stability', 'reproducibility'],
                examples=['uses: actions/checkout@v4']
            ),
            Pattern(
                id='WF004',
                name='Workflow Documentation',
                category='workflow',
                description='Workflow includes name and description comments',
                severity='low',
                type='good_practice',
                tags=['github-actions', 'documentation', 'clarity'],
                examples=['name: Deploy Application\n# Deploys to production']
            ),
            Pattern(
                id='WF005',
                name='Timeout Configuration',
                category='workflow',
                description='Jobs have timeout-minutes configured',
                severity='medium',
                type='good_practice',
                tags=['github-actions', 'reliability', 'resources'],
                examples=['timeout-minutes: 30']
            ),
            Pattern(
                id='WF006',
                name='Unpinned Action Version',
                category='workflow',
                description='Action uses @main or @master (unstable)',
                severity='medium',
                type='anti_pattern',
                tags=['github-actions', 'stability', 'risk'],
                examples=['uses: some/action@main']
            ),
            Pattern(
                id='WF007',
                name='Hardcoded Credentials',
                category='workflow',
                description='Potential hardcoded credentials or tokens detected',
                severity='critical',
                type='anti_pattern',
                tags=['github-actions', 'security', 'credentials'],
                examples=['password: "secret123"']
            ),
            Pattern(
                id='WF008',
                name='Reusable Workflow',
                category='workflow',
                description='Uses workflow_call for reusability',
                severity='info',
                type='good_practice',
                tags=['github-actions', 'reusability', 'maintainability'],
                examples=['on:\n  workflow_call:']
            ),
        ]
    
    def detect(self, file_path: Path, content: str) -> List[PatternMatch]:
        """Detect workflow patterns"""
        matches = []
        
        if not file_path.suffix in ['.yml', '.yaml']:
            return matches
        
        if '.github/workflows' not in str(file_path):
            return matches
        
        try:
            data = yaml.safe_load(content)
            lines = content.split('\n')
            
            # Check for workflow-level patterns
            matches.extend(self._check_workflow_structure(data, file_path, lines))
            
            # Check for job-level patterns
            if isinstance(data, dict) and 'jobs' in data:
                for job_name, job_data in data['jobs'].items():
                    matches.extend(self._check_job_patterns(
                        job_name, job_data, file_path, lines
                    ))
        
        except yaml.YAMLError:
            pass  # Skip invalid YAML
        except Exception as e:
            print(f"Warning: Error analyzing workflow {file_path}: {e}", file=sys.stderr)
        
        return matches
    
    def _check_workflow_structure(
        self,
        data: Dict,
        file_path: Path,
        lines: List[str]
    ) -> List[PatternMatch]:
        """Check workflow-level patterns"""
        matches = []
        
        # Check for workflow name
        if 'name' in data:
            matches.append(self._create_match(
                'WF004', file_path, 1,
                f"name: {data['name']}",
                'Workflow has descriptive name',
                0.9
            ))
        
        # Check for reusable workflow
        if isinstance(data.get('on'), dict) and 'workflow_call' in data['on']:
            matches.append(self._create_match(
                'WF008', file_path, 1,
                'workflow_call',
                'Workflow is reusable',
                0.95
            ))
        
        return matches
    
    def _check_job_patterns(
        self,
        job_name: str,
        job_data: Dict,
        file_path: Path,
        lines: List[str]
    ) -> List[PatternMatch]:
        """Check job-level patterns"""
        matches = []
        
        # Check for timeout
        if 'timeout-minutes' in job_data:
            matches.append(self._create_match(
                'WF005', file_path, 1,
                f'timeout-minutes: {job_data["timeout-minutes"]}',
                f'Job {job_name} has timeout configured',
                0.85
            ))
        
        # Check steps for patterns
        if 'steps' in job_data:
            for step in job_data['steps']:
                if isinstance(step, dict):
                    matches.extend(self._check_step_patterns(
                        step, job_name, file_path, lines
                    ))
        
        return matches
    
    def _check_step_patterns(
        self,
        step: Dict,
        job_name: str,
        file_path: Path,
        lines: List[str]
    ) -> List[PatternMatch]:
        """Check step-level patterns"""
        matches = []
        
        # Check for error handling
        if 'continue-on-error' in step or 'if' in step:
            matches.append(self._create_match(
                'WF001', file_path, 1,
                str(step.get('name', 'step')),
                'Step includes error handling',
                0.85
            ))
        
        # Check action versions
        if 'uses' in step:
            action = step['uses']
            
            # Check for pinned versions
            if '@v' in action or re.match(r'.*@[0-9]+\.[0-9]+', action):
                matches.append(self._create_match(
                    'WF003', file_path, 1,
                    action,
                    'Action uses pinned version',
                    0.9
                ))
            # Check for unpinned versions
            elif '@main' in action or '@master' in action:
                matches.append(self._create_match(
                    'WF006', file_path, 1,
                    action,
                    'Action uses unpinned version (risk of breaking changes)',
                    0.95
                ))
        
        # Check for secrets usage
        step_str = str(step)
        if 'secrets.' in step_str:
            matches.append(self._create_match(
                'WF002', file_path, 1,
                'secrets usage',
                'Properly uses GitHub secrets',
                0.9
            ))
        
        # Check for hardcoded credentials (basic check)
        suspicious_patterns = [
            r'password:\s*["\'][^"\']+["\']',
            r'token:\s*["\'][^"\']+["\']',
            r'api[_-]?key:\s*["\'][^"\']+["\']',
        ]
        for pattern in suspicious_patterns:
            if re.search(pattern, step_str, re.IGNORECASE):
                matches.append(self._create_match(
                    'WF007', file_path, 1,
                    'potential hardcoded credential',
                    'Hardcoded credential detected - use secrets instead',
                    0.8
                ))
        
        return matches
    
    def _create_match(
        self,
        pattern_id: str,
        file_path: Path,
        line_number: int,
        content: str,
        context: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PatternMatch:
        """Helper to create PatternMatch object"""
        pattern = next(p for p in self.patterns if p.id == pattern_id)
        return PatternMatch(
            pattern_id=pattern_id,
            pattern_name=pattern.name,
            category=pattern.category,
            file_path=str(file_path),
            line_number=line_number,
            matched_content=content,
            context=context,
            confidence=confidence,
            metadata=metadata or {}
        )
    
    def get_patterns(self) -> List[Pattern]:
        """Get all workflow patterns"""
        return self.patterns


class SecurityPatternDetector(PatternDetector):
    """Detects security-related patterns"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[Pattern]:
        """Initialize security patterns"""
        return [
            Pattern(
                id='SEC001',
                name='Input Validation',
                category='security',
                description='Code validates external input',
                severity='high',
                type='good_practice',
                tags=['security', 'validation', 'safety'],
                examples=['if not validate_input(user_data):']
            ),
            Pattern(
                id='SEC002',
                name='SQL Injection Risk',
                category='security',
                description='Potential SQL injection vulnerability',
                severity='critical',
                type='anti_pattern',
                tags=['security', 'sql', 'vulnerability'],
                examples=['query = f"SELECT * FROM users WHERE id = {user_id}"']
            ),
            Pattern(
                id='SEC003',
                name='Hardcoded Secrets',
                category='security',
                description='Hardcoded passwords or API keys detected',
                severity='critical',
                type='anti_pattern',
                tags=['security', 'secrets', 'credentials'],
                examples=['API_KEY = "sk-1234567890abcdef"']
            ),
            Pattern(
                id='SEC004',
                name='Secure Random',
                category='security',
                description='Uses secrets module for cryptographic randomness',
                severity='medium',
                type='good_practice',
                tags=['security', 'cryptography', 'random'],
                examples=['import secrets\ntoken = secrets.token_hex(16)']
            ),
        ]
    
    def detect(self, file_path: Path, content: str) -> List[PatternMatch]:
        """Detect security patterns"""
        matches = []
        lines = content.split('\n')
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'["\'](?:api[_-]?key|password|secret|token)["\']?\s*[=:]\s*["\'][\w-]{16,}["\']', 'SEC003'),
            (r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', 'SEC003'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, pattern_id in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(self._create_match(
                        pattern_id, file_path, i,
                        line.strip(),
                        'Hardcoded secret detected',
                        0.75
                    ))
        
        # Check for SQL injection risks
        sql_injection_patterns = [
            r'["\']SELECT .* WHERE .*[+%].*["\']',
            r'f["\']SELECT .* WHERE .*\{.*\}.*["\']',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in sql_injection_patterns:
                if re.search(pattern, line):
                    matches.append(self._create_match(
                        'SEC002', file_path, i,
                        line.strip(),
                        'Potential SQL injection vulnerability',
                        0.7
                    ))
        
        # Check for secure random usage
        if 'import secrets' in content or 'from secrets import' in content:
            line_num = next(i for i, line in enumerate(lines, 1) if 'secrets' in line)
            matches.append(self._create_match(
                'SEC004', file_path, line_num,
                lines[line_num - 1].strip(),
                'Uses secure random number generation',
                0.9
            ))
        
        return matches
    
    def _create_match(
        self,
        pattern_id: str,
        file_path: Path,
        line_number: int,
        content: str,
        context: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PatternMatch:
        """Helper to create PatternMatch object"""
        pattern = next(p for p in self.patterns if p.id == pattern_id)
        return PatternMatch(
            pattern_id=pattern_id,
            pattern_name=pattern.name,
            category=pattern.category,
            file_path=str(file_path),
            line_number=line_number,
            matched_content=content,
            context=context,
            confidence=confidence,
            metadata=metadata or {}
        )
    
    def get_patterns(self) -> List[Pattern]:
        """Get all security patterns"""
        return self.patterns


class CrossRepoPatternMatcher:
    """
    Main pattern matcher that coordinates multiple detectors.
    
    Analyzes repositories for best practices across code, workflows,
    documentation, and security.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize pattern matcher"""
        self.repo_path = Path(repo_path or os.getcwd())
        self.repo_name = self.repo_path.name
        
        # Initialize detectors
        self.detectors: List[PatternDetector] = [
            CodePatternDetector(),
            WorkflowPatternDetector(),
            SecurityPatternDetector(),
        ]
        
        # Analysis results
        self.all_matches: List[PatternMatch] = []
        
    def analyze_repository(self) -> RepositoryAnalysis:
        """
        Analyze the repository for patterns.
        
        Returns:
            RepositoryAnalysis with all findings and recommendations
        """
        print(f"🔍 Analyzing repository: {self.repo_name}")
        print("=" * 80)
        
        self.all_matches = []
        
        # Analyze all relevant files
        file_patterns = {
            '*.py': ['.py'],
            '*.yml': ['.yml', '.yaml'],
            '*.yaml': ['.yml', '.yaml'],
        }
        
        analyzed_count = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and common excludes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file matches our patterns
                if any(file.endswith(ext) for exts in file_patterns.values() for ext in exts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Run all detectors
                        for detector in self.detectors:
                            matches = detector.detect(file_path, content)
                            self.all_matches.extend(matches)
                        
                        analyzed_count += 1
                    
                    except Exception as e:
                        print(f"⚠️  Error analyzing {file_path}: {e}", file=sys.stderr)
        
        print(f"✅ Analyzed {analyzed_count} files")
        print(f"📊 Found {len(self.all_matches)} pattern matches")
        print()
        
        # Generate analysis report
        return self._generate_report()
    
    def _generate_report(self) -> RepositoryAnalysis:
        """Generate comprehensive analysis report"""
        
        # Calculate summary statistics
        summary = self._calculate_summary()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Calculate best practices score
        score = self._calculate_score()
        
        return RepositoryAnalysis(
            repository_name=self.repo_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            patterns_matched=self.all_matches,
            summary=summary,
            recommendations=recommendations,
            score=score
        )
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        
        # Group by category
        by_category = defaultdict(list)
        for match in self.all_matches:
            by_category[match.category].append(match)
        
        # Group by type
        good_practices = [m for m in self.all_matches if self._get_pattern(m.pattern_id).type == 'good_practice']
        anti_patterns = [m for m in self.all_matches if self._get_pattern(m.pattern_id).type == 'anti_pattern']
        
        # Group by severity
        by_severity = defaultdict(list)
        for match in self.all_matches:
            pattern = self._get_pattern(match.pattern_id)
            by_severity[pattern.severity].append(match)
        
        return {
            'total_patterns': len(self.all_matches),
            'good_practices': len(good_practices),
            'anti_patterns': len(anti_patterns),
            'by_category': {cat: len(matches) for cat, matches in by_category.items()},
            'by_severity': {sev: len(matches) for sev, matches in by_severity.items()},
            'unique_files': len(set(m.file_path for m in self.all_matches)),
            'avg_confidence': sum(m.confidence for m in self.all_matches) / len(self.all_matches) if self.all_matches else 0.0
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Critical issues first
        critical = [m for m in self.all_matches if self._get_pattern(m.pattern_id).severity == 'critical']
        if critical:
            recommendations.append(
                f"🔴 CRITICAL: {len(critical)} critical security issues detected. "
                "Address these immediately to prevent vulnerabilities."
            )
        
        # Anti-patterns
        anti_patterns = [m for m in self.all_matches if self._get_pattern(m.pattern_id).type == 'anti_pattern']
        if anti_patterns:
            top_anti = Counter(m.pattern_name for m in anti_patterns).most_common(3)
            recommendations.append(
                f"⚠️  {len(anti_patterns)} anti-patterns detected. "
                f"Most common: {', '.join(f'{name} ({count})' for name, count in top_anti)}"
            )
        
        # Good practices recognition
        good_practices = [m for m in self.all_matches if self._get_pattern(m.pattern_id).type == 'good_practice']
        if good_practices:
            recommendations.append(
                f"✅ {len(good_practices)} good practices found. "
                "Keep up the excellent work!"
            )
        
        # Category-specific recommendations
        by_category = defaultdict(list)
        for match in self.all_matches:
            by_category[match.category].append(match)
        
        if 'security' in by_category:
            sec_matches = by_category['security']
            sec_good = [m for m in sec_matches if self._get_pattern(m.pattern_id).type == 'good_practice']
            sec_bad = [m for m in sec_matches if self._get_pattern(m.pattern_id).type == 'anti_pattern']
            
            if sec_bad:
                recommendations.append(
                    f"🔒 Security: {len(sec_bad)} potential security issues found. "
                    "Review and remediate to improve security posture."
                )
        
        if 'workflow' in by_category:
            wf_matches = by_category['workflow']
            recommendations.append(
                f"⚙️  Workflows: {len(wf_matches)} patterns detected. "
                "Consider standardizing workflow patterns across the repository."
            )
        
        # Score-based recommendations
        score = self._calculate_score()
        if score >= 80:
            recommendations.append(
                f"🌟 Excellent! Score: {score:.1f}/100. "
                "This repository follows strong best practices."
            )
        elif score >= 60:
            recommendations.append(
                f"👍 Good score: {score:.1f}/100. "
                "Some improvements possible to reach excellence."
            )
        elif score >= 40:
            recommendations.append(
                f"📈 Score: {score:.1f}/100. "
                "Significant improvements needed. Focus on critical issues first."
            )
        else:
            recommendations.append(
                f"🔧 Score: {score:.1f}/100. "
                "Major improvements needed. Consider systematic refactoring."
            )
        
        return recommendations
    
    def _calculate_score(self) -> float:
        """
        Calculate overall best practices score (0-100).
        
        Scoring algorithm:
        - Start at 50 (baseline)
        - Add points for good practices (weighted by severity)
        - Subtract points for anti-patterns (weighted by severity)
        - Consider confidence levels
        """
        if not self.all_matches:
            return 50.0
        
        score = 50.0
        
        # Severity weights
        severity_weights = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1,
            'info': 0.5
        }
        
        for match in self.all_matches:
            pattern = self._get_pattern(match.pattern_id)
            weight = severity_weights.get(pattern.severity, 1)
            confidence_factor = match.confidence
            
            if pattern.type == 'good_practice':
                score += weight * confidence_factor
            elif pattern.type == 'anti_pattern':
                score -= weight * confidence_factor
        
        # Normalize to 0-100 range
        return max(0.0, min(100.0, score))
    
    def _get_pattern(self, pattern_id: str) -> Pattern:
        """Get pattern by ID"""
        for detector in self.detectors:
            for pattern in detector.get_patterns():
                if pattern.id == pattern_id:
                    return pattern
        raise ValueError(f"Pattern {pattern_id} not found")
    
    def print_report(self, analysis: RepositoryAnalysis, verbose: bool = False):
        """Print human-readable report"""
        print("=" * 80)
        print(f"📊 PATTERN ANALYSIS REPORT: {analysis.repository_name}")
        print("=" * 80)
        print(f"Generated: {analysis.timestamp}")
        print(f"Score: {analysis.score:.1f}/100")
        print()
        
        # Summary
        print("📈 SUMMARY")
        print("-" * 80)
        print(f"Total patterns matched:    {analysis.summary['total_patterns']}")
        print(f"Good practices:            {analysis.summary['good_practices']}")
        print(f"Anti-patterns:             {analysis.summary['anti_patterns']}")
        print(f"Files analyzed:            {analysis.summary['unique_files']}")
        print(f"Average confidence:        {analysis.summary['avg_confidence']:.2%}")
        print()
        
        # By category
        print("📋 BY CATEGORY")
        print("-" * 80)
        for category, count in sorted(analysis.summary['by_category'].items()):
            print(f"  {category:20s} {count}")
        print()
        
        # By severity
        print("⚠️  BY SEVERITY")
        print("-" * 80)
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        for severity in severity_order:
            count = analysis.summary['by_severity'].get(severity, 0)
            if count > 0:
                icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'info': '🔵'}.get(severity, '⚪')
                print(f"  {icon} {severity:15s} {count}")
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"{i}. {rec}")
        print()
        
        # Detailed matches in verbose mode
        if verbose and analysis.patterns_matched:
            print("🔍 DETAILED FINDINGS")
            print("=" * 80)
            
            # Group by file
            by_file = defaultdict(list)
            for match in analysis.patterns_matched:
                by_file[match.file_path].append(match)
            
            for file_path, matches in sorted(by_file.items())[:10]:  # Top 10 files
                print(f"\n📁 {file_path}")
                for match in matches[:5]:  # Top 5 matches per file
                    pattern = self._get_pattern(match.pattern_id)
                    severity_icon = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🟢',
                        'info': '🔵'
                    }.get(pattern.severity, '⚪')
                    
                    type_icon = '✅' if pattern.type == 'good_practice' else '⚠️'
                    
                    print(f"  {type_icon} {severity_icon} Line {match.line_number}: {match.pattern_name}")
                    print(f"     {match.context}")
                
                if len(matches) > 5:
                    print(f"     ... and {len(matches) - 5} more")
        
        print("=" * 80)
        print("✅ Analysis complete")
        print("=" * 80)
    
    def export_report(self, analysis: RepositoryAnalysis, output_path: str):
        """Export report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(analysis.to_dict(), f, indent=2)
        print(f"📄 Report exported to: {output_path}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Cross-Repository Pattern Matcher for Best Practices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--repo',
        default='.',
        help='Repository path to analyze (default: current directory)'
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
        help='Verbose output with detailed findings'
    )
    parser.add_argument(
        '--patterns',
        action='store_true',
        help='List all available patterns and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize matcher
    matcher = CrossRepoPatternMatcher(args.repo)
    
    # List patterns if requested
    if args.patterns:
        print("📋 AVAILABLE PATTERNS")
        print("=" * 80)
        for detector in matcher.detectors:
            patterns = detector.get_patterns()
            print(f"\n{patterns[0].category.upper()} PATTERNS ({len(patterns)} patterns):")
            for pattern in patterns:
                type_icon = '✅' if pattern.type == 'good_practice' else '⚠️'
                print(f"  {type_icon} {pattern.id}: {pattern.name}")
                print(f"     {pattern.description}")
                print(f"     Severity: {pattern.severity}, Tags: {', '.join(pattern.tags)}")
        return
    
    # Run analysis
    analysis = matcher.analyze_repository()
    
    # Print report
    matcher.print_report(analysis, verbose=args.verbose)
    
    # Export if requested
    if args.output:
        matcher.export_report(analysis, args.output)


if __name__ == '__main__':
    main()
