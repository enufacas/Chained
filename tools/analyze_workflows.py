#!/usr/bin/env python3
"""
Analyze GitHub Actions workflows to generate accurate workflow-schedule.html data.

This script extracts workflow metadata including:
- Schedule triggers (cron expressions)
- Manual triggers (workflow_dispatch)
- Total counts and categorization
- 24-hour schedule view
"""

import os
import yaml
import re
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

def parse_cron(cron_expr):
    """Parse cron expression to extract hour and minute."""
    # Cron format: minute hour day month weekday
    parts = cron_expr.strip().split()
    if len(parts) >= 2:
        minute = parts[0]
        hour = parts[1]
        return hour, minute
    return None, None

def get_schedule_info(workflow_data, workflow_name):
    """Extract schedule information from workflow data."""
    schedules = []
    manual_only = False
    
    # YAML quirk: 'on' can be parsed as True (boolean)
    triggers = workflow_data.get('on') or workflow_data.get(True)
    
    if triggers:
        # Handle both dict and list formats
        if isinstance(triggers, dict):
            if 'schedule' in triggers:
                schedule_list = triggers['schedule']
                for sched in schedule_list:
                    if 'cron' in sched:
                        cron = sched['cron']
                        hour, minute = parse_cron(cron)
                        if hour and minute:
                            schedules.append({
                                'cron': cron,
                                'hour': hour,
                                'minute': minute
                            })
            
            if 'workflow_dispatch' in triggers:
                manual_only = True
    
    return schedules, manual_only

def categorize_workflow(workflow_name, workflow_file):
    """Categorize workflow based on name and content."""
    name_lower = workflow_name.lower()
    file_lower = workflow_file.lower()
    
    # Define categories based on workflow patterns
    if any(x in name_lower or x in file_lower for x in ['learn', 'tldr', 'news', 'hacker', 'github-trending']):
        return 'Learning'
    elif any(x in name_lower or x in file_lower for x in ['agent', 'performance', 'copilot']):
        return 'Agent Management'
    elif any(x in name_lower or x in file_lower for x in ['data', 'sync', 'stats', 'timeline', 'pages']):
        return 'Data & Documentation'
    elif any(x in name_lower or x in file_lower for x in ['review', 'check', 'validate', 'test', 'quality']):
        return 'Quality Assurance'
    elif any(x in name_lower or x in file_lower for x in ['mission', 'idea', 'goal', 'plan', 'autonomous', 'orchestrat']):
        return 'Autonomous Operations'
    elif any(x in name_lower or x in file_lower for x in ['cleanup', 'prune', 'archive']):
        return 'Maintenance'
    else:
        return 'Other'

def main():
    workflows_dir = Path('/home/runner/work/Chained/Chained/.github/workflows')
    
    all_workflows = []
    scheduled_workflows = []
    manual_workflows = []
    categories = defaultdict(list)
    hourly_schedule = defaultdict(list)  # hour -> list of workflows
    
    # Process each workflow file
    for workflow_file in sorted(workflows_dir.glob('*.yml')):
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            if not workflow_data or 'name' not in workflow_data:
                continue
            
            workflow_name = workflow_data['name']
            workflow_filename = workflow_file.name
            
            schedules, has_manual = get_schedule_info(workflow_data, workflow_name)
            category = categorize_workflow(workflow_name, workflow_filename)
            
            workflow_info = {
                'name': workflow_name,
                'file': workflow_filename,
                'schedules': schedules,
                'has_manual': has_manual,
                'category': category
            }
            
            all_workflows.append(workflow_info)
            categories[category].append(workflow_info)
            
            if schedules:
                scheduled_workflows.append(workflow_info)
                # Add to hourly schedule
                for sched in schedules:
                    try:
                        hour_int = int(sched['hour']) if sched['hour'] != '*' else None
                        if hour_int is not None:
                            hourly_schedule[hour_int].append({
                                'name': workflow_name,
                                'minute': sched['minute'],
                                'cron': sched['cron']
                            })
                    except (ValueError, TypeError):
                        pass
            
            if has_manual and not schedules:
                manual_workflows.append(workflow_info)
                
        except Exception as e:
            print(f"Error processing {workflow_file.name}: {e}")
    
    # Generate output
    print("=" * 80)
    print("WORKFLOW ANALYSIS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    print(f"Total Workflows: {len(all_workflows)}")
    print(f"Scheduled Workflows: {len(scheduled_workflows)}")
    print(f"Manual-only Workflows: {len(manual_workflows)}")
    print()
    
    print("=" * 80)
    print("CATEGORIES")
    print("=" * 80)
    for category in sorted(categories.keys()):
        workflows = categories[category]
        print(f"\n{category} ({len(workflows)} workflows):")
        for wf in workflows:
            sched_info = ""
            if wf['schedules']:
                crons = [s['cron'] for s in wf['schedules']]
                sched_info = f" [Scheduled: {', '.join(crons)}]"
            elif wf['has_manual']:
                sched_info = " [Manual only]"
            print(f"  - {wf['name']}{sched_info}")
    
    print("\n" + "=" * 80)
    print("24-HOUR SCHEDULE VIEW")
    print("=" * 80)
    for hour in range(24):
        workflows = hourly_schedule.get(hour, [])
        if workflows:
            print(f"\n{hour:02d}:00 UTC ({len(workflows)} workflows):")
            for wf in sorted(workflows, key=lambda x: x['minute']):
                print(f"  - {wf['minute'].rjust(2, '0')}:{hour:02d} - {wf['name']}")
    
    print("\n" + "=" * 80)
    print("INTERVAL PATTERNS")
    print("=" * 80)
    
    # Detect common intervals
    every_hour = []
    every_2_hours = []
    every_3_hours = []
    every_6_hours = []
    every_12_hours = []
    daily = []
    weekly = []
    
    for wf in scheduled_workflows:
        for sched in wf['schedules']:
            cron = sched['cron']
            hour = sched['hour']
            minute = sched['minute']
            
            # Check patterns
            if '*/1' in hour or hour == '*':
                every_hour.append(wf['name'])
            elif '*/2' in hour:
                every_2_hours.append(wf['name'])
            elif '*/3' in hour:
                every_3_hours.append(wf['name'])
            elif '*/6' in hour:
                every_6_hours.append(wf['name'])
            elif '*/12' in hour:
                every_12_hours.append(wf['name'])
            elif ',' not in hour and '*' not in hour:
                # Specific hour, likely daily
                daily.append(wf['name'])
    
    if every_hour:
        print(f"\nEvery Hour ({len(every_hour)}):")
        for name in sorted(set(every_hour)):
            print(f"  - {name}")
    
    if every_2_hours:
        print(f"\nEvery 2 Hours ({len(every_2_hours)}):")
        for name in sorted(set(every_2_hours)):
            print(f"  - {name}")
    
    if every_3_hours:
        print(f"\nEvery 3 Hours ({len(every_3_hours)}):")
        for name in sorted(set(every_3_hours)):
            print(f"  - {name}")
    
    if every_6_hours:
        print(f"\nEvery 6 Hours ({len(every_6_hours)}):")
        for name in sorted(set(every_6_hours)):
            print(f"  - {name}")
    
    if every_12_hours:
        print(f"\nEvery 12 Hours ({len(every_12_hours)}):")
        for name in sorted(set(every_12_hours)):
            print(f"  - {name}")
    
    if daily:
        print(f"\nDaily at Specific Times ({len(set(daily))}):")
        for name in sorted(set(daily))[:10]:  # Show first 10
            print(f"  - {name}")
        if len(set(daily)) > 10:
            print(f"  ... and {len(set(daily)) - 10} more")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
