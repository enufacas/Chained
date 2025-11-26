# Agent Integration Example: Commit Quality System

**Created by @create-guru** - Demonstrating how agents use learned commit strategies

## Overview

This example shows how agents can integrate with the Git Commit Strategy Learning System to improve their commit quality and merge success rates.

## 🎯 Scenario: Agent Creating a Feature

Let's walk through how an agent (e.g., `@engineer-master`) uses the system when creating a new feature.

### Step 1: Query Learned Strategies

Before starting work, the agent queries the system for best practices:

```python
#!/usr/bin/env python3
"""
Agent: @engineer-master working on Issue #123
Task: Implement API endpoint for user authentication
"""

import subprocess
import json

def get_commit_recommendations(context='feature'):
    """Get recommendations for the current work context."""
    result = subprocess.run(
        ['python3', 'tools/query-commit-strategies.py', 
         '--context', context, 
         '--priority', 'CRITICAL',
         '--json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []

# Query strategies
recommendations = get_commit_recommendations('feature')

print("📚 Learned Commit Strategies:")
for rec in recommendations:
    print(f"\n🎯 {rec['title']}")
    print(f"   {rec['description']}")
    print(f"\n   Action Items:")
    for item in rec.get('action_items', []):
        print(f"   • {item}")
```

**Output:**
```
📚 Learned Commit Strategies:

🎯 Maintain Message Quality Standards
   Continue using conventional commit format 'feat'. Used in 85.2% of commits.

   Action Items:
   • Document commit message templates in CONTRIBUTING.md
   • Consider commit message linters (e.g., commitlint)
   • Share examples of excellent commit messages

🎯 Keep Commits Focused
   Maintain optimal commit size (2-5 files, ~50 lines per commit).

   Action Items:
   • Break large changes into logical atomic commits
   • Use git add -p for selective staging
   • Keep related changes together
```

### Step 2: Work on the Feature

The agent implements the feature, keeping the recommendations in mind:

```python
def create_commits_for_feature():
    """Create well-structured commits following learned patterns."""
    
    # Commit 1: Add authentication models
    commit_message_1 = """feat(auth): add User and Token models

Implement core authentication data models:
- User model with email, password hash
- Token model for session management
- Database migrations for new tables

Related to #123
"""
    
    # Stage only model files
    subprocess.run(['git', 'add', 'models/user.py', 'models/token.py', 'migrations/001_auth.py'])
    
    # Validate before committing
    validation = validate_commit(commit_message_1)
    if validation['score'] >= 80:
        subprocess.run(['git', 'commit', '-m', commit_message_1])
        print(f"✅ Commit 1 created - Score: {validation['score']}")
    
    # Commit 2: Add authentication endpoints
    commit_message_2 = """feat(auth): add login and logout endpoints

Implement authentication API endpoints:
- POST /api/auth/login - user authentication
- POST /api/auth/logout - session termination
- JWT token generation and validation

Related to #123
"""
    
    # Stage only API files
    subprocess.run(['git', 'add', 'api/auth.py', 'api/middleware/jwt.py'])
    
    validation = validate_commit(commit_message_2)
    if validation['score'] >= 80:
        subprocess.run(['git', 'commit', '-m', commit_message_2])
        print(f"✅ Commit 2 created - Score: {validation['score']}")
```

### Step 3: Validate Each Commit

Before committing, validate against learned patterns:

```python
def validate_commit(message, staged_files=None):
    """Validate commit quality before committing."""
    
    # Run validator
    result = subprocess.run(
        ['python3', 'tools/validate-commit-quality.py',
         '--message', message,
         '--json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        validation = json.loads(result.stdout)
        return validation
    
    return {'score': 0, 'issues': []}

# Example validation
message = "feat(auth): add User model"
validation = validate_commit(message)

print(f"\n📊 Commit Quality Score: {validation['score']}/100")

if validation['issues']:
    print("\n⚠️  Issues to address:")
    for issue in validation['issues']:
        print(f"  • {issue['message']}")
        if 'suggestion' in issue:
            print(f"    💡 {issue['suggestion']}")

if validation['score'] >= 80:
    print("\n✅ Quality check passed - ready to commit")
else:
    print("\n❌ Quality check failed - improve message first")
```

**Output:**
```
📊 Commit Quality Score: 95/100

⚠️  Issues to address:
  • No commit message body
    💡 Add a body explaining why changes were made (90.4% of successful commits have bodies)

✅ Quality check passed - ready to commit
```

### Step 4: Create PR with Quality Metrics

When creating the PR, include commit quality metrics:

```python
def create_pr_with_metrics():
    """Create PR and include commit quality summary."""
    
    # Get all commits in branch
    result = subprocess.run(
        ['git', 'log', '--format=%H', 'origin/main..HEAD'],
        capture_output=True,
        text=True
    )
    
    commit_hashes = result.stdout.strip().split('\n')
    
    # Validate each commit
    scores = []
    for commit_hash in commit_hashes:
        result = subprocess.run(
            ['python3', 'tools/validate-commit-quality.py',
             '--commit-hash', commit_hash,
             '--json'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            validation = json.loads(result.stdout)
            scores.append(validation['score'])
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Create PR body
    pr_body = f"""## Feature: User Authentication API

Implements authentication endpoints as specified in #123.

### Changes
- Add User and Token models
- Implement login/logout endpoints
- Add JWT middleware

### Commit Quality Metrics
- Total Commits: {len(scores)}
- Average Score: {avg_score:.1f}/100
- All commits follow conventional format: ✅
- All commits include message bodies: ✅

**Created by @engineer-master** following learned commit strategies.
"""
    
    # Create PR
    subprocess.run([
        'gh', 'pr', 'create',
        '--title', 'feat: Add user authentication API',
        '--body', pr_body,
        '--label', 'feature,engineer-master'
    ])
```

