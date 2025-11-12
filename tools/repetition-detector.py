#!/usr/bin/env python3
"""
AI Pattern Repetition Detector

Analyzes contribution patterns from AI agents to detect repetitive code structures,
solution approaches, and commit patterns that may indicate lack of diversity.
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from hashlib import md5


class ASTHasher(ast.NodeVisitor):
    """Generates structural hash of AST nodes for similarity comparison"""
    
    def __init__(self):
        self.structure = []
        
    def generic_visit(self, node):
        """Visit all nodes and record their types"""
        self.structure.append(type(node).__name__)
        super().generic_visit(node)
        
    def get_hash(self) -> str:
        """Get structural hash of the AST"""
        structure_str = '|'.join(self.structure)
        return md5(structure_str.encode()).hexdigest()


class RepetitionDetector:
    """Detects repetitive patterns in AI agent contributions"""
    
    def __init__(self, repo_dir: str, since_days: int = 30):
        self.repo_dir = Path(repo_dir)
        self.since_days = since_days
        self.since_date = datetime.now(timezone.utc) - timedelta(days=since_days)
        self.contributions = defaultdict(list)
        self.code_structures = defaultdict(list)
        self.commit_messages = defaultdict(list)
        self.file_sequences = defaultdict(list)
        self.approach_clusters = defaultdict(set)
        
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_dir)] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}", file=sys.stderr)
            return ""
    
    def _extract_agent_id(self, author_email: str, author_name: str) -> Optional[str]:
        """Extract agent ID from commit author information"""
        # Match patterns like: copilot-swe-agent[bot], github-actions[bot], etc.
        bot_match = re.search(r'(\w+(?:-\w+)*)\[bot\]', author_name)
        if bot_match:
            return bot_match.group(1)
        
        # Match email patterns like: 198982749+Copilot@users.noreply.github.com
        email_match = re.search(r'\+(\w+)@', author_email)
        if email_match:
            return email_match.group(1).lower()
        
        # Check if it's a GitHub Actions bot
        if 'github-actions' in author_email or 'github-actions' in author_name:
            return 'github-actions'
            
        return None
    
    def collect_contributions(self):
        """Collect all AI agent contributions from git history"""
        # Get all commits since the specified date
        since_str = self.since_date.strftime('%Y-%m-%d')
        log_output = self._run_git_command([
            'log',
            '--all',
            '--pretty=format:%H|%an|%ae|%s|%cd',
            '--date=iso',
            f'--since={since_str}'
        ])
        
        if not log_output:
            print("No commits found in the specified time range", file=sys.stderr)
            return
        
        for line in log_output.split('\n'):
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) < 5:
                continue
                
            commit_hash, author_name, author_email, message, date = parts
            agent_id = self._extract_agent_id(author_email, author_name)
            
            if not agent_id:
                continue  # Skip human contributors
            
            # Get files changed in this commit
            files_output = self._run_git_command([
                'diff-tree',
                '--no-commit-id',
                '--name-only',
                '-r',
                commit_hash
            ])
            
            files = files_output.split('\n') if files_output else []
            
            contribution = {
                'commit_hash': commit_hash,
                'agent_id': agent_id,
                'author_name': author_name,
                'message': message,
                'date': date,
                'files': files
            }
            
            self.contributions[agent_id].append(contribution)
            self.commit_messages[agent_id].append(message)
            
            # Track file modification sequences
            file_pattern = '|'.join(sorted([f for f in files if f]))
            if file_pattern:
                self.file_sequences[agent_id].append(file_pattern)
    
    def analyze_code_structures(self):
        """Analyze code structure similarity using AST comparison"""
        for agent_id, contribs in self.contributions.items():
            for contrib in contribs:
                for file_path in contrib['files']:
                    if not file_path.endswith('.py'):
                        continue
                    
                    full_path = self.repo_dir / file_path
                    
                    # Get file content at this commit
                    try:
                        content = self._run_git_command([
                            'show',
                            f"{contrib['commit_hash']}:{file_path}"
                        ])
                        
                        if content:
                            struct_hash = self._get_ast_hash(content)
                            if struct_hash:
                                self.code_structures[agent_id].append({
                                    'file': file_path,
                                    'commit': contrib['commit_hash'],
                                    'hash': struct_hash
                                })
                    except Exception as e:
                        # File might not exist or be parseable
                        continue
    
    def _get_ast_hash(self, code: str) -> Optional[str]:
        """Get structural hash of Python code"""
        try:
            tree = ast.parse(code)
            hasher = ASTHasher()
            hasher.visit(tree)
            return hasher.get_hash()
        except SyntaxError:
            return None
    
    def detect_commit_message_patterns(self) -> Dict[str, Any]:
        """Detect repetitive commit message templates"""
        patterns = {}
        
        for agent_id, messages in self.commit_messages.items():
            if len(messages) < 2:
                continue
            
            # Extract common prefixes (emojis, tags)
            prefixes = defaultdict(int)
            templates = defaultdict(int)
            
            for msg in messages:
                # Count emoji prefixes
                emoji_match = re.match(r'^([\U0001F300-\U0001F9FF]+)', msg)
                if emoji_match:
                    prefixes[emoji_match.group(1)] += 1
                
                # Extract template by replacing specific words with placeholders
                template = re.sub(r'\b(fix|add|update|remove|create)\b', '<ACTION>', msg, flags=re.IGNORECASE)
                template = re.sub(r'\b(issue|pr|#\d+)\b', '<REF>', template, flags=re.IGNORECASE)
                template = re.sub(r'\b[A-Z_]+\b', '<CONST>', template)
                templates[template] += 1
            
            # Calculate repetition score
            if messages:
                most_common_template = max(templates.values()) if templates else 0
                repetition_rate = most_common_template / len(messages)
                
                patterns[agent_id] = {
                    'total_commits': len(messages),
                    'unique_templates': len(templates),
                    'most_common_count': most_common_template,
                    'repetition_rate': repetition_rate,
                    'emoji_usage': dict(prefixes)
                }
        
        return patterns
    
    def detect_code_similarity(self) -> Dict[str, Any]:
        """Detect similar code structures within agent's contributions"""
        similarity_report = {}
        
        for agent_id, structures in self.code_structures.items():
            if len(structures) < 2:
                continue
            
            # Count hash frequencies
            hash_counts = defaultdict(list)
            for struct in structures:
                hash_counts[struct['hash']].append(struct)
            
            # Find duplicates
            duplicates = {h: files for h, files in hash_counts.items() if len(files) > 1}
            
            if hash_counts:
                total_structures = len(structures)
                duplicate_count = sum(len(files) - 1 for files in duplicates.values())
                similarity_rate = duplicate_count / total_structures if total_structures > 0 else 0
                
                similarity_report[agent_id] = {
                    'total_structures': total_structures,
                    'unique_structures': len(hash_counts),
                    'duplicate_structures': duplicate_count,
                    'similarity_rate': similarity_rate,
                    'duplicates': [
                        {
                            'hash': h,
                            'occurrences': len(files),
                            'files': [f['file'] for f in files[:5]]  # Limit to 5 examples
                        }
                        for h, files in list(duplicates.items())[:10]  # Limit to 10 groups
                    ]
                }
        
        return similarity_report
    
    def detect_file_sequence_patterns(self) -> Dict[str, Any]:
        """Detect repetitive file modification sequences"""
        sequence_patterns = {}
        
        for agent_id, sequences in self.file_sequences.items():
            if len(sequences) < 2:
                continue
            
            sequence_counts = defaultdict(int)
            for seq in sequences:
                sequence_counts[seq] += 1
            
            most_common = max(sequence_counts.values()) if sequence_counts else 0
            repetition_rate = most_common / len(sequences) if sequences else 0
            
            sequence_patterns[agent_id] = {
                'total_commits': len(sequences),
                'unique_sequences': len(sequence_counts),
                'most_common_count': most_common,
                'repetition_rate': repetition_rate,
                'top_sequences': [
                    {'pattern': seq, 'count': count}
                    for seq, count in sorted(
                        sequence_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                ]
            }
        
        return sequence_patterns
    
    def detect_solution_approach_clustering(self) -> Dict[str, Any]:
        """Detect if agents are using similar approaches to solve problems"""
        approach_report = {}
        
        for agent_id, contribs in self.contributions.items():
            approaches = set()
            
            for contrib in contribs:
                # Analyze commit message for approach indicators
                msg = contrib['message'].lower()
                
                # Common approach patterns
                if 'refactor' in msg:
                    approaches.add('refactoring')
                if 'workflow' in msg or 'action' in msg:
                    approaches.add('workflow_automation')
                if 'test' in msg or 'spec' in msg:
                    approaches.add('testing')
                if 'fix' in msg or 'bug' in msg:
                    approaches.add('bug_fixing')
                if 'add' in msg or 'implement' in msg or 'create' in msg:
                    approaches.add('feature_addition')
                if 'documentation' in msg or 'readme' in msg or 'doc' in msg:
                    approaches.add('documentation')
                if 'optimize' in msg or 'performance' in msg:
                    approaches.add('optimization')
                if 'security' in msg:
                    approaches.add('security')
                
                # Analyze file types
                for file_path in contrib['files']:
                    if file_path.endswith('.py'):
                        approaches.add('python_development')
                    elif file_path.endswith(('.yml', '.yaml')):
                        approaches.add('yaml_configuration')
                    elif file_path.endswith('.md'):
                        approaches.add('markdown_documentation')
                    elif file_path.endswith('.sh'):
                        approaches.add('shell_scripting')
            
            if approaches:
                approach_report[agent_id] = {
                    'total_contributions': len(contribs),
                    'unique_approaches': len(approaches),
                    'approaches': list(approaches),
                    'diversity_score': len(approaches) / max(len(contribs), 1) * 100
                }
        
        return approach_report
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive repetition detection report"""
        return {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'repository': str(self.repo_dir),
                'analysis_period_days': self.since_days,
                'since_date': self.since_date.isoformat()
            },
            'summary': {
                'total_agents': len(self.contributions),
                'total_contributions': sum(len(c) for c in self.contributions.values()),
                'agents': list(self.contributions.keys())
            },
            'commit_message_patterns': self.detect_commit_message_patterns(),
            'code_similarity': self.detect_code_similarity(),
            'file_sequence_patterns': self.detect_file_sequence_patterns(),
            'solution_approaches': self.detect_solution_approach_clustering(),
            'repetition_flags': self._generate_flags()
        }
    
    def _generate_flags(self) -> List[Dict[str, Any]]:
        """Generate flags for significant repetition issues"""
        flags = []
        
        # Check commit message repetition
        msg_patterns = self.detect_commit_message_patterns()
        for agent_id, data in msg_patterns.items():
            if data['repetition_rate'] > 0.7:  # More than 70% same template
                flags.append({
                    'agent_id': agent_id,
                    'type': 'commit_message_repetition',
                    'severity': 'high',
                    'description': f"Agent uses the same commit message template {data['repetition_rate']:.1%} of the time",
                    'metric': data['repetition_rate']
                })
        
        # Check code similarity
        similarity = self.detect_code_similarity()
        for agent_id, data in similarity.items():
            if data['similarity_rate'] > 0.5:  # More than 50% duplicate structures
                flags.append({
                    'agent_id': agent_id,
                    'type': 'code_structure_repetition',
                    'severity': 'high',
                    'description': f"Agent produces similar code structures {data['similarity_rate']:.1%} of the time",
                    'metric': data['similarity_rate']
                })
        
        # Check approach diversity
        approaches = self.detect_solution_approach_clustering()
        for agent_id, data in approaches.items():
            if data['diversity_score'] < 30:  # Less than 30% diversity
                flags.append({
                    'agent_id': agent_id,
                    'type': 'low_approach_diversity',
                    'severity': 'medium',
                    'description': f"Agent shows low approach diversity: {data['diversity_score']:.1f}%",
                    'metric': data['diversity_score']
                })
        
        return flags


def main():
    parser = argparse.ArgumentParser(
        description='Detect repetitive patterns in AI agent contributions'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '--since-days',
        type=int,
        default=30,
        help='Number of days to look back in history (default: 30)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for JSON report (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = RepetitionDetector(args.directory, args.since_days)
    
    # Collect and analyze contributions
    print("Collecting contributions...", file=sys.stderr)
    detector.collect_contributions()
    
    print("Analyzing code structures...", file=sys.stderr)
    detector.analyze_code_structures()
    
    print("Generating report...", file=sys.stderr)
    report = detector.generate_report()
    
    # Output report
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2))
    
    # Exit with error code if significant repetition detected
    if report['repetition_flags']:
        high_severity = [f for f in report['repetition_flags'] if f['severity'] == 'high']
        if high_severity:
            print(f"\n⚠️  {len(high_severity)} high-severity repetition issues detected", file=sys.stderr)
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
