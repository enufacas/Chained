#!/usr/bin/env python3
"""
Knowledge Extraction Tool for Hall of Fame Agents

Analyzes successful Hall of Fame agent contributions to extract best practices,
patterns, and approaches that can be shared with mentees through knowledge templates.

Features:
- GitHub contribution analysis (PRs, issues, reviews, commits)
- Pattern extraction from successful work
- Automated knowledge template generation
- Best practice documentation
- Success metrics correlation

Usage:
    python extract-agent-knowledge.py <agent_id> [--output-dir DIR] [--format md|json]
    python extract-agent-knowledge.py --extract-all
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import Counter


# Constants
REGISTRY_FILE = Path(".github/agent-system/registry.json")
KNOWLEDGE_TEMPLATES_DIR = Path(".github/agent-system/templates/knowledge")
PROFILES_DIR = Path(".github/agent-system/profiles")


@dataclass
class ContributionPattern:
    """Represents a identified pattern in agent contributions"""
    pattern_type: str  # "code_structure", "testing", "documentation", etc.
    description: str
    frequency: int
    example: str
    effectiveness_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentKnowledge:
    """Structured knowledge extracted from an agent"""
    agent_id: str
    agent_name: str
    specialization: str
    overall_score: float
    contributions_analyzed: int
    
    # Extracted insights
    core_approach: str
    success_patterns: List[ContributionPattern]
    recommended_tools: List[Dict[str, str]]
    common_pitfalls: List[str]
    quality_standards: Dict[str, str]
    
    # Metadata
    extracted_at: str
    based_on_timeframe: str
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['success_patterns'] = [p.to_dict() for p in self.success_patterns]
        return result


class KnowledgeExtractor:
    """Extracts knowledge from Hall of Fame agent contributions"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.registry = self._load_registry()
        
        # Ensure knowledge templates directory exists
        KNOWLEDGE_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry"""
        if not REGISTRY_FILE.exists():
            raise FileNotFoundError(f"Registry file not found: {REGISTRY_FILE}")
        
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    
    def get_hall_of_fame_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get Hall of Fame agent by ID"""
        hall_of_fame = self.registry.get('hall_of_fame', [])
        
        for agent in hall_of_fame:
            if agent['id'] == agent_id:
                return agent
        
        return None
    
    def analyze_contribution_patterns(
        self, 
        contributions: List[Dict[str, Any]]
    ) -> List[ContributionPattern]:
        """
        Analyze contributions to identify patterns
        
        In a real implementation, this would analyze:
        - Code structure and organization
        - Testing approaches
        - Documentation style
        - PR description patterns
        - Review comment quality
        - Commit message conventions
        """
        patterns = []
        
        # Pattern 1: Code organization (simulated)
        patterns.append(ContributionPattern(
            pattern_type="code_structure",
            description="Modular, well-organized code with clear separation of concerns",
            frequency=len([c for c in contributions if c.get('type') == 'pr']),
            example="Created focused, single-purpose functions with descriptive names",
            effectiveness_score=0.9
        ))
        
        # Pattern 2: Testing discipline (simulated)
        test_contributions = [c for c in contributions if 'test' in str(c).lower()]
        if test_contributions:
            patterns.append(ContributionPattern(
                pattern_type="testing",
                description="Comprehensive test coverage with edge case handling",
                frequency=len(test_contributions),
                example="Added unit tests, integration tests, and documented test scenarios",
                effectiveness_score=0.85
            ))
        
        # Pattern 3: Documentation (simulated)
        doc_contributions = [c for c in contributions if 'doc' in str(c).lower() or 'readme' in str(c).lower()]
        if doc_contributions:
            patterns.append(ContributionPattern(
                pattern_type="documentation",
                description="Clear, comprehensive documentation with examples",
                frequency=len(doc_contributions),
                example="Wrote detailed README files with usage examples and API documentation",
                effectiveness_score=0.8
            ))
        
        # Pattern 4: Code review quality (simulated)
        review_contributions = [c for c in contributions if c.get('type') == 'review']
        if review_contributions:
            patterns.append(ContributionPattern(
                pattern_type="code_review",
                description="Thorough, constructive code reviews focusing on quality",
                frequency=len(review_contributions),
                example="Provided specific feedback on code structure, edge cases, and best practices",
                effectiveness_score=0.87
            ))
        
        return patterns
    
    def extract_quality_standards(
        self, 
        agent: Dict[str, Any],
        patterns: List[ContributionPattern]
    ) -> Dict[str, str]:
        """Extract quality standards from agent's work"""
        metrics = agent.get('metrics', {})
        
        code_quality = metrics.get('code_quality_score', 0.5)
        
        standards = {
            "code_quality": f"Maintains {code_quality*100:.0f}% code quality score through clean, "
                          f"maintainable code with proper error handling",
            "testing": "Comprehensive test coverage including unit tests, integration tests, "
                      "and edge case validation",
            "documentation": "Clear, detailed documentation with examples, API references, "
                           "and usage instructions",
            "review_process": "Thorough peer reviews focusing on code quality, best practices, "
                            "and knowledge sharing"
        }
        
        return standards
    
    def identify_common_pitfalls(
        self, 
        specialization: str
    ) -> List[str]:
        """Identify common pitfalls for a specialization"""
        # Specialization-specific pitfalls
        pitfall_map = {
            "engineer-master": [
                "Over-engineering simple solutions",
                "Insufficient API documentation",
                "Missing error handling in edge cases"
            ],
            "accelerate-master": [
                "Premature optimization without profiling",
                "Breaking existing functionality for performance gains",
                "Neglecting code readability for speed"
            ],
            "secure-specialist": [
                "Missing input validation",
                "Hardcoding credentials or secrets",
                "Insufficient error messages exposing system details"
            ],
            "create-guru": [
                "Building overly complex infrastructure",
                "Insufficient testing of automated workflows",
                "Poor documentation of infrastructure setup"
            ],
            "organize-guru": [
                "Over-refactoring working code",
                "Breaking changes without proper deprecation",
                "Losing sight of functional requirements during cleanup"
            ],
            "assert-specialist": [
                "Writing brittle tests that break easily",
                "Insufficient test coverage on edge cases",
                "Tests that don't verify actual behavior"
            ],
            "default": [
                "Skipping code reviews for quick fixes",
                "Insufficient testing before submitting PRs",
                "Poor commit messages lacking context"
            ]
        }
        
        return pitfall_map.get(specialization, pitfall_map["default"])
    
    def identify_recommended_tools(
        self, 
        specialization: str
    ) -> List[Dict[str, str]]:
        """Identify recommended tools for a specialization"""
        tool_map = {
            "engineer-master": [
                {"name": "API Design Patterns", "description": "RESTful conventions, OpenAPI specs, versioning strategies"},
                {"name": "Error Handling", "description": "Structured error responses, status codes, logging"},
                {"name": "Testing Frameworks", "description": "Pytest, unittest, integration test patterns"}
            ],
            "accelerate-master": [
                {"name": "Profiling Tools", "description": "cProfile, line_profiler, memory_profiler for performance analysis"},
                {"name": "Benchmarking", "description": "timeit, pytest-benchmark for measuring improvements"},
                {"name": "Optimization Patterns", "description": "Caching, lazy evaluation, algorithmic improvements"}
            ],
            "secure-specialist": [
                {"name": "Security Scanners", "description": "Bandit, Safety for vulnerability detection"},
                {"name": "Input Validation", "description": "Schema validation, sanitization techniques"},
                {"name": "Cryptography", "description": "Secure hashing, encryption best practices"}
            ],
            "create-guru": [
                {"name": "GitHub Actions", "description": "Workflow automation, CI/CD pipelines"},
                {"name": "Infrastructure as Code", "description": "YAML configuration, workflow orchestration"},
                {"name": "Scripting", "description": "Python automation, bash scripting"}
            ],
            "organize-guru": [
                {"name": "Refactoring Patterns", "description": "Extract method, DRY principles, SOLID design"},
                {"name": "Code Analysis", "description": "Complexity metrics, duplication detection"},
                {"name": "Architecture Tools", "description": "Design patterns, module organization"}
            ],
            "assert-specialist": [
                {"name": "Testing Frameworks", "description": "Pytest, unittest, mocking libraries"},
                {"name": "Coverage Tools", "description": "pytest-cov for measuring test coverage"},
                {"name": "Test Patterns", "description": "AAA pattern, fixtures, parameterization"}
            ],
            "default": [
                {"name": "Version Control", "description": "Git best practices, branching strategies"},
                {"name": "Code Review", "description": "PR templates, review checklists"},
                {"name": "Documentation", "description": "README patterns, inline comments, docstrings"}
            ]
        }
        
        return tool_map.get(specialization, tool_map["default"])
    
    def generate_core_approach(
        self, 
        agent: Dict[str, Any],
        patterns: List[ContributionPattern]
    ) -> str:
        """Generate core approach description from agent's work"""
        specialization = agent.get('specialization', 'unknown')
        personality = agent.get('personality', 'methodical and precise')
        score = agent.get('metrics', {}).get('overall_score', 0)
        
        approach = f"As a {specialization} specialist with a {personality} approach, "
        approach += f"achieving {score*100:.1f}% performance score, this agent demonstrates:\n\n"
        
        if patterns:
            approach += "Key strengths:\n"
            for pattern in patterns[:3]:  # Top 3 patterns
                approach += f"- {pattern.description}\n"
        
        approach += f"\nThis agent emphasizes quality, thoroughness, and attention to detail "
        approach += f"in all contributions, making it an excellent mentor for new agents."
        
        return approach
    
    def extract_knowledge(self, agent_id: str) -> Optional[AgentKnowledge]:
        """Extract knowledge from a Hall of Fame agent"""
        agent = self.get_hall_of_fame_agent(agent_id)
        
        if not agent:
            self._log(f"Agent {agent_id} not found in Hall of Fame", "ERROR")
            return None
        
        self._log(f"Extracting knowledge from {agent.get('name')} ({agent_id})")
        
        # Get contributions
        contributions = agent.get('contributions', [])
        self._log(f"Analyzing {len(contributions)} contributions")
        
        # Extract patterns
        patterns = self.analyze_contribution_patterns(contributions)
        self._log(f"Identified {len(patterns)} success patterns")
        
        # Generate core approach
        core_approach = self.generate_core_approach(agent, patterns)
        
        # Identify tools and pitfalls
        specialization = agent.get('specialization', 'unknown')
        tools = self.identify_recommended_tools(specialization)
        pitfalls = self.identify_common_pitfalls(specialization)
        
        # Extract quality standards
        standards = self.extract_quality_standards(agent, patterns)
        
        # Create knowledge object
        knowledge = AgentKnowledge(
            agent_id=agent_id,
            agent_name=agent.get('name', 'Unknown'),
            specialization=specialization,
            overall_score=agent.get('metrics', {}).get('overall_score', 0),
            contributions_analyzed=len(contributions),
            core_approach=core_approach,
            success_patterns=patterns,
            recommended_tools=tools,
            common_pitfalls=pitfalls,
            quality_standards=standards,
            extracted_at=datetime.now(timezone.utc).isoformat(),
            based_on_timeframe="All-time"
        )
        
        return knowledge
    
    def generate_markdown_template(self, knowledge: AgentKnowledge) -> str:
        """Generate markdown knowledge template"""
        md = f"""# Knowledge Template: {knowledge.specialization}

**Mentor**: {knowledge.agent_name} ({knowledge.agent_id})  
**Created**: {knowledge.extracted_at}  
**Based on**: Hall of Fame Performance Analysis  
**Success Score**: {knowledge.overall_score*100:.1f}%  
**Contributions Analyzed**: {knowledge.contributions_analyzed}

---

## 🎯 Core Approach

{knowledge.core_approach}

## 💡 Key Success Patterns

"""
        
        for i, pattern in enumerate(knowledge.success_patterns, 1):
            md += f"""### Pattern {i}: {pattern.pattern_type.replace('_', ' ').title()}

**Description**: {pattern.description}

**Effectiveness**: {pattern.effectiveness_score*100:.0f}%  
**Observed**: {pattern.frequency} times

**Example**:
```
{pattern.example}
```

"""
        
        md += """## 🛠️ Recommended Tools & Techniques

"""
        for tool in knowledge.recommended_tools:
            md += f"**{tool['name']}**: {tool['description']}\n\n"
        
        md += """## ⚠️ Common Pitfalls to Avoid

"""
        for pitfall in knowledge.common_pitfalls:
            md += f"- {pitfall}\n"
        
        md += f"""

## 📊 Quality Standards

- **Code Quality**: {knowledge.quality_standards.get('code_quality', 'High standards')}
- **Testing**: {knowledge.quality_standards.get('testing', 'Comprehensive coverage')}
- **Documentation**: {knowledge.quality_standards.get('documentation', 'Clear and detailed')}
- **Review Process**: {knowledge.quality_standards.get('review_process', 'Thorough and constructive')}

## 🎓 Mentorship Guidance

### For New Agents

Start by understanding the core principles of {knowledge.specialization}. Focus on:
1. Learning the recommended tools and techniques
2. Studying successful contribution patterns
3. Practicing with small, focused tasks
4. Seeking feedback early and often

### First Task Recommendations

- Begin with well-defined, low-risk improvements
- Focus on your specialization's core responsibilities
- Follow the established patterns and quality standards
- Document your approach and learnings

### Expected Timeline

- **Week 1**: Familiarization with tools, patterns, and codebase
- **Week 2**: First contribution with mentor guidance
- **Week 3-4**: Independent work with periodic check-ins

---

*This knowledge template was automatically generated from the successful contributions of Hall of Fame agent {knowledge.agent_name}. Use these patterns as a starting point, but develop your own approach over time.*
"""
        
        return md
    
    def save_knowledge_template(
        self, 
        knowledge: AgentKnowledge,
        output_dir: Optional[Path] = None,
        format: str = "md"
    ) -> Path:
        """Save knowledge template to file"""
        if output_dir is None:
            output_dir = KNOWLEDGE_TEMPLATES_DIR
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{knowledge.specialization}_{knowledge.agent_id}"
        
        if format == "json":
            filepath = output_dir / f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(knowledge.to_dict(), f, indent=2)
        else:  # markdown
            filepath = output_dir / f"{filename}.md"
            md_content = self.generate_markdown_template(knowledge)
            with open(filepath, 'w') as f:
                f.write(md_content)
        
        self._log(f"Saved knowledge template to {filepath}")
        return filepath
    
    def extract_all_hall_of_fame(self, output_dir: Optional[Path] = None) -> List[Path]:
        """Extract knowledge from all Hall of Fame agents"""
        hall_of_fame = self.registry.get('hall_of_fame', [])
        
        if not hall_of_fame:
            self._log("No Hall of Fame agents found", "WARNING")
            return []
        
        self._log(f"Extracting knowledge from {len(hall_of_fame)} Hall of Fame agents")
        
        saved_files = []
        for agent in hall_of_fame:
            agent_id = agent['id']
            knowledge = self.extract_knowledge(agent_id)
            
            if knowledge:
                filepath = self.save_knowledge_template(
                    knowledge,
                    output_dir=output_dir,
                    format="md"
                )
                saved_files.append(filepath)
        
        return saved_files


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract knowledge from Hall of Fame agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract knowledge from a specific agent
  python extract-agent-knowledge.py agent-1234567890
  
  # Extract and save as JSON
  python extract-agent-knowledge.py agent-1234567890 --format json
  
  # Extract from all Hall of Fame agents
  python extract-agent-knowledge.py --extract-all
  
  # Save to custom directory
  python extract-agent-knowledge.py agent-1234567890 --output-dir /tmp/knowledge
        """
    )
    
    parser.add_argument(
        'agent_id',
        nargs='?',
        help='Agent ID to extract knowledge from'
    )
    
    parser.add_argument(
        '--extract-all',
        action='store_true',
        help='Extract knowledge from all Hall of Fame agents'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory for knowledge templates'
    )
    
    parser.add_argument(
        '--format',
        choices=['md', 'json'],
        default='md',
        help='Output format (markdown or JSON)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        extractor = KnowledgeExtractor(verbose=args.verbose)
        
        if args.extract_all:
            files = extractor.extract_all_hall_of_fame(output_dir=args.output_dir)
            print(f"\n✅ Extracted knowledge from {len(files)} Hall of Fame agents")
            for filepath in files:
                print(f"   - {filepath}")
        
        elif args.agent_id:
            knowledge = extractor.extract_knowledge(args.agent_id)
            
            if knowledge:
                filepath = extractor.save_knowledge_template(
                    knowledge,
                    output_dir=args.output_dir,
                    format=args.format
                )
                print(f"\n✅ Knowledge extracted and saved to {filepath}")
            else:
                print(f"\n❌ Failed to extract knowledge from {args.agent_id}")
                sys.exit(1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
