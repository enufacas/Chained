#!/usr/bin/env python3
"""
Creative Coding Challenge Generator

An AI-powered system that generates creative coding challenges based on learnings
from TLDR Tech, Hacker News, and the autonomous AI ecosystem.

Created by @create-guru - inventive and visionary infrastructure creation inspired by Nikola Tesla.
Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import re
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from collections import Counter


@dataclass
class ChallengeTemplate:
    """Represents a coding challenge template"""
    template_id: str
    title: str
    category: str  # "algorithms", "data_structures", "api", "ml", "creative", "system_design"
    difficulty: str  # "easy", "medium", "hard", "expert"
    description: str
    requirements: List[str]
    test_cases: List[Dict[str, Any]]
    solution_hints: List[str]
    keywords: List[str]
    learning_sources: List[str]  # URLs or references that inspired this
    estimated_time_minutes: int
    created_at: str = ""
    usage_count: int = 0
    completion_rate: float = 0.0
    avg_rating: float = 0.0
    
    def matches_keywords(self, text: str) -> float:
        """Calculate keyword match score (0-1)"""
        text_lower = text.lower()
        matches = sum(1 for kw in self.keywords if kw.lower() in text_lower)
        return matches / len(self.keywords) if self.keywords else 0.0


@dataclass
class GeneratedChallenge:
    """Represents a generated challenge instance"""
    challenge_id: str
    template_id: str
    title: str
    category: str
    difficulty: str
    full_description: str
    requirements: List[str]
    test_cases: List[Dict[str, Any]]
    hints: List[str]
    timestamp: str
    learning_context: str = ""
    inspiration_sources: List[str] = field(default_factory=list)


class CreativeCodingChallengeGenerator:
    """
    Tesla-inspired creative coding challenge generator.
    
    Architecture inspired by transformer models but lightweight:
    1. Input Layer: Learning insights processing
    2. Template Selection: Keyword matching and relevance scoring
    3. Challenge Synthesis: Template customization with context
    4. Output Layer: Challenge formatting and validation
    
    Features:
    - Learning-integrated challenge generation
    - Difficulty progression system
    - Category diversity
    - Performance tracking
    - Auto-validation with test cases
    """
    
    def __init__(self, data_dir: str = "tools/data/coding_challenges"):
        """Initialize the challenge generator"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates_file = self.data_dir / "templates.json"
        self.generated_file = self.data_dir / "generated.json"
        self.stats_file = self.data_dir / "stats.json"
        
        self.templates: List[ChallengeTemplate] = []
        self.generated_history: List[GeneratedChallenge] = []
        self.stats: Dict[str, Any] = {}
        
        self._load_data()
        self._initialize_templates()
    
    def _load_data(self):
        """Load existing templates and history"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
                self.templates = [ChallengeTemplate(**t) for t in data]
        
        if self.generated_file.exists():
            with open(self.generated_file, 'r') as f:
                data = json.load(f)
                self.generated_history = [GeneratedChallenge(**g) for g in data]
        
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
    
    def _save_data(self):
        """Save templates, history, and stats"""
        with open(self.templates_file, 'w') as f:
            json.dump([asdict(t) for t in self.templates], f, indent=2)
        
        with open(self.generated_file, 'w') as f:
            json.dump([asdict(g) for g in self.generated_history], f, indent=2)
        
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def _initialize_templates(self):
        """Initialize challenge templates if not already loaded"""
        if self.templates:
            return  # Already loaded from file
        
        # Define base challenge templates
        base_templates = [
            # Algorithm Challenges
            ChallengeTemplate(
                template_id="algo_pattern_finder",
                title="Pattern Recognition in Code",
                category="algorithms",
                difficulty="medium",
                description="Build an algorithm that identifies repeating patterns in code repositories, inspired by the autonomous AI's pattern matching.",
                requirements=[
                    "Implement a pattern detection algorithm",
                    "Support multiple programming languages",
                    "Calculate pattern frequency and relevance",
                    "Provide pattern extraction and reporting"
                ],
                test_cases=[
                    {"input": "code_samples", "expected": "pattern_list", "description": "Detects common patterns"},
                    {"input": "edge_case_code", "expected": "no_patterns", "description": "Handles edge cases"}
                ],
                solution_hints=[
                    "Consider using abstract syntax trees (AST) for language-agnostic parsing",
                    "Implement sliding window algorithm for pattern detection",
                    "Use hashing for efficient pattern comparison"
                ],
                keywords=["pattern", "algorithm", "detection", "code analysis", "ast"],
                learning_sources=["autonomous_ai_pattern_matching"],
                estimated_time_minutes=90
            ),
            
            # Creative Coding
            ChallengeTemplate(
                template_id="creative_code_poetry",
                title="Functional Code Poetry Generator",
                category="creative",
                difficulty="medium",
                description="Create a system that generates executable code that is also aesthetically pleasing as poetry, inspired by the AI's creative capabilities.",
                requirements=[
                    "Generate syntactically valid code in target language",
                    "Code should read like poetry when formatted",
                    "Maintain functional correctness",
                    "Support multiple aesthetic styles"
                ],
                test_cases=[
                    {"input": "haiku_style", "expected": "valid_executable_haiku_code", "description": "Generates haiku-style code"},
                    {"input": "sonnet_style", "expected": "valid_executable_sonnet_code", "description": "Generates sonnet-style code"}
                ],
                solution_hints=[
                    "Use template-based code generation with poetic constraints",
                    "Implement syllable counting for code tokens",
                    "Balance aesthetics with functionality"
                ],
                keywords=["creative", "poetry", "code generation", "aesthetics"],
                learning_sources=["creative_ai_concepts"],
                estimated_time_minutes=120
            ),
            
            # API Design
            ChallengeTemplate(
                template_id="api_self_documenting",
                title="Self-Documenting API Generator",
                category="api",
                difficulty="hard",
                description="Build an API that automatically generates comprehensive documentation from its usage patterns, inspired by the self-documenting AI.",
                requirements=[
                    "Create a REST API with auto-documentation",
                    "Track usage patterns and common workflows",
                    "Generate examples from actual usage",
                    "Provide interactive documentation"
                ],
                test_cases=[
                    {"input": "api_endpoints", "expected": "generated_docs", "description": "Generates API documentation"},
                    {"input": "usage_patterns", "expected": "usage_examples", "description": "Creates usage examples"}
                ],
                solution_hints=[
                    "Implement middleware to capture API calls",
                    "Use OpenAPI/Swagger for documentation structure",
                    "Analyze request/response patterns for examples"
                ],
                keywords=["api", "documentation", "self-learning", "rest"],
                learning_sources=["self_documenting_ai"],
                estimated_time_minutes=150
            ),
            
            # Machine Learning
            ChallengeTemplate(
                template_id="ml_code_predictor",
                title="Code Completion Predictor",
                category="ml",
                difficulty="expert",
                description="Create a lightweight ML model that predicts the next line of code based on context, inspired by GitHub Copilot.",
                requirements=[
                    "Train a sequence prediction model",
                    "Support multiple programming languages",
                    "Provide confidence scores for predictions",
                    "Optimize for real-time inference"
                ],
                test_cases=[
                    {"input": "code_context", "expected": "predicted_line", "description": "Predicts next code line"},
                    {"input": "partial_function", "expected": "completion", "description": "Completes functions"}
                ],
                solution_hints=[
                    "Consider using LSTM or transformer-based architecture",
                    "Create a custom tokenizer for code",
                    "Train on public code repositories",
                    "Implement beam search for better predictions"
                ],
                keywords=["ml", "prediction", "code completion", "neural network"],
                learning_sources=["ai_ml_trends"],
                estimated_time_minutes=240
            ),
            
            # Data Structures
            ChallengeTemplate(
                template_id="ds_knowledge_graph",
                title="Dynamic Knowledge Graph Builder",
                category="data_structures",
                difficulty="hard",
                description="Implement a dynamic knowledge graph that learns relationships between concepts from code and documentation.",
                requirements=[
                    "Design graph data structure for knowledge representation",
                    "Implement relationship extraction from text",
                    "Support graph queries and traversal",
                    "Provide visualization capabilities"
                ],
                test_cases=[
                    {"input": "code_and_docs", "expected": "knowledge_graph", "description": "Builds knowledge graph"},
                    {"input": "query", "expected": "related_concepts", "description": "Queries relationships"}
                ],
                solution_hints=[
                    "Use adjacency list or matrix for graph representation",
                    "Implement NLP for relationship extraction",
                    "Consider using graph databases like Neo4j",
                    "Add weighting for relationship strength"
                ],
                keywords=["graph", "knowledge", "data structure", "nlp"],
                learning_sources=["knowledge_graph_system"],
                estimated_time_minutes=180
            ),
            
            # System Design
            ChallengeTemplate(
                template_id="sys_autonomous_workflow",
                title="Autonomous Workflow Orchestrator",
                category="system_design",
                difficulty="expert",
                description="Design a system that automatically orchestrates workflows based on dependencies and resource availability.",
                requirements=[
                    "Implement workflow dependency resolution",
                    "Support parallel and sequential execution",
                    "Handle resource constraints and conflicts",
                    "Provide monitoring and logging"
                ],
                test_cases=[
                    {"input": "workflow_definition", "expected": "execution_plan", "description": "Creates execution plan"},
                    {"input": "resource_limits", "expected": "optimized_schedule", "description": "Optimizes scheduling"}
                ],
                solution_hints=[
                    "Use directed acyclic graphs (DAG) for dependencies",
                    "Implement topological sorting for execution order",
                    "Consider priority queues for scheduling",
                    "Add circuit breakers for fault tolerance"
                ],
                keywords=["workflow", "orchestration", "system design", "dag"],
                learning_sources=["autonomous_pipeline"],
                estimated_time_minutes=200
            ),
            
            # Easy Entry-Level
            ChallengeTemplate(
                template_id="algo_commit_analyzer",
                title="Git Commit Message Analyzer",
                category="algorithms",
                difficulty="easy",
                description="Build a tool that analyzes git commit messages to identify patterns and suggest improvements.",
                requirements=[
                    "Parse git commit messages",
                    "Identify common patterns and conventions",
                    "Suggest improvements for clarity",
                    "Generate statistics and insights"
                ],
                test_cases=[
                    {"input": "commit_messages", "expected": "analysis_report", "description": "Analyzes commits"},
                    {"input": "bad_message", "expected": "suggestions", "description": "Provides suggestions"}
                ],
                solution_hints=[
                    "Use regular expressions for pattern matching",
                    "Implement keyword extraction",
                    "Check against conventional commit standards"
                ],
                keywords=["git", "commit", "analysis", "patterns"],
                learning_sources=["code_analysis"],
                estimated_time_minutes=60
            ),
            
            # Creative - Visual
            ChallengeTemplate(
                template_id="creative_code_visualizer",
                title="Real-Time Code Execution Visualizer",
                category="creative",
                difficulty="medium",
                description="Create an animated visualizer that shows code execution flow in real-time, making algorithms come alive.",
                requirements=[
                    "Parse and instrument code for tracking",
                    "Create visual representation of execution",
                    "Support step-through debugging",
                    "Animate data structure changes"
                ],
                test_cases=[
                    {"input": "sorting_algorithm", "expected": "animated_visualization", "description": "Visualizes sorting"},
                    {"input": "tree_traversal", "expected": "tree_animation", "description": "Animates tree operations"}
                ],
                solution_hints=[
                    "Use code instrumentation for execution tracking",
                    "Implement canvas or SVG for visualization",
                    "Add timeline controls for playback",
                    "Consider using D3.js for data visualization"
                ],
                keywords=["visualization", "animation", "execution", "debugging"],
                learning_sources=["visual_programming"],
                estimated_time_minutes=120
            )
        ]
        
        # Set creation timestamp for all templates
        now = datetime.now(timezone.utc).isoformat()
        for template in base_templates:
            template.created_at = now
        
        self.templates = base_templates
        self._save_data()
    
    def generate_challenge(self, 
                          category: Optional[str] = None,
                          difficulty: Optional[str] = None,
                          learning_context: Optional[str] = None) -> GeneratedChallenge:
        """
        Generate a coding challenge based on criteria.
        
        Args:
            category: Specific category or None for random
            difficulty: Specific difficulty or None for random
            learning_context: Text from recent learnings to influence selection
        
        Returns:
            GeneratedChallenge instance
        """
        # Filter templates by criteria
        candidates = self.templates
        
        if category:
            candidates = [t for t in candidates if t.category == category]
        
        if difficulty:
            candidates = [t for t in candidates if t.difficulty == difficulty]
        
        if not candidates:
            raise ValueError("No templates match the specified criteria")
        
        # Score templates by learning context if provided
        if learning_context:
            scored_templates = []
            for template in candidates:
                score = template.matches_keywords(learning_context)
                scored_templates.append((template, score))
            
            # Sort by score and use weighted random selection
            scored_templates.sort(key=lambda x: x[1], reverse=True)
            
            # Use top 3 with weighted probability
            top_templates = scored_templates[:min(3, len(scored_templates))]
            weights = [score for _, score in top_templates]
            
            if sum(weights) > 0:
                selected_template = random.choices(
                    [t for t, _ in top_templates],
                    weights=weights,
                    k=1
                )[0]
            else:
                selected_template = random.choice(candidates)
        else:
            selected_template = random.choice(candidates)
        
        # Generate unique challenge ID with microseconds for uniqueness
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp())
        microseconds = now.microsecond
        challenge_id = f"challenge-{selected_template.template_id}-{timestamp}-{microseconds}"
        
        # Create challenge instance
        challenge = GeneratedChallenge(
            challenge_id=challenge_id,
            template_id=selected_template.template_id,
            title=selected_template.title,
            category=selected_template.category,
            difficulty=selected_template.difficulty,
            full_description=self._format_challenge_description(selected_template),
            requirements=selected_template.requirements,
            test_cases=selected_template.test_cases,
            hints=selected_template.solution_hints,
            timestamp=datetime.now(timezone.utc).isoformat(),
            learning_context=learning_context or "",
            inspiration_sources=selected_template.learning_sources
        )
        
        # Update template usage
        selected_template.usage_count += 1
        
        # Save to history
        self.generated_history.append(challenge)
        self._save_data()
        
        return challenge
    
    def _format_challenge_description(self, template: ChallengeTemplate) -> str:
        """Format full challenge description with all details"""
        sections = [
            f"# {template.title}",
            f"",
            f"**Category:** {template.category.replace('_', ' ').title()}",
            f"**Difficulty:** {template.difficulty.title()}",
            f"**Estimated Time:** {template.estimated_time_minutes} minutes",
            f"",
            f"## Description",
            f"",
            template.description,
            f"",
            f"## Requirements",
            f""
        ]
        
        for i, req in enumerate(template.requirements, 1):
            sections.append(f"{i}. {req}")
        
        sections.extend([
            f"",
            f"## Test Cases",
            f""
        ])
        
        for i, test in enumerate(template.test_cases, 1):
            sections.append(f"### Test Case {i}: {test.get('description', 'Test')}")
            sections.append(f"- **Input:** `{test['input']}`")
            sections.append(f"- **Expected:** `{test['expected']}`")
            sections.append(f"")
        
        sections.extend([
            f"## Hints",
            f""
        ])
        
        for hint in template.solution_hints:
            sections.append(f"- {hint}")
        
        sections.extend([
            f"",
            f"## Inspiration",
            f"",
            f"This challenge was inspired by concepts from the Chained autonomous AI ecosystem:",
        ])
        
        for source in template.learning_sources:
            sections.append(f"- {source.replace('_', ' ').title()}")
        
        return "\n".join(sections)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        stats = {
            "total_templates": len(self.templates),
            "total_generated": len(self.generated_history),
            "by_category": {},
            "by_difficulty": {},
            "popular_templates": [],
            "recent_generations": []
        }
        
        # Count by category
        for template in self.templates:
            cat = template.category
            if cat not in stats["by_category"]:
                stats["by_category"][cat] = {
                    "count": 0,
                    "avg_time": 0,
                    "templates": []
                }
            stats["by_category"][cat]["count"] += 1
            stats["by_category"][cat]["templates"].append(template.template_id)
        
        # Count by difficulty
        for template in self.templates:
            diff = template.difficulty
            if diff not in stats["by_difficulty"]:
                stats["by_difficulty"][diff] = 0
            stats["by_difficulty"][diff] += 1
        
        # Most used templates
        sorted_templates = sorted(self.templates, key=lambda t: t.usage_count, reverse=True)
        stats["popular_templates"] = [
            {
                "id": t.template_id,
                "title": t.title,
                "usage_count": t.usage_count
            }
            for t in sorted_templates[:5]
        ]
        
        # Recent generations
        recent = sorted(self.generated_history, key=lambda g: g.timestamp, reverse=True)[:10]
        stats["recent_generations"] = [
            {
                "id": g.challenge_id,
                "title": g.title,
                "timestamp": g.timestamp
            }
            for g in recent
        ]
        
        return stats
    
    def get_learning_inspired_challenges(self, learnings_dir: str = "learnings") -> List[GeneratedChallenge]:
        """
        Generate challenges inspired by recent learnings.
        
        Args:
            learnings_dir: Path to learnings directory
        
        Returns:
            List of generated challenges
        """
        learnings_path = Path(learnings_dir)
        if not learnings_path.exists():
            return []
        
        challenges = []
        
        # Read recent learning files
        learning_files = sorted(learnings_path.glob("*.json"), reverse=True)[:5]
        
        for learning_file in learning_files:
            try:
                with open(learning_file, 'r') as f:
                    learning_data = json.load(f)
                
                # Extract context from learning
                context_parts = []
                
                if "topics" in learning_data:
                    context_parts.extend(learning_data["topics"].keys())
                
                if "insights" in learning_data:
                    insights = learning_data["insights"]
                    if isinstance(insights, list):
                        context_parts.extend([str(i) for i in insights[:3]])
                
                learning_context = " ".join(context_parts)
                
                # Generate challenge inspired by this learning
                if learning_context:
                    challenge = self.generate_challenge(learning_context=learning_context)
                    challenges.append(challenge)
                    
            except Exception as e:
                print(f"Warning: Could not process {learning_file}: {e}")
                continue
        
        return challenges


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Creative Coding Challenge Generator")
    parser.add_argument("--category", choices=["algorithms", "data_structures", "api", "ml", "creative", "system_design"],
                       help="Challenge category")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "expert"],
                       help="Challenge difficulty")
    parser.add_argument("--learning-context", type=str,
                       help="Learning context to influence challenge selection")
    parser.add_argument("--stats", action="store_true",
                       help="Show statistics")
    parser.add_argument("--output", type=str,
                       help="Output file for generated challenge")
    
    args = parser.parse_args()
    
    generator = CreativeCodingChallengeGenerator()
    
    if args.stats:
        stats = generator.get_statistics()
        print("\n=== Creative Coding Challenge Generator Statistics ===\n")
        print(json.dumps(stats, indent=2))
        return
    
    # Generate challenge
    challenge = generator.generate_challenge(
        category=args.category,
        difficulty=args.difficulty,
        learning_context=args.learning_context
    )
    
    print("\n=== Generated Challenge ===\n")
    print(challenge.full_description)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(asdict(challenge), f, indent=2)
        
        print(f"\n✓ Challenge saved to: {args.output}")
    
    print(f"\n✓ Challenge ID: {challenge.challenge_id}")
    print(f"✓ Template: {challenge.template_id}")


if __name__ == "__main__":
    main()
