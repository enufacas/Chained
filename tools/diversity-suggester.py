#!/usr/bin/env python3
"""
AI Diversity Suggester

Analyzes repetition reports and suggests concrete alternative approaches
based on successful diverse solutions from repository history.
"""

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set


class DiversitySuggester:
    """Suggests diverse alternatives based on repetition analysis"""
    
    def __init__(self, repo_dir: str):
        self.repo_dir = Path(repo_dir)
        self.analysis_dir = self.repo_dir / 'analysis'
        self.diversity_data = self._load_diversity_data()
        self.successful_patterns = []
        
    def _load_diversity_data(self) -> Dict:
        """Load pattern diversity data"""
        diversity_file = self.analysis_dir / 'pattern-diversity.json'
        
        if diversity_file.exists():
            with open(diversity_file, 'r') as f:
                return json.load(f)
        
        return {
            'pattern_library': {
                'successful_diverse_approaches': [],
                'repetitive_patterns': []
            }
        }
    
    def load_repetition_report(self, report_path: str) -> Dict:
        """Load repetition detection report"""
        try:
            with open(report_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Report file not found: {report_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in report file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def analyze_repository_patterns(self):
        """Analyze repository for successful diverse patterns"""
        # Look for diverse solutions in analysis directory
        if self.analysis_dir.exists():
            for file_path in self.analysis_dir.glob('*.json'):
                if file_path.name == 'pattern-diversity.json':
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        # Extract successful patterns if they exist
                        if 'successful_patterns' in data:
                            self.successful_patterns.extend(data['successful_patterns'])
                except Exception:
                    continue
    
    def suggest_for_commit_message_repetition(self, agent_id: str, data: Dict) -> List[str]:
        """Suggest alternatives for repetitive commit messages"""
        suggestions = [
            "## Commit Message Diversity Suggestions",
            "",
            f"Agent **{agent_id}** shows high commit message repetition ({data['repetition_rate']:.1%}).",
            "",
            "### Alternative Commit Message Styles:",
            "",
            "1. **Conventional Commits Format**:",
            "   - `feat: add new feature X`",
            "   - `fix: resolve issue with Y`",
            "   - `docs: update documentation for Z`",
            "   - `refactor: restructure component A`",
            "   - `test: add tests for B`",
            "   - `chore: update dependencies`",
            "",
            "2. **Descriptive Action-Based**:",
            "   - `Implement user authentication system`",
            "   - `Optimize database query performance`",
            "   - `Add validation for user input`",
            "   - `Extract utility functions into separate module`",
            "",
            "3. **Problem-Solution Format**:",
            "   - `Fix: Users unable to login → Add session management`",
            "   - `Issue: Slow page load → Implement caching layer`",
            "   - `Bug: Invalid data → Add input sanitization`",
            "",
            "4. **Context-Rich Messages**:",
            "   - Include WHY, not just WHAT",
            "   - Reference related issues/PRs",
            "   - Mention affected components",
            "   - Note any breaking changes",
            "",
            f"**Examples from your history:** {', '.join(list(data.get('emoji_usage', {}).keys())[:3])}",
            "",
            "**Recommendation:** Rotate between these styles to maintain variety while staying informative.",
            ""
        ]
        
        return suggestions
    
    def suggest_for_code_structure_repetition(self, agent_id: str, data: Dict) -> List[str]:
        """Suggest alternatives for repetitive code structures"""
        suggestions = [
            "## Code Structure Diversity Suggestions",
            "",
            f"Agent **{agent_id}** shows high code structure repetition ({data['similarity_rate']:.1%}).",
            "",
            "### Alternative Architectural Patterns:",
            "",
            "1. **Design Patterns to Explore**:",
            "   - **Strategy Pattern**: For varying algorithms",
            "   - **Factory Pattern**: For object creation flexibility",
            "   - **Observer Pattern**: For event-driven architectures",
            "   - **Decorator Pattern**: For extending functionality",
            "   - **Command Pattern**: For encapsulating operations",
            "",
            "2. **Code Organization Approaches**:",
            "   - **Class-based OOP**: Encapsulate related functionality",
            "   - **Functional Programming**: Use pure functions and composition",
            "   - **Module-based**: Organize by feature rather than type",
            "   - **Service-oriented**: Separate concerns into services",
            "",
            "3. **Data Structure Variations**:",
            "   - Use dictionaries for flexible key-value storage",
            "   - Leverage dataclasses for structured data",
            "   - Consider namedtuples for immutable records",
            "   - Use sets for unique collections",
            "   - Explore generators for memory efficiency",
            "",
            "4. **Control Flow Alternatives**:",
            "   - Replace nested ifs with guard clauses",
            "   - Use dictionary dispatch instead of if-elif chains",
            "   - Leverage list comprehensions over loops",
            "   - Consider itertools for complex iterations",
            ""
        ]
        
        # Add examples from repository if available
        if self.successful_patterns:
            suggestions.extend([
                "### Successful Patterns from Repository:",
                ""
            ])
            for pattern in self.successful_patterns[:3]:
                suggestions.append(f"- {pattern.get('description', 'Pattern example')}")
            suggestions.append("")
        
        suggestions.extend([
            "**Recommendation:** Experiment with different patterns based on the problem domain.",
            ""
        ])
        
        return suggestions
    
    def suggest_for_low_approach_diversity(self, agent_id: str, data: Dict) -> List[str]:
        """Suggest alternatives for low approach diversity"""
        current_approaches = set(data.get('approaches', []))
        
        all_possible_approaches = {
            'refactoring': 'Improve existing code structure and readability',
            'testing': 'Add comprehensive test coverage',
            'bug_fixing': 'Resolve reported issues and defects',
            'feature_addition': 'Implement new functionality',
            'documentation': 'Create or improve documentation',
            'optimization': 'Enhance performance and efficiency',
            'security': 'Address security vulnerabilities',
            'workflow_automation': 'Automate development and deployment processes',
            'code_review': 'Review and improve code quality',
            'dependency_management': 'Update and manage dependencies',
            'architecture_design': 'Design system architecture',
            'api_design': 'Create or improve APIs',
            'ui_ux': 'Enhance user interface and experience',
            'database_optimization': 'Optimize data storage and queries',
            'error_handling': 'Improve error handling and logging',
            'monitoring': 'Add monitoring and observability',
            'ci_cd': 'Improve continuous integration/deployment',
            'accessibility': 'Enhance accessibility features'
        }
        
        unused_approaches = {k: v for k, v in all_possible_approaches.items() 
                           if k not in current_approaches}
        
        suggestions = [
            "## Approach Diversity Suggestions",
            "",
            f"Agent **{agent_id}** shows low approach diversity (score: {data['diversity_score']:.1f}%).",
            "",
            f"**Current approaches used:** {', '.join(current_approaches) if current_approaches else 'None detected'}",
            "",
            "### Unexplored Approaches to Consider:",
            ""
        ]
        
        # Suggest top unexplored approaches
        for approach, description in list(unused_approaches.items())[:8]:
            suggestions.append(f"- **{approach.replace('_', ' ').title()}**: {description}")
        
        suggestions.extend([
            "",
            "### Diversification Strategy:",
            "",
            "1. **Problem-First Thinking**: Analyze the problem before choosing an approach",
            "2. **Cross-Pollination**: Apply patterns from one domain to another",
            "3. **Learn from Others**: Study diverse solutions in the repository",
            "4. **Experiment**: Try unfamiliar approaches in low-risk situations",
            "5. **Rotate Focus**: Alternate between different types of contributions",
            "",
            "### Specific Recommendations:",
            ""
        ])
        
        # Provide specific recommendations based on current approaches
        if 'feature_addition' in current_approaches and 'testing' not in current_approaches:
            suggestions.append("- Balance feature work with comprehensive testing")
        
        if 'bug_fixing' in current_approaches and 'optimization' not in current_approaches:
            suggestions.append("- Consider performance optimization alongside bug fixes")
        
        if 'documentation' not in current_approaches:
            suggestions.append("- Add documentation to enhance knowledge sharing")
        
        if 'security' not in current_approaches:
            suggestions.append("- Include security considerations in your work")
        
        suggestions.extend([
            "",
            "**Recommendation:** Aim to use at least 5-7 different approaches across contributions.",
            ""
        ])
        
        return suggestions
    
    def suggest_for_file_sequence_repetition(self, agent_id: str, data: Dict) -> List[str]:
        """Suggest alternatives for repetitive file modification patterns"""
        suggestions = [
            "## File Modification Pattern Suggestions",
            "",
            f"Agent **{agent_id}** shows repetitive file modification patterns ({data['repetition_rate']:.1%}).",
            "",
            "### Diversify Your File Touchpoints:",
            "",
            "1. **Explore Different Layers**:",
            "   - Frontend: UI components, styles, assets",
            "   - Backend: APIs, services, data models",
            "   - Infrastructure: Workflows, configs, scripts",
            "   - Testing: Unit tests, integration tests, e2e tests",
            "   - Documentation: READMEs, guides, API docs",
            "",
            "2. **Cross-Cutting Concerns**:",
            "   - Work on multiple related components simultaneously",
            "   - Address system-wide improvements",
            "   - Refactor common utilities",
            "   - Update configuration across the project",
            "",
            "3. **Broaden Your Scope**:",
            "   - Contribute to different modules/packages",
            "   - Work on various feature areas",
            "   - Address technical debt in different parts",
            "   - Improve tooling and automation",
            "",
            "**Recommendation:** Vary the files you modify to demonstrate full-stack capabilities.",
            ""
        ]
        
        return suggestions
    
    def generate_suggestions(self, report: Dict) -> str:
        """Generate comprehensive suggestions based on repetition report"""
        suggestions = [
            "# 🎨 AI Agent Diversity Improvement Suggestions",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "This report provides concrete suggestions for improving diversity in AI agent contributions.",
            "",
            "---",
            ""
        ]
        
        # Check for flags
        flags = report.get('repetition_flags', [])
        
        if not flags:
            suggestions.extend([
                "## ✅ No Significant Repetition Detected",
                "",
                "All agents show healthy diversity in their contributions.",
                "Continue maintaining varied approaches and patterns.",
                ""
            ])
            return '\n'.join(suggestions)
        
        # Group flags by agent
        agent_flags = defaultdict(list)
        for flag in flags:
            agent_flags[flag['agent_id']].append(flag)
        
        suggestions.extend([
            f"## 📊 Summary",
            "",
            f"- **Agents analyzed:** {report['summary']['total_agents']}",
            f"- **Agents with repetition issues:** {len(agent_flags)}",
            f"- **Total flags raised:** {len(flags)}",
            "",
            "---",
            ""
        ])
        
        # Generate suggestions for each agent
        for agent_id, agent_flag_list in agent_flags.items():
            suggestions.extend([
                f"## 🤖 Agent: `{agent_id}`",
                "",
                f"**Issues detected:** {len(agent_flag_list)}",
                ""
            ])
            
            for flag in agent_flag_list:
                flag_type = flag['type']
                
                if flag_type == 'commit_message_repetition':
                    data = report['commit_message_patterns'].get(agent_id, {})
                    suggestions.extend(self.suggest_for_commit_message_repetition(agent_id, data))
                
                elif flag_type == 'code_structure_repetition':
                    data = report['code_similarity'].get(agent_id, {})
                    suggestions.extend(self.suggest_for_code_structure_repetition(agent_id, data))
                
                elif flag_type == 'low_approach_diversity':
                    data = report['solution_approaches'].get(agent_id, {})
                    suggestions.extend(self.suggest_for_low_approach_diversity(agent_id, data))
                
                elif flag_type == 'file_sequence_repetition':
                    data = report['file_sequence_patterns'].get(agent_id, {})
                    suggestions.extend(self.suggest_for_file_sequence_repetition(agent_id, data))
            
            suggestions.append("---\n")
        
        # Add general recommendations
        suggestions.extend([
            "## 🎯 General Recommendations",
            "",
            "### For All Agents:",
            "",
            "1. **Study Successful Diverse Contributions**:",
            "   - Review `analysis/pattern-diversity.json` for examples",
            "   - Learn from agents with high diversity scores",
            "   - Identify patterns that correlate with success",
            "",
            "2. **Deliberate Practice**:",
            "   - Consciously vary your approaches",
            "   - Set personal diversity goals",
            "   - Track your own pattern metrics",
            "",
            "3. **Cross-Training**:",
            "   - Learn from different programming paradigms",
            "   - Explore unfamiliar design patterns",
            "   - Study solutions from other domains",
            "",
            "4. **Mindful Contribution**:",
            "   - Before starting, review recent contributions",
            "   - Choose different approaches intentionally",
            "   - Challenge yourself to avoid repetition",
            "",
            "5. **Feedback Loop**:",
            "   - Monitor your uniqueness scores",
            "   - Adjust based on feedback",
            "   - Celebrate improvements in diversity",
            "",
            "---",
            "",
            "## 📚 Resources",
            "",
            "- **Repository Analysis**: `analysis/` directory",
            "- **Pattern Library**: `analysis/pattern-diversity.json`",
            "- **Code Examples**: Various implementations across the codebase",
            "- **Workflow Examples**: `.github/workflows/` directory",
            "",
            "---",
            "",
            f"*Report generated by Diversity Suggester v1.0 on {datetime.now(timezone.utc).isoformat()}*",
            ""
        ])
        
        return '\n'.join(suggestions)


def main():
    parser = argparse.ArgumentParser(
        description='Generate diversity suggestions based on repetition analysis'
    )
    parser.add_argument(
        '--repetition-report',
        required=True,
        help='Path to repetition detection report (JSON)'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for suggestions (markdown, default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Initialize suggester
    suggester = DiversitySuggester(args.directory)
    
    # Load repetition report
    print("Loading repetition report...", file=sys.stderr)
    report = suggester.load_repetition_report(args.repetition_report)
    
    # Analyze repository for patterns
    print("Analyzing repository patterns...", file=sys.stderr)
    suggester.analyze_repository_patterns()
    
    # Generate suggestions
    print("Generating suggestions...", file=sys.stderr)
    suggestions = suggester.generate_suggestions(report)
    
    # Output suggestions
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(suggestions)
        print(f"Suggestions saved to {args.output}", file=sys.stderr)
    else:
        print(suggestions)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
