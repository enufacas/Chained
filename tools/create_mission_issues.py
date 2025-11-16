#!/usr/bin/env python3
"""
Create GitHub issues for agent missions based on missions_data.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def calculate_ecosystem_relevance(patterns, summary):
    """
    Calculate ecosystem relevance score (1-10) based on patterns and summary.
    
    Scores missions based on how relevant they are to Chained's core ecosystem:
    - High (7-10): Directly applicable to core systems
    - Medium (4-6): Potentially applicable with some adaptation
    - Low (1-3): Primarily external learning
    
    Args:
        patterns: List of technology patterns
        summary: Mission summary text
    
    Returns:
        tuple: (score, relevance_level, applicable_components)
    """
    score = 3  # Base score for all learning missions
    applicable_components = []
    
    # Core ecosystem patterns (high relevance)
    high_relevance_patterns = {
        'agents': 3,
        'autonomous': 3,
        'ci_automation': 2,
        'devops': 2,
        'github': 2,
        'workflow': 2,
        'testing': 2,
        'code_generation': 3,
        'self_healing': 2,
        'evaluation': 2,
        'performance': 2,
        'monitoring': 2,
    }
    
    # Medium relevance patterns
    medium_relevance_patterns = {
        'ai': 1,
        'ai_ml': 1,
        'ml': 1,
        'api': 1,
        'web': 1,
        'cloud': 1,
        'security': 1,
        'data': 1,
        'analytics': 1,
    }
    
    # Calculate score based on patterns
    for pattern in patterns:
        pattern_lower = pattern.lower()
        if pattern_lower in high_relevance_patterns:
            score += high_relevance_patterns[pattern_lower]
        elif pattern_lower in medium_relevance_patterns:
            score += medium_relevance_patterns[pattern_lower]
    
    # Check summary for ecosystem keywords
    summary_lower = summary.lower()
    ecosystem_keywords = {
        'agent': ('Agent System', 1),
        'autonomous': ('Autonomous Pipeline', 1),
        'workflow': ('Autonomous Pipeline', 1),
        'ci/cd': ('Autonomous Pipeline', 1),
        'github actions': ('Autonomous Pipeline', 1),
        'testing': ('Autonomous Pipeline', 1),
        'world model': ('World Model', 2),
        'geographic': ('World Model', 1),
        'learning': ('Learning System', 1),
        'documentation': ('Documentation', 1),
    }
    
    for keyword, (component, points) in ecosystem_keywords.items():
        if keyword in summary_lower:
            score += points
            if component not in applicable_components:
                applicable_components.append(component)
    
    # Cap score at 10
    score = min(score, 10)
    
    # Determine relevance level
    if score >= 7:
        relevance_level = 'High'
        relevance_emoji = '🔴'
    elif score >= 4:
        relevance_level = 'Medium'
        relevance_emoji = '🟡'
    else:
        relevance_level = 'Low'
        relevance_emoji = '🟢'
    
    return score, f"{relevance_emoji} {relevance_level}", applicable_components


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
    
    created_issues = []  # Track created issues for assignment
    
    for i, mission in enumerate(missions, 1):
        idea_title = mission.get('idea_title', 'Unknown Mission')
        idea_summary = mission.get('idea_summary', '')
        patterns = mission.get('patterns', [])
        agent = mission.get('agent', {})  # Single agent, not list
        regions = mission.get('regions', [])
        idea_id = mission.get('idea_id', 'unknown')
        
        # Build agent info (single agent)
        agent_name = agent.get('agent_name', 'Unknown')
        agent_specialization = agent.get('specialization', '')
        agent_score = agent.get('score', 0.0)
        
        # Validate agent specialization - NEVER use 'unknown'
        if not agent_specialization or agent_specialization == 'unknown':
            print(f"  ⚠️  Warning: Mission '{idea_title}' has invalid agent specialization: '{agent_specialization}'")
            print(f"  ⚠️  Skipping mission creation - agent validation failed")
            continue  # Skip this mission
        
        location_list = ', '.join(regions) if regions else 'No specific location'
        pattern_list = ', '.join(patterns) if patterns else 'General'
        
        # Calculate ecosystem relevance
        relevance_score, relevance_level, applicable_components = calculate_ecosystem_relevance(patterns, idea_summary)
        
        # Determine mission type and focus based on relevance
        if relevance_score >= 7:
            mission_type = '⚙️ Ecosystem Enhancement'
            mission_focus = 'high relevance to core capabilities'
        elif relevance_score >= 4:
            mission_type = '🧠 Learning Mission'
            mission_focus = 'medium relevance with potential applications'
        else:
            mission_type = '🧠 Learning Mission'
            mission_focus = 'external learning and exploration'
        
        # Build ecosystem connection section
        if relevance_score >= 4:
            components_text = ', '.join(applicable_components) if applicable_components else 'To be determined'
            ecosystem_section = f"""
### 🔗 Ecosystem Connection ({relevance_level}: {relevance_score}/10)

This mission has {mission_focus}:

**Potentially applicable to:**
- {components_text if applicable_components else 'Evaluate during research'}

**Integration priority:** {'High - Consider implementation' if relevance_score >= 7 else 'Medium - Monitor for insights'}

{f'**Recommended approach:** If you identify strong ecosystem applications (7+/10), document specific integration proposals for potential follow-up work.' if relevance_score < 7 else '**Focus:** This mission has high relevance to Chained. Research thoroughly and propose concrete integration approaches.'}
"""
        else:
            ecosystem_section = f"""
### 🔗 Ecosystem Connection ({relevance_level}: {relevance_score}/10)

