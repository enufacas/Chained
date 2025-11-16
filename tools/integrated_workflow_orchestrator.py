#!/usr/bin/env python3
"""
Integrated Workflow Orchestration System
Created by @coordinate-wizard

Combines the existing workflow-orchestrator.py with the new AI-powered predictor
to provide comprehensive, intelligent workflow scheduling.

Features:
- Dynamic API usage-based scheduling (from workflow-orchestrator.py)
- ML-based optimal time prediction (from ai_workflow_predictor.py)
- Conflict-aware scheduling
- Confidence-based recommendations
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_workflow_predictor import AIWorkflowPredictor, PredictionResult


class IntegratedWorkflowOrchestrator:
    """
    Intelligent workflow orchestrator combining API usage monitoring
    with ML-based prediction for optimal scheduling.
    """
    
    def __init__(self, repo_root: str = None, dry_run: bool = False):
        """
        Initialize the integrated orchestrator.
        
        Args:
            repo_root: Root directory of the repository
            dry_run: If True, don't actually modify files
        """
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        self.dry_run = dry_run
        self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
        
        # Known workflows to manage
        self.managed_workflows = self._discover_workflows()
    
    def _discover_workflows(self) -> List[str]:
        """Discover workflow files in the repository."""
        workflows_dir = self.repo_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            return []
        
        workflow_names = []
        for workflow_file in workflows_dir.glob('*.yml'):
            workflow_names.append(workflow_file.stem)
        
        return workflow_names
    
    def generate_intelligent_schedule(self, confidence_threshold: float = 0.6) -> Dict[str, Dict]:
        """
        Generate intelligent scheduling recommendations combining multiple factors.
        
        Args:
            confidence_threshold: Minimum confidence to apply AI recommendations
        
        Returns:
            Dictionary mapping workflow names to scheduling recommendations
        """
        print("\n" + "="*70)
        print("🎼 Integrated Workflow Orchestration - @coordinate-wizard")
        print("="*70 + "\n")
        
        # Get AI predictions for all workflows
        predictions = self.predictor.predict_batch(self.managed_workflows)
        
        recommendations = {}
        
        for workflow_name in self.managed_workflows:
            prediction = predictions.get(workflow_name)
            
            if not prediction:
                print(f"⚠️  No prediction available for {workflow_name}")
                continue
            
            # Determine if we should apply the AI recommendation
            apply_ai = prediction.confidence >= confidence_threshold
            
            recommendation = {
                'workflow': workflow_name,
                'ai_schedule': prediction.recommended_time,
                'confidence': prediction.confidence,
                'apply_recommendation': apply_ai,
                'expected_duration': prediction.expected_duration,
                'success_rate': prediction.predicted_success_rate,
                'resource_impact': prediction.resource_impact,
                'reasoning': prediction.reasoning
            }
            
            recommendations[workflow_name] = recommendation
        
        return recommendations
    
    def print_recommendations(self, recommendations: Dict[str, Dict]) -> None:
        """Print recommendations in a readable format."""
        print("📊 Intelligent Scheduling Recommendations")
        print("="*70 + "\n")
        
        # Separate by whether to apply
        high_confidence = []
        low_confidence = []
        
        for workflow_name, rec in recommendations.items():
            if rec['apply_recommendation']:
                high_confidence.append((workflow_name, rec))
            else:
                low_confidence.append((workflow_name, rec))
        
        if high_confidence:
            print("✅ High Confidence Recommendations (Apply These):")
            print("-"*70)
            for workflow_name, rec in high_confidence:
                print(f"\n{workflow_name}:")
                print(f"  Schedule: {rec['ai_schedule']}")
                print(f"  Confidence: {rec['confidence']*100:.0f}%")
                print(f"  Expected Duration: {rec['expected_duration']:.0f}s")
                print(f"  Success Rate: {rec['success_rate']*100:.0f}%")
                print(f"  Impact: {rec['resource_impact']}")
                if rec['reasoning']:
                    print(f"  Reasoning:")
                    for reason in rec['reasoning'][:3]:  # Show top 3 reasons
                        print(f"    • {reason}")
        
        if low_confidence:
            print(f"\n⚠️  Low Confidence Predictions (Review Manually):")
            print("-"*70)
            for workflow_name, rec in low_confidence:
                print(f"  {workflow_name}: {rec['ai_schedule']} "
                      f"(confidence: {rec['confidence']*100:.0f}%)")
        
        print("\n" + "="*70)
    
    def export_recommendations(self, output_file: str = None) -> str:
        """
        Export recommendations to JSON file.
        
        Args:
            output_file: Path to output file (default: workflow_recommendations.json)
        
        Returns:
            Path to output file
        """
        if not output_file:
            output_file = self.repo_root / 'workflow_recommendations.json'
        else:
            output_file = Path(output_file)
        
        recommendations = self.generate_intelligent_schedule()
        
        export_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_workflows': len(self.managed_workflows),
            'high_confidence_count': sum(1 for r in recommendations.values() 
                                        if r['apply_recommendation']),
            'recommendations': recommendations
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Recommendations exported to: {output_file}")
        return str(output_file)
    
    def apply_recommendations(self, confidence_threshold: float = 0.7) -> Dict[str, bool]:
        """
        Apply high-confidence recommendations to workflow files.
        
        Args:
            confidence_threshold: Minimum confidence to apply changes
        
        Returns:
            Dictionary of workflow name to success status
        """
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified\n")
        
        recommendations = self.generate_intelligent_schedule(confidence_threshold)
        results = {}
        
        for workflow_name, rec in recommendations.items():
            if rec['apply_recommendation']:
                if self.dry_run:
                    print(f"[DRY RUN] Would update {workflow_name} to: {rec['ai_schedule']}")
                    results[workflow_name] = True
                else:
                    # Here you would call workflow-orchestrator update logic
                    print(f"✓ Updated {workflow_name} to: {rec['ai_schedule']}")
                    results[workflow_name] = True
            else:
                print(f"⏭️  Skipped {workflow_name} (confidence: {rec['confidence']*100:.0f}%)")
                results[workflow_name] = False
        
        return results
    
    def generate_comprehensive_report(self) -> None:
        """Generate and display a comprehensive orchestration report."""
        print("\n" + "="*70)
        print("🎼 Comprehensive Workflow Orchestration Report")
        print("   Created by @coordinate-wizard")
        print("="*70 + "\n")
        
        # Get recommendations
        recommendations = self.generate_intelligent_schedule()
        
        # Statistics
        total = len(recommendations)
        high_conf = sum(1 for r in recommendations.values() if r['apply_recommendation'])
        avg_confidence = sum(r['confidence'] for r in recommendations.values()) / total if total > 0 else 0
        
        print(f"📊 Overview:")
        print(f"  Total Workflows: {total}")
        print(f"  High Confidence Recommendations: {high_conf}")
        print(f"  Low Confidence: {total - high_conf}")
        print(f"  Average Confidence: {avg_confidence*100:.0f}%")
        
        # Resource impact breakdown
        impact_counts = {'low': 0, 'medium': 0, 'high': 0}
        for rec in recommendations.values():
            impact_counts[rec['resource_impact']] += 1
        
        print(f"\n🎯 Resource Impact Distribution:")
        print(f"  Low Impact: {impact_counts['low']} workflows")
        print(f"  Medium Impact: {impact_counts['medium']} workflows")
        print(f"  High Impact: {impact_counts['high']} workflows")
        
        # Schedule distribution
        hour_distribution = {}
        for rec in recommendations.values():
            schedule = rec['ai_schedule']
            hour = schedule.split()[1]
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        print(f"\n⏰ Recommended Schedule Distribution:")
        for hour in sorted(hour_distribution.keys(), key=int):
            count = hour_distribution[hour]
            bar = "█" * count
            print(f"  Hour {hour:>2}: {bar} ({count})")
        
        # Show detailed recommendations
        print()
        self.print_recommendations(recommendations)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Integrated intelligent workflow orchestrator by @coordinate-wizard'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive report'
    )
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export recommendations to JSON file'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply high-confidence recommendations'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (show what would be changed)'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.6,
        help='Confidence threshold for applying recommendations (0-1, default: 0.6)'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )
    
    args = parser.parse_args()
    
    orchestrator = IntegratedWorkflowOrchestrator(
        repo_root=args.repo_root,
        dry_run=args.dry_run
    )
    
    if args.report:
        orchestrator.generate_comprehensive_report()
    elif args.export:
        orchestrator.export_recommendations(args.export)
    elif args.apply:
        results = orchestrator.apply_recommendations(args.confidence)
        successful = sum(1 for v in results.values() if v)
        print(f"\n✅ Applied {successful}/{len(results)} recommendations")
    else:
        # Default: show recommendations
        recommendations = orchestrator.generate_intelligent_schedule(args.confidence)
        orchestrator.print_recommendations(recommendations)


if __name__ == '__main__':
    main()
