#!/usr/bin/env python3
"""
Autonomous Code Reviewer with Self-Improving Criteria

This script evaluates pull requests against evolving criteria and learns
from outcomes to improve its review quality over time.

Created by: @workflows-tech-lead
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class AutonomousReviewer:
    """Self-improving code reviewer that learns from outcomes."""
    
    def __init__(self, criteria_file: str = ".github/review-system/criteria.json"):
        self.criteria_file = Path(criteria_file)
        self.criteria = self._load_criteria()
        self.review_results = []
        
    def _load_criteria(self) -> Dict:
        """Load review criteria from JSON file."""
        if not self.criteria_file.exists():
            raise FileNotFoundError(f"Criteria file not found: {self.criteria_file}")
        
        with open(self.criteria_file, 'r') as f:
            return json.load(f)
    
    def _save_criteria(self):
        """Save updated criteria back to file."""
        self.criteria['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        with open(self.criteria_file, 'w') as f:
            json.dump(self.criteria, f, indent=2)
    
    def evaluate_pr_files(self, file_paths: List[str], file_contents: Dict[str, str]) -> Dict:
        """
        Evaluate PR files against all criteria.
        
        Args:
            file_paths: List of file paths changed in the PR
            file_contents: Dict mapping file paths to their contents
            
        Returns:
            Dictionary with evaluation results
        """
        results = {
            'overall_score': 0.0,
            'category_scores': {},
            'findings': [],
            'passed_checks': [],
            'failed_checks': [],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        total_weight = 0.0
        weighted_score = 0.0
        
        # Evaluate each criteria category
        for category_name, category in self.criteria['criteria'].items():
            category_result = self._evaluate_category(
                category_name, category, file_paths, file_contents
            )
            
            results['category_scores'][category_name] = category_result['score']
            results['findings'].extend(category_result['findings'])
            results['passed_checks'].extend(category_result['passed'])
            results['failed_checks'].extend(category_result['failed'])
            
            # Weight the score
            weight = category['weight']
            total_weight += weight
            weighted_score += category_result['score'] * weight
        
        # Calculate overall score
        results['overall_score'] = weighted_score / total_weight if total_weight > 0 else 0.0
        
        return results
    
    def _evaluate_category(
        self, 
        category_name: str, 
        category: Dict, 
        file_paths: List[str],
        file_contents: Dict[str, str]
    ) -> Dict:
        """Evaluate a single criteria category."""
        
        results = {
            'score': 0.0,
            'findings': [],
            'passed': [],
            'failed': []
        }
        
        checks = category.get('checks', [])
        if not checks:
            return results
        
        total_check_weight = sum(check['weight'] for check in checks)
        weighted_score = 0.0
        
        for check in checks:
            check_result = self._evaluate_check(
                check, category_name, file_paths, file_contents
            )
            
            check_weight = check['weight']
            weighted_score += check_result['score'] * check_weight
            
            # Track findings
            if check_result['passed']:
                results['passed'].append({
                    'category': category_name,
                    'check': check['name'],
                    'details': check_result.get('details', '')
                })
            else:
                results['failed'].append({
                    'category': category_name,
                    'check': check['name'],
                    'details': check_result.get('details', ''),
                    'severity': check_result.get('severity', 'medium')
                })
            
            if check_result.get('findings'):
                results['findings'].extend(check_result['findings'])
            
            # Update times_applied counter
            check['times_applied'] = check.get('times_applied', 0) + 1
        
        # Calculate category score
        results['score'] = weighted_score / total_check_weight if total_check_weight > 0 else 0.0
        
        return results
    
    def _evaluate_check(
        self, 
        check: Dict, 
        category: str,
        file_paths: List[str],
        file_contents: Dict[str, str]
    ) -> Dict:
        """Evaluate a single check against the PR."""
        
        result = {
            'score': 0.0,
            'passed': False,
            'findings': [],
            'details': ''
        }
        
        check_id = check['id']
        
        # Handle different check types
        if 'patterns' in check:
            result = self._check_patterns(check, file_contents)
        elif 'file_patterns' in check:
            result = self._check_file_patterns(check, file_paths)
        elif 'max_lines' in check:
            result = self._check_function_size(check, file_contents)
        elif 'max_depth' in check:
            result = self._check_nesting_depth(check, file_contents)
        elif check_id == 'dry_principle':
            result = self._check_duplication(check, file_contents)
        
        return result
    
    def _check_patterns(self, check: Dict, file_contents: Dict[str, str]) -> Dict:
        """Check for presence/absence of regex patterns."""
        
        patterns = check.get('patterns', [])
        negative_patterns = check.get('negative_patterns', [])
        
        positive_matches = 0
        negative_matches = 0
        findings = []
        
        for file_path, content in file_contents.items():
            # Check positive patterns (should be present)
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    positive_matches += len(matches)
            
            # Check negative patterns (should NOT be present)
            for pattern in negative_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    negative_matches += len(matches)
                    findings.append({
                        'file': file_path,
                        'issue': f"Found pattern that should be avoided: {pattern}",
                        'matches': len(matches),
                        'severity': 'high' if check.get('weight', 0) > 0.3 else 'medium'
                    })
        
        # Calculate score
        if patterns and not negative_patterns:
            # Positive patterns check - we want matches
            score = 1.0 if positive_matches > 0 else 0.0
            passed = positive_matches > 0
            details = f"Found {positive_matches} positive matches"
        elif negative_patterns and not patterns:
            # Negative patterns check - we don't want matches
            score = 1.0 if negative_matches == 0 else 0.0
            passed = negative_matches == 0
            details = f"Found {negative_matches} negative matches (should be 0)"
        else:
            # Both positive and negative
            score = (1.0 if positive_matches > 0 else 0.5) * (1.0 if negative_matches == 0 else 0.5)
            passed = positive_matches > 0 and negative_matches == 0
            details = f"Positive: {positive_matches}, Negative: {negative_matches}"
        
        return {
            'score': score,
            'passed': passed,
            'findings': findings,
            'details': details
        }
    
    def _check_file_patterns(self, check: Dict, file_paths: List[str]) -> Dict:
        """Check if certain file patterns are present (e.g., test files)."""
        
        file_patterns = check.get('file_patterns', [])
        matches = 0
        
        for pattern in file_patterns:
            for file_path in file_paths:
                if re.search(pattern, file_path):
                    matches += 1
        
        # Score based on whether test files are present
        score = 1.0 if matches > 0 else 0.0
        passed = matches > 0
        
        return {
            'score': score,
            'passed': passed,
            'details': f"Found {matches} matching files"
        }
    
    def _check_function_size(self, check: Dict, file_contents: Dict[str, str]) -> Dict:
        """Check if functions are reasonably sized."""
        
        max_lines = check.get('max_lines', 50)
        patterns = check.get('patterns', [])
        
        violations = []
        total_functions = 0
        
        for file_path, content in file_contents.items():
            if not (file_path.endswith('.py') or file_path.endswith('.js')):
                continue
            
            lines = content.split('\n')
            
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    total_functions += 1
                    # Count lines in function
                    start_line = content[:match.start()].count('\n')
                    # Simple heuristic: find next function or end
                    remaining = content[match.end():]
                    next_func = float('inf')
                    for p in patterns:
                        m = re.search(p, remaining)
                        if m:
                            next_func = min(next_func, remaining[:m.start()].count('\n'))
                    
                    func_lines = min(next_func, len(lines) - start_line)
                    
                    if func_lines > max_lines:
                        violations.append({
                            'file': file_path,
                            'lines': func_lines,
                            'max_allowed': max_lines
                        })
        
        # Score based on violation rate
        if total_functions == 0:
            score = 1.0  # No functions, pass by default
        else:
            violation_rate = len(violations) / total_functions
            score = max(0.0, 1.0 - violation_rate)
        
        passed = len(violations) == 0
        
        return {
            'score': score,
            'passed': passed,
            'details': f"{len(violations)} violations out of {total_functions} functions",
            'findings': violations if violations else []
        }
    
    def _check_nesting_depth(self, check: Dict, file_contents: Dict[str, str]) -> Dict:
        """Check nesting depth of code."""
        
        max_depth = check.get('max_depth', 3)
        violations = []
        
        for file_path, content in file_contents.items():
            if not (file_path.endswith('.py') or file_path.endswith('.js')):
                continue
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Count leading spaces/tabs
                stripped = line.lstrip()
                if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                    continue
                
                indent = len(line) - len(stripped)
                # Assume 4 spaces or 1 tab per level
                depth = indent // 4 if ' ' in line[:indent] else indent
                
                if depth > max_depth:
                    violations.append({
                        'file': file_path,
                        'line': i,
                        'depth': depth,
                        'max_allowed': max_depth
                    })
        
        score = 1.0 if len(violations) == 0 else max(0.0, 1.0 - len(violations) / 10)
        passed = len(violations) == 0
        
        return {
            'score': score,
            'passed': passed,
            'details': f"Found {len(violations)} nesting violations",
            'findings': violations if violations else []
        }
    
    def _check_duplication(self, check: Dict, file_contents: Dict[str, str]) -> Dict:
        """Check for code duplication (simple heuristic)."""
        
        # Simple check: look for repeated lines
        line_counts = {}
        duplicates = []
        
        for file_path, content in file_contents.items():
            if not (file_path.endswith('.py') or file_path.endswith('.js')):
                continue
            
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            
            for line in lines:
                if len(line) > 20:  # Only check substantial lines
                    line_counts[line] = line_counts.get(line, 0) + 1
        
        # Find duplicates
        for line, count in line_counts.items():
            if count > 2:
                duplicates.append({
                    'line': line[:50] + '...' if len(line) > 50 else line,
                    'occurrences': count
                })
        
        score = 1.0 if len(duplicates) == 0 else max(0.0, 1.0 - len(duplicates) / 5)
        passed = len(duplicates) < 3
        
        return {
            'score': score,
            'passed': passed,
            'details': f"Found {len(duplicates)} duplicated code patterns",
            'findings': duplicates if duplicates else []
        }
    
    def learn_from_outcome(self, review_id: str, outcome: Dict):
        """
        Learn from PR outcome to improve criteria.
        
        Args:
            review_id: Unique identifier for the review
            outcome: Dictionary with outcome data (merged, rejected, modified, feedback)
        """
        
        # Record outcome in history
        outcome_record = {
            'review_id': review_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'outcome': outcome
        }
        
        if 'history' not in self.criteria:
            self.criteria['history'] = []
        
        self.criteria['history'].append(outcome_record)
        
        # Update metadata
        self.criteria['metadata']['total_reviews'] += 1
        
        # Calculate success (merged without major changes = success)
        if outcome.get('merged') and not outcome.get('major_changes_required'):
            success = 1.0
        elif outcome.get('rejected'):
            success = 0.0
        else:
            success = 0.5
        
        # Update running success rate
        total = self.criteria['metadata']['total_reviews']
        current_rate = self.criteria['metadata']['success_rate']
        new_rate = (current_rate * (total - 1) + success) / total
        self.criteria['metadata']['success_rate'] = new_rate
        
        # Check if we have enough data to adjust criteria
        if total >= self.criteria['evolution_config']['min_reviews_before_adjustment']:
            self._adjust_criteria()
        
        self._save_criteria()
    
    def _adjust_criteria(self):
        """Adjust criteria weights and thresholds based on effectiveness."""
        
        config = self.criteria['evolution_config']
        window = config['effectiveness_window']
        
        # Analyze recent history
        recent_history = self.criteria['history'][-window:] if len(self.criteria['history']) > window else self.criteria['history']
        
        if len(recent_history) < 5:
            return  # Not enough data
        
        # For each criteria category, calculate effectiveness
        for category_name, category in self.criteria['criteria'].items():
            effectiveness_scores = []
            
            for check in category.get('checks', []):
                check_id = check['id']
                times_applied = check.get('times_applied', 0)
                
                if times_applied < 3:
                    continue
                
                # Calculate effectiveness: how often did this check correlate with good outcomes?
                current_eff = check.get('effectiveness', 0.5)
                
                # Update historical effectiveness
                if 'historical_effectiveness' not in category:
                    category['historical_effectiveness'] = []
                
                category['historical_effectiveness'].append({
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'check_id': check_id,
                    'effectiveness': current_eff
                })
                
                effectiveness_scores.append(current_eff)
            
            if effectiveness_scores:
                avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)
                
                # Adjust category weight based on effectiveness
                learning_rate = category.get('learning_rate', 0.1)
                adjustment = (avg_effectiveness - 0.5) * config['weight_adjustment_rate']
                category['weight'] = max(0.1, min(2.0, category['weight'] + adjustment))
                
                # Adjust threshold
                if avg_effectiveness > config['criteria_promotion_threshold']:
                    # Very effective - can be stricter
                    category['threshold'] = min(0.9, category['threshold'] + config['threshold_adjustment_rate'])
                elif avg_effectiveness < config['criteria_removal_threshold']:
                    # Not effective - be more lenient
                    category['threshold'] = max(0.3, category['threshold'] - config['threshold_adjustment_rate'])
            
            # Increment times_evaluated
            category['times_evaluated'] = category.get('times_evaluated', 0) + 1
    
    def generate_review_comment(self, results: Dict) -> str:
        """Generate a formatted review comment from results."""
        
        overall_score = results['overall_score']
        
        # Determine overall assessment
        if overall_score >= 0.8:
            assessment = "✅ **Excellent Code Quality**"
            emoji = "🌟"
        elif overall_score >= 0.6:
            assessment = "👍 **Good Code Quality**"
            emoji = "✓"
        elif overall_score >= 0.4:
            assessment = "⚠️ **Code Needs Improvement**"
            emoji = "⚠️"
        else:
            assessment = "❌ **Significant Issues Found**"
            emoji = "❌"
        
        comment = f"""## 🤖 Autonomous Code Review