This mission is primarily for external learning and trend awareness.

**Focus:** Understand tech trends and document insights for future reference. If you discover unexpected applications to Chained's core capabilities, note them in your findings.
"""
        
        # Build deliverables based on relevance
        if relevance_score >= 7:
            deliverables_section = f"""### 📊 Expected Outputs

**Learning Deliverables (Required):**
- [ ] **Research Report** (2-3 pages)
  - Summary of key findings related to {', '.join(patterns)}
  - Best practices and lessons learned (3-5 points)
  - Industry trends and patterns
  
- [ ] **Ecosystem Integration Proposal** (Required for high relevance)
  - Specific changes to Chained's components
  - Expected improvements and benefits
  - Implementation complexity estimate (low/medium/high)
  - Risk assessment and mitigation strategies

**Additional Deliverables:**
- [ ] Code examples or proof-of-concept (if applicable)
- [ ] World model updates with geographic/tech data
- [ ] Integration design document or architecture proposal"""
        elif relevance_score >= 4:
            deliverables_section = f"""### 📊 Expected Outputs

**Learning Deliverables (Required):**
- [ ] **Research Report** (1-2 pages)
  - Summary of findings related to {', '.join(patterns)}
  - Key takeaways (3-5 bullet points)
  
- [ ] **Ecosystem Applicability Assessment**
  - Rate relevance to Chained: __ / 10
  - Specific components that could benefit
  - Integration complexity estimate (low/medium/high)

**Ecosystem Integration (If relevance ≥ 7):**
- [ ] Integration proposal document
  - Specific changes to Chained's workflows/systems
  - Expected benefits and improvements
  - Implementation effort estimate

**Additional:**
- [ ] Code examples or tools (if applicable)
- [ ] World model updates"""
        else:
            deliverables_section = f"""### 📊 Expected Outputs

**Learning Deliverables (Required):**
- [ ] **Research Report** (1-2 pages)
  - Summary of findings related to {', '.join(patterns)}
  - Key insights (3-5 points)
  - Industry trends observed
  
- [ ] **Brief Ecosystem Assessment**
  - Any unexpected applications to Chained (if found)
  - Relevance rating: __ / 10

**Additional:**
- [ ] Documentation updates
- [ ] World model updates with findings"""
        
        # Build next steps based on relevance
        if relevance_score >= 7:
            next_steps = f"""### 🔄 Next Steps

1. **@{agent_specialization}** researches {', '.join(patterns)} thoroughly
2. Analyzes applicability to Chained's core systems
3. **Develops integration proposal** with specific recommendations
4. Documents implementation approach and complexity
5. Creates artifacts (code samples, design docs, etc.)
6. Submits comprehensive findings with clear action items

**Success Criteria:**
- [ ] Clear understanding of technology/patterns
- [ ] Detailed integration proposal for Chained
- [ ] Implementation roadmap with effort estimates
- [ ] Risk assessment completed"""
        elif relevance_score >= 4:
            next_steps = f"""### 🔄 Next Steps

1. **@{agent_specialization}** researches {', '.join(patterns)}
2. Documents findings and key insights
3. **Evaluates ecosystem relevance** (critical step!)
4. If high relevance (≥7): Proposes specific integration approach
5. Updates world model with learnings
6. Agent metrics updated based on contributions

**Success Criteria:**
- [ ] Research report completed
- [ ] Ecosystem relevance honestly evaluated
- [ ] If relevant: Integration ideas proposed"""
        else:
            next_steps = f"""### 🔄 Next Steps

1. **@{agent_specialization}** investigates {', '.join(patterns)}
2. Gathers insights and documents findings
3. Notes any unexpected applications (if discovered)
4. Updates world model with learnings
5. Agent metrics updated based on contributions"""
        
        issue_body = f"""## {mission_type}: {idea_title}

**Mission ID:** {idea_id}
**Type:** {mission_type}
**Ecosystem Relevance:** {relevance_level} ({relevance_score}/10)
**Created:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

### 📋 Mission Summary

{idea_summary}
{ecosystem_section}

### 🌍 Mission Locations

{location_list}

### 🏷️ Patterns & Technologies

{pattern_list}

### 🤖 Assigned Agent

**{agent_name}** (@{agent_specialization}) - Match Score: {agent_score:.2f}

This mission was matched to **@{agent_specialization}** based on:
- Location relevance (30%)
- Role/skill match (40%)  
- Performance history (30%)

{deliverables_section}

{next_steps}

---

*This mission was automatically created by the Agent Missions workflow. Ecosystem relevance: **{relevance_level} ({relevance_score}/10)** - {'Focus on integration opportunities' if relevance_score >= 7 else 'Focus on learning and evaluation' if relevance_score >= 4 else 'Focus on external learning'}.*
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
            issue_url = result.stdout.strip()
            # Extract issue number from URL (format: https://github.com/owner/repo/issues/123)
            issue_number = issue_url.split('/')[-1] if issue_url else None
            
            print(f"  ✅ Created: {title}")
            print(f"     Issue URL: {issue_url}")
            
            # Track created issue with agent specialization for assignment
            created_issues.append({
                'issue_number': issue_number,
                'agent_specialization': agent_specialization,
                'title': title
            })
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Failed to create issue: {e.stderr}")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    
    print(f"\n✅ All mission issues created")
    
    # Save created issues info for assignment step
    with open('created_missions.json', 'w') as f:
        json.dump(created_issues, f, indent=2)
    
    print(f"📝 Saved {len(created_issues)} issue numbers for assignment")
    return 0


if __name__ == '__main__':
    sys.exit(main())
