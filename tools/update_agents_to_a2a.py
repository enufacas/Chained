import os
import yaml
import re

AGENTS_DIR = '.github/agents'

# Skill mappings based on agent name keywords
SKILL_MAPPINGS = {
    'bug-hunter': ['detect-bugs', 'analyze-errors', 'debug-code'],
    'code-poet': ['write-code', 'improve-style', 'document-code'],
    'coordinate-wizard': ['coordinate-tasks', 'plan-workflow', 'decompose-tasks'],
    'create-guru': ['create-infrastructure', 'provision-resources'],
    'doc-master': ['write-documentation', 'update-guides', 'format-markdown'],
    'engineer-master': ['design-api', 'implement-backend', 'optimize-performance'],
    'engineer-wizard': ['design-system', 'architect-solution'],
    'feature-architect': ['design-feature', 'plan-implementation'],
    'integration-specialist': ['integrate-systems', 'connect-apis', 'manage-data-flow'],
    'meta-coordinator': ['orchestrate-system', 'manage-prs', 'assign-agents'],
    'performance-optimizer': ['analyze-performance', 'optimize-code', 'reduce-latency'],
    'refactor-wizard': ['refactor-code', 'improve-structure', 'reduce-complexity'],
    'security-guardian': ['audit-security', 'fix-vulnerabilities', 'verify-compliance'],
    'teach-wizard': ['explain-concepts', 'create-tutorials', 'mentor-users'],
    'test-champion': ['write-tests', 'verify-coverage', 'execute-test-plans'],
    'troubleshoot-expert': ['diagnose-issues', 'fix-pipeline', 'analyze-logs'],
    'ux-enhancer': ['design-ui', 'improve-ux', 'create-mockups'],
    'validate-pro': ['validate-inputs', 'verify-constraints'],
    'validate-wizard': ['check-compliance', 'validate-schema'],
    'infrastructure-specialist': ['manage-cloud', 'deploy-resources'],
    'a2a-coordinator': ['coordinate-a2a', 'manage-agents']
}

DEFAULT_SKILLS = ['analyze-code', 'provide-feedback']

def update_agent(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"Skipping {filepath}: Invalid frontmatter format")
        return

    frontmatter_raw = parts[1]
    body = parts[2]

    try:
        data = yaml.safe_load(frontmatter_raw)
    except yaml.YAMLError as e:
        print(f"Skipping {filepath}: YAML error {e}")
        return

    # Update fields
    changed = False
    
    if 'protocolVersion' not in data:
        data['protocolVersion'] = '0.3.0'
        changed = True
    
    if 'version' not in data:
        data['version'] = '1.0.0'
        changed = True
        
    if 'skills' not in data:
        name = data.get('name', '')
        skills = DEFAULT_SKILLS
        for key, mapped_skills in SKILL_MAPPINGS.items():
            if key in name:
                skills = mapped_skills
                break
        data['skills'] = skills
        changed = True
        
    if 'capabilities' not in data:
        data['capabilities'] = {
            'streaming': False,
            'pushNotifications': False
        }
        changed = True

    if changed:
        print(f"Updating {filepath}...")
        new_frontmatter = yaml.dump(data, sort_keys=False, default_flow_style=False).strip()
        new_content = f"---\n{new_frontmatter}\n---{body}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    for filename in os.listdir(AGENTS_DIR):
        if filename.endswith('.md') and filename != 'README.md':
            update_agent(os.path.join(AGENTS_DIR, filename))

if __name__ == '__main__':
    main()