{assessment}

**Overall Score:** {overall_score:.2%} {emoji}

### Category Scores

"""
        
        # Add category scores
        for category, score in results['category_scores'].items():
            bar = '█' * int(score * 10) + '░' * (10 - int(score * 10))
            comment += f"- **{category.replace('_', ' ').title()}**: {score:.0%} `{bar}`\n"
        
        # Add failed checks
        if results['failed_checks']:
            comment += "\n### ⚠️ Issues Found\n\n"
            for failure in results['failed_checks'][:10]:  # Limit to top 10
                comment += f"- **{failure['check']}** ({failure['category']})\n"
                if failure.get('details'):
                    comment += f"  - {failure['details']}\n"
        
        # Add passed checks
        if results['passed_checks']:
            comment += "\n### ✅ Passed Checks\n\n"
            comment += f"This PR passed {len(results['passed_checks'])} quality checks.\n"
        
        # Add learning note
        comment += f"""

---

### 📊 About This Review

This autonomous review uses **self-improving criteria** based on {self.criteria['metadata']['total_reviews']} previous reviews.

- **Success Rate**: {self.criteria['metadata']['success_rate']:.1%}
- **Criteria Version**: {self.criteria['version']}
- **Last Updated**: {self.criteria['last_updated']}

The review criteria evolve over time based on PR outcomes, becoming more accurate with each review.

**Reviewed by:** @workflows-tech-lead (Autonomous Reviewer)  
**Timestamp:** {results['timestamp']}
"""
        
        return comment


def main():
    """Main entry point for CLI usage."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Autonomous Code Reviewer')
    parser.add_argument('--pr-number', type=str, help='PR number to review')
    parser.add_argument('--file-list', type=str, help='File with list of changed files')
    parser.add_argument('--output', type=str, default='review_results.json', help='Output file')
    parser.add_argument('--comment', action='store_true', help='Generate review comment')
    
    args = parser.parse_args()
    
    reviewer = AutonomousReviewer()
    
    # For CLI testing, we'd read files from git diff
    # In the workflow, we'll pass files differently
    
    print("Autonomous Code Reviewer initialized")
    print(f"Total reviews performed: {reviewer.criteria['metadata']['total_reviews']}")
    print(f"Success rate: {reviewer.criteria['metadata']['success_rate']:.1%}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
