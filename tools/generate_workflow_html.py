#!/usr/bin/env python3
"""
Generate updated workflow-schedule.html based on current workflow analysis.

@APIs-architect - Systematic HTML generation from workflow data
"""

import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def parse_cron(cron_expr):
    """Parse cron expression to extract hour and minute."""
    parts = cron_expr.strip().split()
    if len(parts) >= 2:
        minute = parts[0]
        hour = parts[1]
        return hour, minute
    return None, None

def categorize_workflow(workflow_name, workflow_file):
    """Categorize workflow based on name and content."""
    name_lower = workflow_name.lower()
    file_lower = workflow_file.lower()
    
    if any(x in name_lower or x in file_lower for x in ['learn', 'tldr', 'news', 'hacker', 'github-trending']):
        return 'Learning & Knowledge'
    elif any(x in name_lower or x in file_lower for x in ['agent', 'performance', 'copilot', 'spawning', 'evolution']):
        return 'Agent Management'
    elif any(x in name_lower or x in file_lower for x in ['data', 'sync', 'stats', 'timeline', 'pages', 'tv', 'episode']):
        return 'Data & Documentation'
    elif any(x in name_lower or x in file_lower for x in ['review', 'check', 'validate', 'test', 'quality', 'ab-test']):
        return 'Quality Assurance'
    elif any(x in name_lower or x in file_lower for x in ['mission', 'idea', 'goal', 'plan', 'autonomous', 'orchestrat', 'pipeline']):
        return 'Autonomous Operations'
    elif any(x in name_lower or x in file_lower for x in ['cleanup', 'prune', 'archive', 'maintenance']):
        return 'Maintenance'
    elif any(x in name_lower or x in file_lower for x in ['friend', 'conversation', 'creative', 'challenge']):
        return 'AI Interactions'
    elif any(x in name_lower or x in file_lower for x in ['merge', 'conflict', 'label', 'issue']):
        return 'Automation'
    else:
        return 'Other'

def analyze_workflows():
    """Analyze all workflows."""
    workflows_dir = Path('.github/workflows')
    
    all_workflows = []
    scheduled_workflows = []
    manual_workflows = []
    categories = defaultdict(list)
    hourly_schedule = defaultdict(list)
    
    for workflow_file in sorted(workflows_dir.glob('*.yml')):
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            if not workflow_data or 'name' not in workflow_data:
                continue
            
            workflow_name = workflow_data['name']
            workflow_filename = workflow_file.name
            
            # Get triggers
            triggers = workflow_data.get('on') or workflow_data.get(True)
            schedules = []
            has_manual = False
            
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
                    has_manual = True
            
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
                for sched in schedules:
                    try:
                        hour_val = sched['hour']
                        # Handle different hour formats
                        if hour_val == '*':
                            # Every hour
                            for h in range(24):
                                hourly_schedule[h].append({
                                    'name': workflow_name,
                                    'minute': sched['minute'],
                                    'interval': True
                                })
                        elif '/' in hour_val:
                            # Interval (e.g., */3)
                            interval = int(hour_val.split('/')[1])
                            for h in range(0, 24, interval):
                                hourly_schedule[h].append({
                                    'name': workflow_name,
                                    'minute': sched['minute'],
                                    'interval': True
                                })
                        elif ',' in hour_val:
                            # Multiple specific hours
                            for h in hour_val.split(','):
                                hourly_schedule[int(h)].append({
                                    'name': workflow_name,
                                    'minute': sched['minute'],
                                    'interval': False
                                })
                        else:
                            # Single specific hour
                            hourly_schedule[int(hour_val)].append({
                                'name': workflow_name,
                                'minute': sched['minute'],
                                'interval': False
                            })
                    except (ValueError, TypeError):
                        pass
            
            if has_manual and not schedules:
                manual_workflows.append(workflow_info)
                
        except Exception as e:
            print(f"Error processing {workflow_file.name}: {e}")
    
    return {
        'all_workflows': all_workflows,
        'scheduled_workflows': scheduled_workflows,
        'manual_workflows': manual_workflows,
        'categories': dict(categories),
        'hourly_schedule': dict(hourly_schedule)
    }

def generate_24hour_schedule(hourly_schedule):
    """Generate 24-hour schedule HTML."""
    html = []
    
    for hour in range(24):
        workflows = hourly_schedule.get(hour, [])
        
        hour_label = f"{hour:02d}:00"
        html.append(f'        <div class="hour-label">{hour_label}</div>')
        html.append('        <div class="hour-content">')
        
        if workflows:
            for wf in sorted(workflows, key=lambda x: (x.get('minute', '0'), x['name'])):
                badge_class = 'workflow-badge interval' if wf.get('interval') else 'workflow-badge'
                html.append(f'            <span class="{badge_class}">{wf["name"]}</span>')
        else:
            html.append('            <span class="empty-hour">No scheduled workflows</span>')
        
        html.append('        </div>')
    
    return '\n'.join(html)

