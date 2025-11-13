#!/usr/bin/env python3
"""
Workflow Harmonizer - Orchestration and Coordination Tool
Created by @harmonize-wizard (George Martin)

This tool brings harmony to the workflow ecosystem by:
- Monitoring workflow health and performance
- Detecting workflow conflicts and dependencies
- Optimizing workflow scheduling
- Providing coordination insights
"""

import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import re


class WorkflowHarmonizer:
    """Orchestrate and harmonize GitHub Actions workflows."""
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows: Dict[str, Dict] = {}
        self.schedule_map: Dict[str, List[str]] = defaultdict(list)
        self.trigger_map: Dict[str, Set[str]] = defaultdict(set)
        
    def load_workflows(self) -> None:
        """Load all workflow definitions from the workflows directory."""
        if not self.workflows_dir.exists():
            raise FileNotFoundError(f"Workflows directory not found: {self.workflows_dir}")
        
        for workflow_file in self.workflows_dir.glob("*.yml"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                    if workflow_data:
                        # YAML parses 'on:' as True (boolean)
                        # GitHub Actions uses 'on' as the trigger key
                        on_config = workflow_data.get('on') or workflow_data.get(True)
                        
                        self.workflows[workflow_file.stem] = {
                            'name': workflow_data.get('name', workflow_file.stem),
                            'file': workflow_file.name,
                            'data': workflow_data,
                            'on': on_config
                        }
            except Exception as e:
                print(f"⚠️  Warning: Could not parse {workflow_file.name}: {e}")
    
    def analyze_schedules(self) -> Dict[str, List[Tuple[str, str]]]:
        """Analyze workflow schedules and identify potential conflicts."""
        schedule_timeline = defaultdict(list)
        
        for workflow_id, workflow in self.workflows.items():
            on_config = workflow.get('on', {})
            
            # Handle both string and dict 'on' configurations
            if isinstance(on_config, str):
                on_config = {on_config: {}}
            elif not isinstance(on_config, dict):
                continue
            
            if 'schedule' in on_config:
                schedules = on_config['schedule']
                if not isinstance(schedules, list):
                    schedules = [schedules]
                
                for schedule in schedules:
                    if isinstance(schedule, dict):
                        cron = schedule.get('cron', '')
                    else:
                        cron = str(schedule)
                    
                    if cron:
                        # Parse cron to estimate frequency
                        frequency = self._parse_cron_frequency(cron)
                        schedule_timeline[frequency].append((
                            workflow['name'],
                            cron
                        ))
                        self.schedule_map[workflow_id].append(cron)
        
        return dict(schedule_timeline)
    
    def _parse_cron_frequency(self, cron: str) -> str:
        """Convert cron expression to human-readable frequency."""
        parts = cron.split()
        if len(parts) < 5:
            return "unknown"
        
        minute, hour, day, month, weekday = parts[:5]
        
        # Determine frequency
        if minute.startswith('*/'):
            interval = minute[2:]
            return f"every_{interval}_minutes"
        elif hour.startswith('*/'):
            interval = hour[2:]
            return f"every_{interval}_hours"
        elif hour.isdigit() and minute.isdigit():
            return f"daily_at_{hour}:{minute}"
        elif weekday.isdigit():
            return f"weekly_on_day_{weekday}"
        else:
            return "custom_schedule"
    
    def analyze_triggers(self) -> Dict[str, List[str]]:
        """Analyze workflow triggers and identify dependencies."""
        trigger_analysis = defaultdict(list)
        
        for workflow_id, workflow in self.workflows.items():
            on_config = workflow.get('on', {})
            
            # Handle string triggers (single trigger)
            if isinstance(on_config, str):
                trigger_analysis[on_config].append(workflow['name'])
                self.trigger_map[workflow_id].add(on_config)
            # Handle list of triggers
            elif isinstance(on_config, list):
                for trigger in on_config:
                    trigger_analysis[trigger].append(workflow['name'])
                    self.trigger_map[workflow_id].add(trigger)
            # Handle dict of triggers with configuration
            elif isinstance(on_config, dict):
                for trigger_type in on_config.keys():
                    trigger_analysis[trigger_type].append(workflow['name'])
                    self.trigger_map[workflow_id].add(trigger_type)
        
        return dict(trigger_analysis)
    
    def detect_conflicts(self) -> List[Dict[str, any]]:
        """Detect potential workflow conflicts and resource contention."""
        conflicts = []
        
        # Check for workflows scheduled at the same time
        schedules = self.analyze_schedules()
        for frequency, workflows in schedules.items():
            if len(workflows) > 3:
                conflicts.append({
                    'type': 'schedule_congestion',
                    'severity': 'medium',
                    'frequency': frequency,
                    'workflows': [w[0] for w in workflows],
                    'count': len(workflows),
                    'recommendation': 'Consider staggering these workflows to reduce resource contention'
                })
        
        # Check for workflows with overlapping triggers
        triggers = self.analyze_triggers()
        for trigger_type, workflow_names in triggers.items():
            if len(workflow_names) > 5:
                conflicts.append({
                    'type': 'trigger_overload',
                    'severity': 'low',
                    'trigger': trigger_type,
                    'workflows': workflow_names,
                    'count': len(workflow_names),
                    'recommendation': f'Multiple workflows trigger on {trigger_type} - ensure this is intentional'
                })
        
        return conflicts
    
    def generate_health_report(self) -> Dict[str, any]:
        """Generate a comprehensive workflow health report."""
        self.load_workflows()
        
        report = {
            'timestamp': datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None).replace(tzinfo=None).isoformat() if hasattr(datetime, 'UTC') else datetime.utcnow().isoformat(),
            'summary': {
                'total_workflows': len(self.workflows),
                'scheduled_workflows': sum(1 for w in self.workflows.values() 
                                          if 'schedule' in str(w.get('on', {}))),
                'event_triggered': sum(1 for w in self.workflows.values() 
                                      if any(t in str(w.get('on', {})) 
                                            for t in ['push', 'pull_request', 'issues'])),
                'manual_only': sum(1 for w in self.workflows.values() 
                                  if w.get('on') == ['workflow_dispatch'] or 
                                  (isinstance(w.get('on'), dict) and 
                                   list(w.get('on', {}).keys()) == ['workflow_dispatch']))
            },
            'schedule_analysis': self.analyze_schedules(),
            'trigger_analysis': self.analyze_triggers(),
            'conflicts': self.detect_conflicts(),
            'workflow_list': []
        }
        
        # Add detailed workflow information
        for workflow_id, workflow in sorted(self.workflows.items()):
            workflow_info = {
                'id': workflow_id,
                'name': workflow['name'],
                'file': workflow['file'],
                'triggers': list(self.trigger_map.get(workflow_id, [])),
                'schedules': self.schedule_map.get(workflow_id, []),
                'concurrency': workflow['data'].get('concurrency', {})
            }
            report['workflow_list'].append(workflow_info)
        
        return report
    
    def generate_coordination_recommendations(self) -> List[str]:
        """Generate recommendations for workflow coordination."""
        recommendations = []
        
        schedules = self.analyze_schedules()
        
        # High-frequency schedules
        high_freq = [freq for freq, workflows in schedules.items() 
                    if 'minutes' in freq and len(workflows) > 0]
        if len(high_freq) > 5:
            recommendations.append(
                "⚠️  Consider consolidating high-frequency workflows (every X minutes) "
                "into fewer, more efficient workflows to reduce GitHub Actions usage."
            )
        
        # Check for daily workflows clustered at same time
        daily_workflows = [freq for freq in schedules.keys() if 'daily' in freq]
        if len(daily_workflows) > 3:
            recommendations.append(
                "💡 Multiple daily workflows detected. Consider staggering their "
                "execution times throughout the day for better resource distribution."
            )
        
        # Check for workflows without concurrency control
        no_concurrency = [w['name'] for w in self.workflows.values() 
                         if 'concurrency' not in w['data']]
        if len(no_concurrency) > len(self.workflows) * 0.5:
            recommendations.append(
                "🔧 Many workflows lack concurrency control. Adding concurrency groups "
                "can prevent duplicate runs and save resources."
            )
        
        return recommendations
    
    def export_report(self, output_file: str = "workflow_health_report.json") -> None:
        """Export the health report to a JSON file."""
        report = self.generate_health_report()
        report['recommendations'] = self.generate_coordination_recommendations()
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Workflow health report exported to: {output_path}")
    
    def print_summary(self) -> None:
        """Print a summary of the workflow ecosystem."""
        self.load_workflows()
        report = self.generate_health_report()
        
        print("\n" + "="*70)
        print("🎼 Workflow Harmonizer - Ecosystem Summary")
        print("="*70)
        print(f"\n📊 Workflow Statistics:")
        print(f"   Total Workflows: {report['summary']['total_workflows']}")
        print(f"   Scheduled: {report['summary']['scheduled_workflows']}")
        print(f"   Event-Triggered: {report['summary']['event_triggered']}")
        print(f"   Manual Only: {report['summary']['manual_only']}")
        
        print(f"\n⏰ Schedule Distribution:")
        for frequency, workflows in sorted(report['schedule_analysis'].items()):
            print(f"   {frequency}: {len(workflows)} workflow(s)")
        
        print(f"\n🎯 Trigger Distribution:")
        for trigger, workflows in sorted(report['trigger_analysis'].items())[:10]:
            print(f"   {trigger}: {len(workflows)} workflow(s)")
        
        conflicts = report['conflicts']
        if conflicts:
            print(f"\n⚠️  Detected {len(conflicts)} Potential Conflicts:")
            for conflict in conflicts[:5]:
                print(f"   - {conflict['type']}: {conflict.get('count', 0)} workflows")
        else:
            print(f"\n✅ No workflow conflicts detected")
        
        recommendations = self.generate_coordination_recommendations()
        if recommendations:
            print(f"\n💡 Coordination Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Main entry point for the workflow harmonizer."""
    harmonizer = WorkflowHarmonizer()
    
    try:
        harmonizer.print_summary()
        harmonizer.export_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
