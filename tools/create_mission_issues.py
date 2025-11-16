#!/usr/bin/env python3
"""
Create GitHub issues for agent missions based on missions_data.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def ensure_label_exists(label_name, color='0E8A16', description=''):
    """
    Ensure a GitHub label exists in the repository.
    Creates the label if it doesn't exist.
    
    Args:
        label_name: Name of the label to create
        color: Hex color code without the # prefix
        description: Description for the label
    
    Returns:
        True if label exists or was created successfully, False otherwise
    """
    # Check if label exists
    check_cmd = ['gh', 'label', 'list', '--search', label_name]
    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, check=False)
        if label_name.lower() in result.stdout.lower():
            return True  # Label already exists
    except Exception as e:
        print(f"  ⚠️  Error checking label '{label_name}': {e}")
        return False
    
    # Create label if it doesn't exist
    create_cmd = ['gh', 'label', 'create', label_name, 
                  '--color', color, 
                  '--description', description or f'Auto-generated label: {label_name}']
    try:
        subprocess.run(create_cmd, capture_output=True, text=True, check=True)
        print(f"  ✓ Created label: {label_name}")
        return True
    except subprocess.CalledProcessError as e:
        # Label might already exist, which is OK
        if 'already exists' in e.stderr.lower():
            return True
        print(f"  ⚠️  Could not create label '{label_name}': {e.stderr}")
        return False
    except Exception as e:
        print(f"  ⚠️  Error creating label '{label_name}': {e}")
        return False


def main():
    # Load missions data
    with open('missions_data.json', 'r') as f:
        missions = json.load(f)
    
    print(f"📝 Creating {len(missions)} mission issues")
    
    # Collect all labels that will be needed
    all_labels = set(['learning', 'agent-mission', 'ai-generated', 'automated'])
    
    for mission in missions:
        patterns = mission.get('patterns', [])
        regions = mission.get('regions', [])
        
        # Add pattern labels
        for pattern in patterns:
            label_name = f"pattern-{pattern.lower()}"
            all_labels.add(label_name)
        
        # Add location labels
        for region in regions:
            label_name = f"location-{region.lower().replace(':', '-')}"
            all_labels.add(label_name)
    
    # Ensure all labels exist before creating issues
    print(f"\n🏷️  Ensuring {len(all_labels)} labels exist...")
    label_colors = {
        'learning': '0E8A16',
        'agent-mission': 'D93F0B',
        'ai-generated': '1D76DB',
        'automated': 'FBCA04',
    }
    
    for label in sorted(all_labels):
        # Determine color based on label type
        if label.startswith('pattern-'):
            color = '5319E7'  # Purple for patterns
            description = f'Technology/pattern: {label.replace("pattern-", "")}'
        elif label.startswith('location-'):
            color = 'F9D0C4'  # Pink for locations
            description = f'Location/region: {label.replace("location-", "")}'
        else:
            color = label_colors.get(label, '0E8A16')
            description = ''
        
        ensure_label_exists(label, color, description)
    
    print(f"\n📝 Creating issues for {len(missions)} missions\n")
    
    for i, mission in enumerate(missions, 1):
        idea_title = mission.get('idea_title', 'Unknown Mission')
        idea_summary = mission.get('idea_summary', '')
        patterns = mission.get('patterns', [])
        agents = mission.get('agents', [])
        regions = mission.get('regions', [])
        idea_id = mission.get('idea_id', 'unknown')
        
        # Build issue body
        agent_list = '\n'.join([
            f"- **{a.get('agent_name', 'Unknown')}** (@{a.get('specialization', 'unknown')}) - Score: {a.get('score', 0.0):.2f}"
            for a in agents
        ])
        
        location_list = ', '.join(regions) if regions else 'No specific location'
        pattern_list = ', '.join(patterns) if patterns else 'General'
        
        issue_body = f"""## 🎯 Agent Mission: {idea_title}

**Mission ID:** {idea_id}
**Created:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

### 📋 Mission Summary

{idea_summary}

### 🌍 Mission Locations

{location_list}

### 🏷️ Patterns & Technologies

{pattern_list}

### 👥 Assigned Agents (Max 10)

{agent_list}

**Note:** Only the top 10 most relevant agents were selected based on:
- Location relevance (30%)
- Role/skill match (40%)  
- Performance history (30%)

### 📊 Expected Outputs

- [ ] Documentation related to {', '.join(patterns)}
- [ ] Code examples or tools
- [ ] World model updates
- [ ] Learning artifacts

### 🔄 Next Steps

1. Agents investigate the mission locations
2. Gather insights and create artifacts
3. Report findings back to world model
4. Update agent metrics based on contributions

---

*This mission was automatically created by the Agent Missions workflow based on recent learning analysis.*
"""
        
        # Create labels list
        labels = ['learning', 'agent-mission', 'ai-generated', 'automated']
        
        # Add pattern labels
        for pattern in patterns:
            label_name = f"pattern-{pattern.lower()}"
            labels.append(label_name)
        
        # Add location labels
        for region in regions:
            label_name = f"location-{region.lower().replace(':', '-')}"
            labels.append(label_name)
        
        labels_str = ','.join(labels)
        
        # Create issue using gh CLI
        title = f"🎯 Mission: {idea_title}"
        
        try:
            result = subprocess.run(
                ['gh', 'issue', 'create', 
                 '--title', title,
                 '--body', issue_body,
                 '--label', labels_str],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  ✅ Created: {title}")
            print(f"     Issue URL: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Failed to create issue: {e.stderr}")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    
    print(f"\n✅ All mission issues created")
    return 0


if __name__ == '__main__':
    sys.exit(main())