def generate_category_sections(categories):
    """Generate category sections HTML."""
    html = []
    
    # Sort categories by workflow count (descending)
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, workflows in sorted_cats:
        html.append(f'        <section class="category-section">')
        html.append(f'            <div class="category-header">')
        html.append(f'                <h2>{category}</h2>')
        html.append(f'                <span class="category-count">{len(workflows)} workflows</span>')
        html.append(f'            </div>')
        
        for wf in sorted(workflows, key=lambda x: x['name']):
            html.append('            <div class="workflow-card">')
            html.append(f'                <div class="workflow-name">{wf["name"]}</div>')
            html.append(f'                <div class="workflow-file">{wf["file"]}</div>')
            
            if wf['schedules'] or wf['has_manual']:
                html.append('                <div class="schedule-info">')
                
                for sched in wf['schedules']:
                    html.append(f'                    <span class="schedule-tag">🕐 {sched["cron"]}</span>')
                
                if wf['has_manual']:
                    html.append('                    <span class="trigger-tag">🎯 Manual trigger</span>')
                
                html.append('                </div>')
            
            html.append('            </div>')
        
        html.append('        </section>')
    
    return '\n'.join(html)

def main():
    """Generate the complete HTML file."""
    print("Analyzing workflows...")
    data = analyze_workflows()
    
    total = len(data['all_workflows'])
    scheduled = len(data['scheduled_workflows'])
    manual = len(data['manual_workflows'])
    num_categories = len(data['categories'])
    
    print(f"Total: {total}, Scheduled: {scheduled}, Manual: {manual}, Categories: {num_categories}")
    
    # Read the template (first part of existing HTML)
    with open('docs/workflow-schedule.html', 'r') as f:
        lines = f.readlines()
    
    # Find where to start replacing content
    # We'll keep everything up to the stats section and regenerate from there
    
    html_parts = []
    
    # Keep header and styles (lines 1-268)
    html_parts.append(''.join(lines[:268]))
    
    # Generate stats
    stats_html = f"""
        <!-- Statistics -->
        <section id="stats">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{scheduled}</div>
                    <div class="stat-label">Scheduled Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{manual}</div>
                    <div class="stat-label">Manual Only</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{num_categories}</div>
                    <div class="stat-label">Categories</div>
                </div>
            </div>
        </section>
"""
    html_parts.append(stats_html)
    
    # Keep legend section
    html_parts.append(''.join(lines[291:309]))
    
    # Generate 24-hour schedule
    schedule_html = f"""
        <!-- 24-Hour Schedule -->
        <section id="schedule">
            <h2 style="text-align: center; margin: 3rem 0 2rem;">📅 24-Hour Schedule View (UTC)</h2>
            <div class="schedule-grid">
{generate_24hour_schedule(data['hourly_schedule'])}
            </div>
        </section>
"""
    html_parts.append(schedule_html)
    
    # Generate category sections
    categories_html = f"""
        <!-- Workflow Categories -->
        <section id="categories">
            <h2 style="text-align: center; margin: 3rem 0 2rem;">📂 Workflows by Category</h2>
{generate_category_sections(data['categories'])}
        </section>
"""
    html_parts.append(categories_html)
    
    # Add footer
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    footer_html = f"""
    </main>

    <footer style="text-align: center; padding: 2rem; color: var(--text-muted); margin-top: 4rem;">
        <p>Last updated: {timestamp}</p>
        <p>Generated by <strong>@APIs-architect</strong> workflow analysis system</p>
        <p><a href="https://github.com/enufacas/Chained" style="color: var(--primary-color);">View on GitHub</a></p>
    </footer>

    <script>
        // Hamburger menu toggle
        const hamburger = document.querySelector('.hamburger');
        const mainNav = document.querySelector('.main-nav');

        hamburger.addEventListener('click', () => {{
            hamburger.classList.toggle('active');
            mainNav.classList.toggle('active');
        }});
    </script>
</body>
</html>
"""
    html_parts.append(footer_html)
    
    # Write the new file
    output_file = 'docs/workflow-schedule.html'
    with open(output_file, 'w') as f:
        f.write(''.join(html_parts))
    
    print(f"✓ Generated {output_file}")
    print(f"  Total workflows: {total}")
    print(f"  Scheduled: {scheduled}")
    print(f"  Manual: {manual}")
    print(f"  Categories: {num_categories}")

if __name__ == '__main__':
    main()