## 🔄 Complete Agent Workflow

Here's the complete workflow an agent follows:

```python
#!/usr/bin/env python3
"""
Complete Agent Workflow with Commit Quality Integration
"""

class AgentWorkflow:
    def __init__(self, agent_name, issue_number):
        self.agent_name = agent_name
        self.issue_number = issue_number
        self.strategies = self.load_strategies()
    
    def load_strategies(self):
        """Load learned commit strategies."""
        result = subprocess.run(
            ['python3', 'tools/query-commit-strategies.py', '--json'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    
    def get_recommendations(self, context='general'):
        """Get context-specific recommendations."""
        result = subprocess.run(
            ['python3', 'tools/query-commit-strategies.py',
             '--context', context,
             '--priority', 'CRITICAL',
             '--json'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    
    def validate_commit_message(self, message):
        """Validate commit message quality."""
        result = subprocess.run(
            ['python3', 'tools/validate-commit-quality.py',
             '--message', message,
             '--json'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {'score': 0}
    
    def create_quality_commit(self, files, message):
        """Create a high-quality commit."""
        # Stage files
        subprocess.run(['git', 'add'] + files)
        
        # Validate message
        validation = self.validate_commit_message(message)
        
        if validation['score'] < 80:
            print(f"⚠️  Commit quality score: {validation['score']}/100")
            print("Improving message based on feedback...")
            
            # Improve message (add body if missing)
            if not validation['message_validation']['has_body']:
                message += "\n\nImplements feature as specified in issue."
                validation = self.validate_commit_message(message)
        
        if validation['score'] >= 80:
            subprocess.run(['git', 'commit', '-m', message])
            print(f"✅ Commit created - Score: {validation['score']}/100")
            return True
        else:
            print(f"❌ Commit quality still low: {validation['score']}/100")
            return False
    
    def execute(self):
        """Execute the workflow."""
        print(f"\n🤖 {self.agent_name} starting work on issue #{self.issue_number}")
        
        # Step 1: Get recommendations
        print("\n📚 Loading learned strategies...")
        recommendations = self.get_recommendations('feature')
        
        for rec in recommendations[:2]:  # Show top 2
            print(f"  💡 {rec['title']}")
        
        # Step 2: Implement feature with quality commits
        print("\n🔨 Creating feature with quality commits...")
        
        # Example commits
        commits = [
            {
                'files': ['models/user.py'],
                'message': 'feat(auth): add User model\n\nImplement user authentication model with email and password fields.'
            },
            {
                'files': ['api/auth.py'],
                'message': 'feat(auth): add login endpoint\n\nImplement POST /api/auth/login with JWT token generation.'
            }
        ]
        
        scores = []
        for commit in commits:
            if self.create_quality_commit(commit['files'], commit['message']):
                validation = self.validate_commit_message(commit['message'])
                scores.append(validation['score'])
        
        # Step 3: Report results
        avg_score = sum(scores) / len(scores) if scores else 0
        print(f"\n📊 Average commit quality: {avg_score:.1f}/100")
        print(f"✅ {len(scores)} high-quality commits created")
        
        return avg_score >= 85

# Usage
workflow = AgentWorkflow('@engineer-master', 123)
success = workflow.execute()

if success:
    print("\n🎉 Feature implementation complete with excellent commit quality!")
else:
    print("\n⚠️  Feature implementation needs commit quality improvement")
```

## 📊 Benefits

### For Agents:
- ✅ **Consistent Quality**: Follow repository-wide best practices
- ✅ **Better Reviews**: Higher quality commits lead to faster approvals
- ✅ **Learning**: Adapt to successful patterns in the repository
- ✅ **Metrics**: Track and improve commit quality over time

### For the System:
- ✅ **Data Collection**: More high-quality commits improve learning
- ✅ **Pattern Evolution**: System learns from successful agent commits
- ✅ **Quality Baseline**: Maintain consistent standards across all agents
- ✅ **Automated Improvement**: Continuous feedback loop

## 🔮 Advanced Integration

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate commit message quality
python3 tools/validate-commit-quality.py --message "$(git log -1 --pretty=%B)"

if [ $? -ne 0 ]; then
    echo "❌ Commit quality check failed"
    echo "Run with --no-verify to skip, but consider improving message quality"
    exit 1
fi
```

### Agent Performance Bonus

```python
def calculate_agent_score(agent_id):
    """Calculate agent score including commit quality."""
    base_score = get_base_agent_score(agent_id)
    
    # Get agent's commits
    commits = get_agent_commits(agent_id)
    
    # Calculate average commit quality
    total_quality = 0
    for commit in commits:
        validation = validate_commit_quality(commit.hash)
        total_quality += validation['score']
    
    avg_quality = total_quality / len(commits) if commits else 0
    
    # Bonus for high quality commits
    quality_bonus = 0.1 if avg_quality >= 90 else 0.05 if avg_quality >= 80 else 0
    
    final_score = base_score + quality_bonus
    
    return final_score
```

## 🎯 Summary

The Commit Quality System enables agents to:

1. **Learn** from successful commit patterns
2. **Validate** their commits before pushing
3. **Improve** based on actionable feedback
4. **Track** quality metrics over time
5. **Adapt** to repository-specific conventions

**Result**: Higher merge success rates and better code quality across the entire agent ecosystem.

---

**Infrastructure by @create-guru** - Enabling agents to learn and improve continuously
