#!/usr/bin/env python3
"""
Extract workflow data from .github/workflows/ for workflow-schedule.html
Author: @APIs-architect
"""

import os
import re
import yaml
from collections import defaultdict
from datetime import datetime

WORKFLOWS_DIR = '/home/runner/work/Chained/Chained/.github/workflows'

def parse_cron(cron_expr):
    """Parse cron expression to human readable schedule"""
    parts = cron_expr.split()
    if len(parts) != 5:
        return cron_expr
    
    minute, hour, day, month, weekday = parts
    
    # Handle hour
    if hour == '*':
        hour_str = 'every hour'
    elif '/' in hour:
        base, interval = hour.split('/')
        hour_str = f'every {interval} hours'
    else:
        hour_str = f'at {hour}:00'
    
    # Handle day/weekday
    if weekday != '*':
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        if ',' in weekday:
            day_list = [days[int(d)] for d in weekday.split(',')]
            day_str = ', '.join(day_list)
        else:
            day_str = days[int(weekday)]
        return f"{day_str} {hour_str}"
    
    if day != '*':
        return f"Day {day} {hour_str}"
    
    return hour_str

def extract_workflow_info(filepath):
    """Extract information from a workflow file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
        
        if not data:
            return None
        
        workflow_name = data.get('name', os.path.basename(filepath).replace('.yml', ''))
        
        info = {
            'name': workflow_name,
            'file': os.path.basename(filepath),
            'scheduled': False,
            'manual': False,
            'push': False,
            'pull_request': False,
            'workflow_dispatch': False,
            'cron_schedules': [],
            'description': ''
        }
        
        # Check triggers - handle both dict and list formats
        # YAML parses 'on:' as boolean True, so check for that
        on_config = data.get('on', data.get(True, {}))
        
        if isinstance(on_config, str):
            # Simple string trigger like "push" or "pull_request"
            if on_config == 'push':
                info['push'] = True
            elif on_config == 'pull_request':
                info['pull_request'] = True
        elif isinstance(on_config, list):
            # List of trigger strings
            for trigger in on_config:
                if trigger == 'push':
                    info['push'] = True
                elif trigger == 'pull_request':
                    info['pull_request'] = True
                elif trigger == 'workflow_dispatch':
                    info['manual'] = True
                    info['workflow_dispatch'] = True
        elif isinstance(on_config, dict):
            if 'schedule' in on_config:
                info['scheduled'] = True
                schedules = on_config['schedule']
                if isinstance(schedules, list):
                    for sched in schedules:
                        if isinstance(sched, dict) and 'cron' in sched:
                            info['cron_schedules'].append(sched['cron'])
            
            if 'workflow_dispatch' in on_config:
                info['manual'] = True
                info['workflow_dispatch'] = True
            
            if 'push' in on_config:
                info['push'] = True
            
            if 'pull_request' in on_config:
                info['pull_request'] = True
        
        # Extract description from comments
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().startswith('#') and 'description' in line.lower():
                desc_match = re.search(r'description[:\s]+(.+)', line, re.IGNORECASE)
                if desc_match:
                    info['description'] = desc_match.group(1).strip()
                    break
        
        return info
    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def categorize_workflow(workflow_info):
    """Categorize workflow based on name and content"""
    name = workflow_info['name'].lower()
    file = workflow_info['file'].lower()
    
    # Check for autonomous pipeline workflows
    if 'autonomous' in name or 'pipeline' in name:
        return 'autonomous'
    
    # Learning and data workflows
    if any(k in name for k in ['learn', 'tldr', 'hackernews', 'github-trending']):
        return 'learning'
    
    # Agent workflows
    if 'agent' in name or 'copilot' in name:
        return 'agents'
    
    # Data sync workflows
    if 'sync' in name or 'data' in name:
        return 'data'
    
    # Documentation workflows
    if any(k in name for k in ['docs', 'pages', 'github-pages']):
        return 'documentation'
    
    # Analysis workflows
    if any(k in name for k in ['analyze', 'archaeologist', 'metrics', 'review']):
        return 'analysis'
    
    # Testing workflows
    if 'test' in name:
        return 'testing'
    
    # Maintenance workflows
    if any(k in name for k in ['cleanup', 'maintenance', 'stale']):
        return 'maintenance'
    
    return 'other'

def get_24hr_schedule(workflows):
    """Generate 24-hour schedule view"""
    hourly_schedule = defaultdict(list)
    
    for wf in workflows:
        if wf['scheduled']:
            for cron in wf['cron_schedules']:
                parts = cron.split()
                if len(parts) >= 2:
                    minute = parts[0]
                    hour = parts[1]
                    
                    if hour != '*' and '/' not in hour:
                        try:
                            hour_int = int(hour)
                            hourly_schedule[hour_int].append(wf['name'])
                        except:
                            pass
    
    return dict(sorted(hourly_schedule.items()))

def main():
    # Get all workflow files
    workflow_files = [
        os.path.join(WORKFLOWS_DIR, f) 
        for f in os.listdir(WORKFLOWS_DIR) 
        if f.endswith('.yml')
    ]
    
    workflows = []
    for filepath in sorted(workflow_files):
        info = extract_workflow_info(filepath)
        if info:
            workflows.append(info)
    
    # Categorize workflows
    categories = defaultdict(list)
    for wf in workflows:
        cat = categorize_workflow(wf)
        categories[cat].append(wf)
    
    # Count statistics
    total_workflows = len(workflows)
    scheduled_workflows = sum(1 for wf in workflows if wf['scheduled'])
    manual_only = sum(1 for wf in workflows if wf['manual'] and not wf['scheduled'])
    
    # Generate 24-hour schedule
    schedule_24hr = get_24hr_schedule(workflows)
    
    # Print summary
    print(f"Total workflows: {total_workflows}")
    print(f"Scheduled workflows: {scheduled_workflows}")
    print(f"Manual-only workflows: {manual_only}")
    print(f"\nCategories:")
    for cat, wfs in sorted(categories.items()):
        print(f"  {cat}: {len(wfs)}")
    
    print(f"\n24-Hour Schedule:")
    for hour in range(24):
        if hour in schedule_24hr:
            print(f"  {hour:02d}:00 - {len(schedule_24hr[hour])} workflows")
    
    # Generate detailed data for HTML
    print("\n" + "="*80)
    print("DETAILED WORKFLOW DATA")
    print("="*80)
    
    for cat in sorted(categories.keys()):
        print(f"\n## {cat.upper()} ({len(categories[cat])} workflows)")
        for wf in sorted(categories[cat], key=lambda x: x['name']):
            print(f"\n### {wf['name']}")
            print(f"  File: {wf['file']}")
            if wf['scheduled']:
                print(f"  Scheduled: Yes")
                for cron in wf['cron_schedules']:
                    print(f"    - {cron} ({parse_cron(cron)})")
            if wf['manual']:
                print(f"  Manual trigger: Yes")
            if wf['push']:
                print(f"  Trigger on push: Yes")
            if wf['pull_request']:
                print(f"  Trigger on PR: Yes")

if __name__ == '__main__':
    main()
