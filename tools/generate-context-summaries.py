#!/usr/bin/env python3
"""
Context Summary Generator for Chained Autonomous AI System

This tool extracts key insights from learnings data and generates
contextual summaries for different areas of the codebase.

Usage:
    python tools/generate-context-summaries.py [--update-all] [--area AREA]

Author: @investigate-champion (Ada - Visionary and analytical AI agent)
Date: 2025-11-17
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

class ContextGenerator:
    """Generate context summaries from learnings data"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.knowledge_graph_path = repo_root / 'learnings' / 'discussions' / 'knowledge_graph.json'
        self.discussions_dir = repo_root / 'learnings' / 'discussions'
        
    def load_knowledge_graph(self) -> Dict:
        """Load the knowledge graph"""
        with open(self.knowledge_graph_path, 'r') as f:
            return json.load(f)
    
    def categorize_insights(self, insights: Dict) -> Dict[str, List]:
        """Categorize insights by topic area - NO DUPLICATION
        
        Each insight is assigned to EXACTLY ONE category based on content.
        Categories are path-specific to match directory structure.
        """
        categories = {
            'workflows': [],
            'agents': [],
            'instructions': [],
            'tools': [],
            'learnings': [],
            'general': []
        }
        
        for insight_id, insight in insights.items():
            content = insight.get('content', '').lower()
            
            # PATH-SPECIFIC categorization - first match wins (no duplication)
            # Order matters: most specific first
            
            # Workflows: .github/workflows/**/*.yml
            if any(kw in content for kw in ['workflow', '.yml', 'github actions', 'ci/cd', 
                                            'branch protection', 'pr creation', 'workflow run']):
                categories['workflows'].append(insight)
                continue  # Only one category per insight
            
            # Agents: .github/agents/**, .github/agent-system/**
            elif any(kw in content for kw in ['agent', '@', 'copilot', 'custom agent',
                                              'agent assignment', 'coordination', 'specialization']):
                categories['agents'].append(insight)
                continue
            
            # Tools: tools/**/*.py
            elif any(kw in content for kw in ['tool', 'script', '.py', 'utility', 
                                              'python', 'automation', 'data processing']):
                categories['tools'].append(insight)
                continue
            
            # Instructions: .github/instructions/**/*.instructions.md
            elif any(kw in content for kw in ['instruction', 'copilot-instruction', 'guideline',
                                              'applyto', 'path-specific instruction']):
                categories['instructions'].append(insight)
                continue
            
            # Learnings: learnings/** (for meta-learning context)
            elif any(kw in content for kw in ['learning', 'tldr', 'hacker news', 'trend']):
                categories['learnings'].append(insight)
                continue
            
            # General: catch-all (not used in specific context files)
            else:
                categories['general'].append(insight)
        
        # Verify no duplication
        self._verify_no_duplication(categories)
        
        return categories
    
    def _verify_no_duplication(self, categories: Dict[str, List]):
        """Verify that no insight appears in multiple categories"""
        seen_ids = set()
        total_count = 0
        
        for category_name, insights in categories.items():
            for insight in insights:
                insight_id = id(insight)  # Use object id for uniqueness
                if insight_id in seen_ids:
                    raise ValueError(
                        f"DUPLICATE INSIGHT DETECTED! Insight appears in multiple categories. "
                        f"This violates the path-specific, non-duplicated requirement."
                    )
                seen_ids.add(insight_id)
                total_count += 1
        
        print(f"✓ Verified: {total_count} insights, no duplicates across categories")
        return True
    
    def extract_key_patterns(self, insights: List[Dict]) -> List[str]:
        """Extract key patterns from insights"""
        patterns = []
        
        # Look for high-confidence insights
        high_conf = [i for i in insights if i.get('confidence', 0) >= 0.7]
        
        # Extract unique content snippets
        seen = set()
        for insight in high_conf[:10]:  # Top 10 high-confidence
            content = insight.get('content', '').strip()
            if content and content not in seen and len(content) < 200:
                patterns.append(content)
                seen.add(content)
        
        return patterns
    
    def generate_workflow_context(self, insights: List[Dict]) -> str:
        """Generate context file for workflow development"""
        patterns = self.extract_key_patterns(insights)
        
        context = f"""# Context: Workflow Development

> **Path-Specific Context for:** `.github/workflows/**/*.yml`  
> Auto-generated from learnings and discussions  
> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> Generated by: @investigate-champion

## 🎯 Purpose

This file provides historical context and learned patterns **specific to GitHub Actions workflow development** in the Chained autonomous AI system.

**Scope:** This context applies ONLY to files in `.github/workflows/` directory.

## 🔑 Key Insights

"""
        # Add top patterns
        for i, pattern in enumerate(patterns[:5], 1):
            # Clean up the pattern
            clean_pattern = pattern.replace('\n', ' ').strip()
            if len(clean_pattern) > 150:
                clean_pattern = clean_pattern[:150] + "..."
            context += f"{i}. {clean_pattern}\n\n"
        
        context += """## 📋 Critical Requirements

Based on historical issues and discussions:

### Branch Protection
- **NEVER push directly to main branch**
- Always create a PR for any repository changes
- Use unique branch names with timestamps and run IDs
- Format: `workflow-name/YYYYMMDD-HHMMSS-${run_id}`

### Agent Attribution
- Always mention agents by name using @agent-name syntax
- Include agent references in issue bodies and PR descriptions
- Add workflow references to created issues/PRs
- Format: `*🤖 Created by workflow: [workflow-name](run-url)*`

### Issue Updates
- Comment on the issue when work is complete
- Include @agent-name attribution in issue updates
- Post issue update BEFORE removing WIP status from PR
- Reference the PR number in the issue comment

## 🚫 Common Pitfalls

- Using generic "agent" references without @mention
- Direct pushes to main branch
- Missing workflow attribution in created issues
- Not updating issues when work completes
- Forgetting to include run IDs in branch names

## ✅ Recommended Practices

1. **Always create PRs for changes** - Even automated changes
2. **Use @agent-name mentions** - Consistently reference agents
3. **Include context in PRs** - Reference related issues and discussions
4. **Test before merging** - Validate workflow changes
5. **Update documentation** - Keep context files current

## 📚 Related Resources

- `.github/instructions/branch-protection.instructions.md` - Branch protection rules
- `.github/instructions/agent-mentions.instructions.md` - Agent mention requirements
- `.github/instructions/workflow-reference.instructions.md` - Workflow attribution
- `learnings/discussions/knowledge_graph.json` - Full knowledge graph
- `docs/DATA_STORAGE_LIFECYCLE.md` - Data architecture

## 🔗 Reference Discussions

- Issue #1460 - Agent repetition patterns and diversity
- Issue #1461 - Multi-agent coordination patterns
- Issue #1486 - Documentation and README updates

---

*Part of the Chained autonomous AI ecosystem - Providing context for better agent decisions* 🤖
"""
        return context
    
    def generate_agent_context(self, insights: List[Dict]) -> str:
        """Generate context file for agent system"""
        patterns = self.extract_key_patterns(insights)
        
        context = f"""# Context: Agent System

> Auto-generated from learnings and discussions  
> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> Generated by: @investigate-champion

## 🎯 Purpose

This file provides historical context about agent behaviors, coordination patterns, and lessons learned from the autonomous agent system.

## 🔑 Key Insights from Past Work

"""
        for i, pattern in enumerate(patterns[:5], 1):
            clean_pattern = pattern.replace('\n', ' ').strip()
            if len(clean_pattern) > 150:
                clean_pattern = clean_pattern[:150] + "..."
            context += f"{i}. {clean_pattern}\n\n"
        
        context += """## 🤖 Agent Behavior Patterns

### Successful Patterns
- **Specialized Focus**: Agents perform best when working within their specialization
- **Clear Attribution**: @agent-name mentions improve tracking and accountability
- **Context Awareness**: Agents benefit from understanding related past work
- **Collaboration**: Multi-agent coordination requires explicit communication

### Observed Challenges
- **Repetition**: Agents may fall into habitual approaches without diversity
- **Context Loss**: Missing historical context leads to reinventing solutions
- **Attribution Gaps**: Generic references reduce performance tracking accuracy
- **Scope Creep**: Agents sometimes work outside their specialization

## 📋 Agent Assignment Best Practices

1. **Match to Specialization**: Use intelligent matching based on issue content
2. **Provide Clear Directives**: Include @agent-name and specialization reference
3. **Include Context**: Link to related issues and past discussions
4. **Set Expectations**: Define scope and success criteria
5. **Track Performance**: Use @mentions for accurate attribution

## 🚫 Anti-Patterns to Avoid

- Assigning work outside agent specialization
- Using generic "agent" references without @mention
- Missing context about similar past work
- Overloading a single agent with too many tasks
- Not tracking agent performance metrics

## ✅ Recommended Agent Workflow

```markdown
1. Issue created with clear description
2. Intelligent matching selects appropriate agent (@agent-name)
3. Issue body updated with agent directive and context
4. Agent reviews context files and related discussions
5. Agent implements solution following specialization
6. Agent creates PR with proper attribution
7. Agent comments on issue with completion status
8. Performance metrics updated based on work quality
```

## 📊 Performance Considerations

- **Code Quality**: Agents evaluated on code review scores
- **Resolution Rate**: Successfully closed issues improve scores
- **Review Feedback**: Positive reviews boost agent performance
- **Attribution**: Proper @mentions enable accurate tracking
- **Specialization**: Working within expertise increases success

## 📚 Related Resources

- `.github/agents/` - Agent definitions and specializations
- `.github/agent-system/registry.json` - Agent registry
- `.github/instructions/agent-mentions.instructions.md` - Mention requirements
- `AGENT_QUICKSTART.md` - Agent system overview
- `learnings/discussions/knowledge_graph.json` - Historical insights

## 🔗 Reference Discussions

- Issue #1460 - Agent repetition and diversity patterns
- Issue #1461 - Multi-agent coordination strategies
- Agent evaluation and performance tracking improvements

---

*Part of the Chained autonomous AI ecosystem - Learning from agent experiences* 🤖
"""
        return context
    
    def generate_tools_context(self, insights: List[Dict]) -> str:
        """Generate context file for tools development"""
        context = f"""# Context: Tools Development

> Auto-generated from learnings and discussions  
> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> Generated by: @investigate-champion

## 🎯 Purpose

This file provides context for developing and maintaining Python tools in the Chained autonomous AI system.

## 🔧 Tools Philosophy

The `tools/` directory contains Python utilities that support the autonomous system:
- **Code Analysis**: Pattern detection, archaeology, metrics
- **Content Processing**: Learning ingestion, parsing, filtering
- **System Management**: Agent validation, label creation, world state
- **Automation**: Context generation, data synchronization

## 📋 Development Best Practices

### Code Quality
- Use type hints for function signatures
- Follow PEP 8 style guide
- Include docstrings for all public functions
- Handle exceptions gracefully
- Use virtual environments

### Tool Design
- **Single Responsibility**: Each tool should do one thing well
- **Composability**: Tools should work together via standard inputs/outputs
- **Error Handling**: Fail gracefully with clear error messages
- **Logging**: Use logging module for debugging
- **Testing**: Include unit tests where appropriate

### Integration
- **Workflow Integration**: Tools often called from GitHub Actions
- **Data Formats**: Use JSON for structured data exchange
- **Exit Codes**: Return 0 for success, non-zero for errors
- **Output**: Write to stdout for data, stderr for errors

## 🔑 Common Tool Patterns

### Learning Processors
```python
# Pattern: Fetch → Parse → Filter → Store
def fetch_data(source): ...
def parse_content(raw_data): ...
def filter_quality(parsed_data): ...
def store_learning(filtered_data): ...
```

### Analysis Tools
```python
# Pattern: Load → Analyze → Generate Insights → Output
def load_data(path): ...
def analyze_patterns(data): ...
def generate_insights(analysis): ...
def output_results(insights): ...
```

### System Utilities
```python
# Pattern: Validate → Process → Update → Verify
def validate_input(data): ...
def process_operation(validated_data): ...
def update_state(processed_data): ...
def verify_changes(updated_state): ...
```

## 🚫 Common Pitfalls

- Not handling file paths correctly (use Path from pathlib)
- Hardcoding repository paths (use relative paths or env vars)
- Not validating JSON data structures
- Missing error handling for external API calls
- Not logging important operations

## ✅ Recommended Practices

1. **Use pathlib.Path** - Better path handling than string concatenation
2. **Type Hints** - Makes code self-documenting
3. **Error Context** - Provide useful error messages
4. **Idempotency** - Tools should be safe to run multiple times
5. **Documentation** - Include usage examples in docstrings

## 📚 Related Resources

- `tools/README.md` - Tools directory overview
- `requirements.txt` - Python dependencies
- `.github/workflows/` - Workflow integrations
- `docs/DATA_STORAGE_LIFECYCLE.md` - Data architecture

---

*Part of the Chained autonomous AI ecosystem - Building robust automation tools* 🤖
"""
        return context
    
    def generate_instructions_context(self) -> str:
        """Generate context file for instructions directory"""
        context = f"""# Context: Path-Specific Instructions

> Auto-generated from learnings and discussions  
> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> Generated by: @investigate-champion

## 🎯 Purpose

This file provides guidance for creating and maintaining path-specific custom instruction files.

## 📋 Instruction File System

Path-specific instructions use the `.instructions.md` format with YAML frontmatter:

```markdown
---
applyTo:
  - "path/pattern/**"
  - "another/pattern/*.yml"
---

# Instructions Title

Your instructions here...
```

## 🔑 Key Learnings

### Effective Instructions
- **Be Specific**: Clear, actionable rules work best
- **Include Examples**: Show correct and incorrect usage
- **Provide Context**: Explain WHY rules exist
- **Link Resources**: Reference related documentation
- **Use Markdown**: Headers, lists, code blocks for clarity

### Common Patterns
1. **Enforcement Rules**: MUST/NEVER statements for critical requirements
2. **Best Practices**: Recommended approaches with rationale
3. **Anti-Patterns**: Examples of what NOT to do
4. **Quick Reference**: Checklists and summary tables

## 📊 Current Instruction Files

- `agent-mentions.instructions.md` - Agent attribution requirements
- `workflow-agent-assignment.instructions.md` - Workflow-specific rules
- `issue-pr-agent-mentions.instructions.md` - Issue/PR templates
- `branch-protection.instructions.md` - PR-based workflow enforcement
- `agent-issue-updates.instructions.md` - Issue communication requirements
- `github-pages-testing.instructions.md` - Pages quality assurance
- `workflow-reference.instructions.md` - Workflow attribution

## 🚫 Pitfalls to Avoid

- **Too Generic**: Instructions should be path-specific
- **Too Lengthy**: Keep focused and concise
- **Conflicting Rules**: Ensure consistency across files
- **Outdated Content**: Keep instructions current
- **Missing ApplyTo**: Always specify scope patterns

## ✅ Best Practices

1. **Test Patterns**: Verify `applyTo:` glob patterns match intended files
2. **Clear Examples**: Show both correct and incorrect usage
3. **Reference Standards**: Link to official documentation
4. **Version Control**: Commit changes to track evolution
5. **Review Regularly**: Update as patterns emerge

## 📚 Related Resources

- `.github/instructions/README.md` - Instruction system overview
- `.github/copilot-instructions.md` - Repository-wide instructions
- [GitHub Docs](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) - Official guidance

---

*Part of the Chained autonomous AI ecosystem - Guiding agents with context-aware instructions* 🤖
"""
        return context
    
    def generate_context_index(self, categories: Dict[str, List]) -> Dict:
        """Generate the context index JSON"""
        index = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "generated_by": "@investigate-champion",
            "contexts": {
                "workflows": {
                    "path": ".github/workflows/.context.md",
                    "summary": "Workflow development patterns, branch protection, and agent attribution",
                    "key_insights": len(categories.get('workflows', [])),
                    "applies_to": [".github/workflows/**/*.yml"]
                },
                "agents": {
                    "path": ".github/agents/.context.md",
                    "summary": "Agent system behavior, coordination patterns, and performance insights",
                    "key_insights": len(categories.get('agents', [])),
                    "applies_to": [".github/agents/**", ".github/agent-system/**"]
                },
                "tools": {
                    "path": "tools/.context.md",
                    "summary": "Tool development best practices and common patterns",
                    "key_insights": len(categories.get('tools', [])),
                    "applies_to": ["tools/**/*.py"]
                },
                "instructions": {
                    "path": ".github/instructions/.context.md",
                    "summary": "Guidance for creating effective path-specific instructions",
                    "key_insights": 0,
                    "applies_to": [".github/instructions/**/*.instructions.md"]
                }
            },
            "quick_reference": {
                "agent_mentions": "Always use @agent-name syntax for agent references",
                "branch_protection": "Never push directly to main, always create PR",
                "workflow_references": "Include workflow name and run ID in created issues/PRs",
                "issue_updates": "Comment on issues when work completes with @agent attribution",
                "context_awareness": "Check for .context.md files before starting work"
            },
            "data_sources": {
                "knowledge_graph": "learnings/discussions/knowledge_graph.json",
                "discussions": "learnings/discussions/*.json",
                "analysis": "analysis/*.json"
            }
        }
        return index
    
    def generate_all(self):
        """Generate all context files"""
        print("🔍 Loading knowledge graph...")
        kg = self.load_knowledge_graph()
        
        print("📊 Categorizing insights...")
        categories = self.categorize_insights(kg['insights'])
        
        for cat, insights in categories.items():
            print(f"  - {cat}: {len(insights)} insights")
        
        print("\n📝 Generating context files...")
        
        # Generate workflow context
        workflow_path = self.repo_root / '.github' / 'workflows' / '.context.md'
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_context = self.generate_workflow_context(categories['workflows'])
        with open(workflow_path, 'w') as f:
            f.write(workflow_context)
        print(f"✅ Created {workflow_path}")
        
        # Generate agent context
        agent_path = self.repo_root / '.github' / 'agents' / '.context.md'
        agent_context = self.generate_agent_context(categories['agents'])
        with open(agent_path, 'w') as f:
            f.write(agent_context)
        print(f"✅ Created {agent_path}")
        
        # Generate tools context
        tools_path = self.repo_root / 'tools' / '.context.md'
        tools_context = self.generate_tools_context(categories['tools'])
        with open(tools_path, 'w') as f:
            f.write(tools_context)
        print(f"✅ Created {tools_path}")
        
        # Generate instructions context
        instr_path = self.repo_root / '.github' / 'instructions' / '.context.md'
        instr_context = self.generate_instructions_context()
        with open(instr_path, 'w') as f:
            f.write(instr_context)
        print(f"✅ Created {instr_path}")
        
        # Generate context index
        index_path = self.repo_root / '.github' / 'context-index.json'
        index = self.generate_context_index(categories)
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        print(f"✅ Created {index_path}")
        
        print("\n✨ Context generation complete!")
        print(f"\nGenerated {len(categories)} context areas:")
        for cat, insights in categories.items():
            if insights:
                print(f"  - {cat}: {len(insights)} insights")

def main():
    parser = argparse.ArgumentParser(description='Generate context summaries from learnings data')
    parser.add_argument('--update-all', action='store_true', help='Update all context files')
    parser.add_argument('--area', type=str, help='Update specific area (workflows, agents, tools)')
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    generator = ContextGenerator(repo_root)
    
    if args.update_all or not args.area:
        generator.generate_all()
    else:
        print(f"Updating {args.area} context...")
        # Could implement selective updates here
        generator.generate_all()

if __name__ == '__main__':
    main()
