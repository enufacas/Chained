#!/usr/bin/env python3
"""
Archaeology Integration Helpers

Provides integration between archaeology learning system and
GitHub workflows (PR reviews, issue planning, preventive maintenance).
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import archaeology learner
import importlib.util
spec = importlib.util.spec_from_file_location(
    "archaeology_learner",
    os.path.join(os.path.dirname(__file__), "archaeology-learner.py")
)
archaeology_learner_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archaeology_learner_module)
ArchaeologyLearner = archaeology_learner_module.ArchaeologyLearner


class ArchaeologyIntegration:
    """Integration helpers for archaeology system with GitHub workflows"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.learner = ArchaeologyLearner(repo_path=repo_path)
        
    def analyze_pr_changes(self, files_changed: List[str], pr_description: str = "") -> Dict:
        """
        Analyze PR changes and provide archaeology insights
        
        Args:
            files_changed: List of files modified in the PR
            pr_description: PR description text
            
        Returns:
            Dictionary with insights, risks, and recommendations
        """
        # Extract characteristics from PR
        characteristics = self._extract_pr_characteristics(files_changed, pr_description)
        
        # Assess risk
        risk_assessment = self.learner.assess_risk(characteristics, files_changed)
        
        # Predict outcome
        prediction = self.learner.predict_outcome(characteristics)
        
        # Find similar historical changes
        similar_changes = self.learner.find_similar_changes(characteristics, max_results=3)
        
        # Search for relevant knowledge
        relevant_knowledge = []
        for file in files_changed[:5]:  # Check first 5 files
            ext = Path(file).suffix
            if ext:
                kb_results = self.learner.search_knowledge_base(ext.replace('.', ''))
                relevant_knowledge.extend(kb_results)
        
        return {
            "risk_assessment": risk_assessment,
            "prediction": prediction,
            "similar_changes": similar_changes,
            "relevant_knowledge": relevant_knowledge[:5],  # Top 5 results
            "characteristics": characteristics,
            "pr_insights": self._generate_pr_insights(
                risk_assessment, prediction, similar_changes, files_changed
            )
        }
    
    def _extract_pr_characteristics(self, files_changed: List[str], pr_description: str) -> Dict:
        """Extract commit characteristics from PR"""
        desc_lower = pr_description.lower()
        
        return {
            "is_refactor": any(kw in desc_lower for kw in ['refactor', 'restructure', 'reorganize']),
            "is_feature": any(kw in desc_lower for kw in ['add', 'implement', 'create', 'new feature']),
            "is_bug_fix": any(kw in desc_lower for kw in ['fix', 'bug', 'issue', 'resolve']),
            "has_tests": any('test' in f.lower() for f in files_changed),
            "large_change": len(files_changed) > 10,
            "has_documentation": any(kw in desc_lower for kw in ['why', 'because', 'decided to', 'reason'])
        }
    
    def _generate_pr_insights(
        self,
        risk: Dict,
        prediction: Dict,
        similar: List[Dict],
        files: List[str]
    ) -> str:
        """Generate human-readable insights for PR"""
        insights = []
        
        # Risk summary
        risk_emoji = {"low": "✅", "medium": "⚠️", "high": "🚨"}
        insights.append(f"{risk_emoji.get(risk['risk_level'], '❓')} **Risk Level**: {risk['risk_level'].upper()}")
        insights.append(f"   - Success probability: {risk['success_probability']:.1%}")
        
        if risk['risk_factors']:
            insights.append("   - Risk factors:")
            for factor in risk['risk_factors'][:3]:
                insights.append(f"     - {factor}")
        
        # Prediction
        pred_emoji = {
            "success": "✅",
            "likely_needs_fixes": "⚠️",
            "uncertain": "❓",
            "unknown": "❔"
        }
        insights.append(f"\n{pred_emoji.get(prediction['prediction'], '❔')} **Prediction**: {prediction['prediction'].replace('_', ' ').title()}")
        insights.append(f"   - {prediction['reasoning']}")
        
        # Similar changes
        if similar:
            insights.append(f"\n📚 **Similar Historical Changes**:")
            for i, change in enumerate(similar[:3], 1):
                outcome_emoji = "✅" if change['outcome'] == 'success' else "❌"
                insights.append(f"{i}. {outcome_emoji} `{change['commit_hash']}`: {change['subject']}")
                insights.append(f"   - Similarity: {change['similarity']:.1%}")
                if change['lessons_learned']:
                    insights.append(f"   - Key lesson: {change['lessons_learned'][0]}")
        
        # Recommendation
        if risk['recommendation']:
            insights.append(f"\n💡 **Recommendation**:")
            insights.append(f"   {risk['recommendation']}")
        
        return '\n'.join(insights)
    
    def plan_issue_work(self, issue_title: str, issue_description: str) -> Dict:
        """
        Provide planning assistance for an issue based on historical data
        
        Args:
            issue_title: Title of the issue
            issue_description: Issue description
            
        Returns:
            Dictionary with timeline estimates, similar work, and recommendations
        """
        # Determine work type
        desc_lower = f"{issue_title} {issue_description}".lower()
        
        if any(kw in desc_lower for kw in ['feature', 'implement', 'add', 'new']):
            work_type = "feature"
        elif any(kw in desc_lower for kw in ['refactor', 'improve', 'optimize']):
            work_type = "refactor"
        elif any(kw in desc_lower for kw in ['fix', 'bug', 'issue', 'error']):
            work_type = "bugfix"
        else:
            work_type = "feature"  # Default
        
        # Estimate timeline
        estimated_files = self._estimate_files_affected(issue_description)
        timeline = self.learner.estimate_timeline(work_type, files_count=estimated_files)
        
        # Search for relevant knowledge
        keywords = self._extract_keywords(issue_title)
        relevant_knowledge = []
        for keyword in keywords[:3]:
            kb_results = self.learner.search_knowledge_base(keyword)
            relevant_knowledge.extend(kb_results)
        
        # Find similar past work
        characteristics = {
            "is_feature": work_type == "feature",
            "is_refactor": work_type == "refactor",
            "is_bug_fix": work_type == "bugfix"
        }
        similar_work = self.learner.find_similar_changes(characteristics, max_results=5)
        
        return {
            "work_type": work_type,
            "timeline_estimate": timeline,
            "similar_past_work": similar_work,
            "relevant_knowledge": relevant_knowledge[:5],
            "estimated_files_affected": estimated_files,
            "planning_insights": self._generate_planning_insights(
                work_type, timeline, similar_work, relevant_knowledge
            )
        }
    
    def _estimate_files_affected(self, description: str) -> int:
        """Estimate number of files that will be affected"""
        desc_lower = description.lower()
        
        # Heuristics based on description
        if any(kw in desc_lower for kw in ['large', 'major', 'significant', 'multiple']):
            return 8
        elif any(kw in desc_lower for kw in ['small', 'minor', 'single', 'quick']):
            return 2
        else:
            return 4  # Default medium size
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for knowledge base search"""
        # Simple keyword extraction (could be enhanced with NLP)
        text_lower = text.lower()
        
        keywords = []
        common_tech_words = [
            'api', 'test', 'database', 'auth', 'security', 'performance',
            'refactor', 'feature', 'bug', 'workflow', 'documentation'
        ]
        
        for word in common_tech_words:
            if word in text_lower:
                keywords.append(word)
        
        return keywords
    
    def _generate_planning_insights(
        self,
        work_type: str,
        timeline: Dict,
        similar: List[Dict],
        knowledge: List[Dict]
    ) -> str:
        """Generate planning insights for issue"""
        insights = []
        
        # Timeline
        if timeline['estimated_days']:
            insights.append(f"⏱️ **Estimated Timeline**: {timeline['estimated_days']} days")
            insights.append(f"   - Range: {timeline['range']}")
            insights.append(f"   - Confidence: {timeline['confidence']}")
            insights.append(f"   - {timeline['reasoning']}")
        else:
            insights.append(f"⏱️ **Timeline**: {timeline['reasoning']}")
        
        # Similar work
        if similar:
            insights.append(f"\n📋 **Similar Past Work**:")
            success_count = sum(1 for s in similar if s['outcome'] == 'success')
            insights.append(f"   - Found {len(similar)} similar tasks ({success_count} successful)")
            
            for i, work in enumerate(similar[:3], 1):
                outcome_emoji = "✅" if work['outcome'] == 'success' else "❌"
                insights.append(f"   {i}. {outcome_emoji} `{work['commit_hash']}`: {work['subject']}")
        
        # Knowledge base insights
        best_practices = [k for k in knowledge if k.get('type') == 'best_practice']
        pitfalls = [k for k in knowledge if k.get('type') == 'common_pitfall']
        
        if best_practices:
            insights.append(f"\n💡 **Best Practices**:")
            for practice in best_practices[:2]:
                insights.append(f"   - {practice['content']}")
        
        if pitfalls:
            insights.append(f"\n⚠️ **Common Pitfalls to Avoid**:")
            for pitfall in pitfalls[:2]:
                insights.append(f"   - {pitfall['content']}")
        
        return '\n'.join(insights)
    
    def suggest_preventive_maintenance(self) -> List[Dict]:
        """
        Analyze patterns to suggest preventive maintenance
        
        Returns:
            List of maintenance suggestions with priority
        """
        suggestions = []
        
        # Get evolution patterns
        patterns = self.learner.patterns_data.get("patterns", {})
        evolution_patterns = patterns.get("evolution", [])
        
        # High churn files need attention
        high_churn = [
            p for p in evolution_patterns
            if p.get("change_frequency") in ["very_frequent", "frequent"]
        ]
        
        for pattern in high_churn[:5]:
            suggestions.append({
                "priority": "high",
                "type": "high_churn",
                "title": f"Review frequently changing file: {pattern['file']}",
                "description": f"This file has changed {pattern['changes_count']} times. Consider refactoring for stability.",
                "file": pattern['file'],
                "action": "Create issue to review and stabilize this component"
            })
        
        # Files with bug patterns
        failure_patterns = patterns.get("failure", [])
        files_with_issues = {}
        for pattern in failure_patterns:
            for file in pattern.get("files_changed", []):
                files_with_issues[file] = files_with_issues.get(file, 0) + 1
        
        for file, issue_count in sorted(files_with_issues.items(), key=lambda x: x[1], reverse=True)[:5]:
            if issue_count > 1:
                suggestions.append({
                    "priority": "medium",
                    "type": "bug_prone",
                    "title": f"Bug-prone file needs attention: {file}",
                    "description": f"This file has been involved in {issue_count} failed changes. May need quality improvements.",
                    "file": file,
                    "action": "Add tests or refactor to improve reliability"
                })
        
        # Old components that haven't been touched
        insights = self.learner.patterns_data.get("insights", [])
        for insight in insights:
            if insight.get("type") == "high_churn" and insight.get("actionable"):
                suggestions.append({
                    "priority": "medium",
                    "type": "maintenance",
                    "title": insight["title"],
                    "description": insight["description"],
                    "action": "Schedule regular maintenance review"
                })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return suggestions
    
    def generate_pr_comment(self, files_changed: List[str], pr_description: str = "") -> str:
        """Generate a formatted comment for PR with archaeology insights"""
        analysis = self.analyze_pr_changes(files_changed, pr_description)
        
        comment = ["## 🏛️ Code Archaeology Insights\n"]
        comment.append(analysis["pr_insights"])
        
        # Add footer
        comment.append("\n---")
        comment.append("*Insights provided by Code Archaeology Active Learning System*")
        comment.append("*Based on historical pattern analysis*")
        
        return '\n'.join(comment)
    
    def generate_issue_comment(self, issue_title: str, issue_description: str) -> str:
        """Generate a formatted comment for issue with planning insights"""
        planning = self.plan_issue_work(issue_title, issue_description)
        
        comment = ["## 🏛️ Code Archaeology Planning Insights\n"]
        comment.append(planning["planning_insights"])
        
        # Add footer
        comment.append("\n---")
        comment.append("*Planning assistance provided by Code Archaeology Active Learning System*")
        comment.append("*Based on historical data analysis*")
        
        return '\n'.join(comment)


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Archaeology Integration Helpers - Connect archaeology learning to workflows'
    )
    parser.add_argument(
        'command',
        choices=['analyze-pr', 'plan-issue', 'suggest-maintenance'],
        help='Command to run'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='List of files changed (for analyze-pr)'
    )
    parser.add_argument(
        '--description',
        help='PR or issue description'
    )
    parser.add_argument(
        '--title',
        help='Issue title (for plan-issue)'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory (default: current directory)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'markdown'],
        default='markdown',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    integration = ArchaeologyIntegration(repo_path=args.directory)
    
    if args.command == 'analyze-pr':
        if not args.files:
            print("Error: --files required for analyze-pr", file=sys.stderr)
            sys.exit(1)
        
        result = integration.analyze_pr_changes(args.files, args.description or "")
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(integration.generate_pr_comment(args.files, args.description or ""))
    
    elif args.command == 'plan-issue':
        if not args.title:
            print("Error: --title required for plan-issue", file=sys.stderr)
            sys.exit(1)
        
        result = integration.plan_issue_work(args.title, args.description or "")
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(integration.generate_issue_comment(args.title, args.description or ""))
    
    elif args.command == 'suggest-maintenance':
        suggestions = integration.suggest_preventive_maintenance()
        
        if args.format == 'json':
            print(json.dumps(suggestions, indent=2))
        else:
            print("## 🔧 Preventive Maintenance Suggestions\n")
            for i, suggestion in enumerate(suggestions, 1):
                priority_emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}
                print(f"{i}. {priority_emoji.get(suggestion['priority'], '•')} **[{suggestion['priority'].upper()}]** {suggestion['title']}")
                print(f"   - {suggestion['description']}")
                print(f"   - Action: {suggestion['action']}\n")


if __name__ == '__main__':
    main()
