#!/usr/bin/env python3
"""
Self-Improving Prompt Generator Enhancement Module

Adds advanced self-improvement capabilities:
- Genetic algorithm for prompt evolution
- Multi-dimensional quality scoring
- Automated feedback extraction from PR reviews
- Intelligent template crossover and mutation

Created by @construct-specialist - direct and practical approach for systems that work.
Part of the Chained autonomous AI ecosystem.
"""

import json
import re
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class PromptQualityScore:
    """Multi-dimensional quality assessment for prompts"""
    clarity: float  # 0-1: How clear and understandable
    completeness: float  # 0-1: How comprehensive
    actionability: float  # 0-1: How actionable the instructions are
    specificity: float  # 0-1: How specific vs generic
    success_rate: float  # 0-1: Historical success rate
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score"""
        return (
            self.clarity * 0.2 +
            self.completeness * 0.2 +
            self.actionability * 0.25 +
            self.specificity * 0.15 +
            self.success_rate * 0.2
        )


@dataclass
class PromptGene:
    """Represents a genetic component of a prompt"""
    gene_id: str
    gene_type: str  # "structure", "instruction", "constraint", "example"
    content: str
    fitness_score: float = 0.5  # 0-1 effectiveness score


class PromptSelfImprover:
    """
    Advanced self-improvement engine for prompt generation.
    
    Uses genetic algorithms and multi-dimensional scoring to continuously
    evolve and optimize prompts based on real-world performance.
    """
    
    def __init__(self, data_dir: str = "tools/data/prompts"):
        """Initialize the self-improver"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.genes_file = self.data_dir / "prompt_genes.json"
        self.quality_scores_file = self.data_dir / "quality_scores.json"
        self.evolution_history_file = self.data_dir / "evolution_history.json"
        
        self.prompt_genes: Dict[str, PromptGene] = {}
        self.quality_scores: Dict[str, PromptQualityScore] = {}
        self.evolution_history: List[Dict[str, Any]] = []
        
        self._load_data()
        self._initialize_default_genes()
    
    def _load_data(self):
        """Load existing data"""
        if self.genes_file.exists():
            try:
                with open(self.genes_file, 'r') as f:
                    data = json.load(f)
                    self.prompt_genes = {
                        gid: PromptGene(**gdata)
                        for gid, gdata in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load genes: {e}")
        
        if self.quality_scores_file.exists():
            try:
                with open(self.quality_scores_file, 'r') as f:
                    data = json.load(f)
                    self.quality_scores = {
                        pid: PromptQualityScore(**qdata)
                        for pid, qdata in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load quality scores: {e}")
        
        if self.evolution_history_file.exists():
            try:
                with open(self.evolution_history_file, 'r') as f:
                    self.evolution_history = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load evolution history: {e}")
    
    def _save_data(self):
        """Save all data"""
        with open(self.genes_file, 'w') as f:
            json.dump(
                {gid: asdict(g) for gid, g in self.prompt_genes.items()},
                f,
                indent=2
            )
        
        with open(self.quality_scores_file, 'w') as f:
            json.dump(
                {pid: asdict(q) for pid, q in self.quality_scores.items()},
                f,
                indent=2
            )
        
        with open(self.evolution_history_file, 'w') as f:
            json.dump(self.evolution_history, f, indent=2)
    
    def _initialize_default_genes(self):
        """Initialize default prompt genes if not present"""
        if self.prompt_genes:
            return  # Already initialized
        
        default_genes = [
            # Structure genes
            PromptGene(
                gene_id="structure_numbered_steps",
                gene_type="structure",
                content="1. **Step**: Description\n2. **Step**: Description",
                fitness_score=0.7
            ),
            PromptGene(
                gene_id="structure_principles_section",
                gene_type="structure",
                content="**Key Principles:**\n- Principle 1\n- Principle 2",
                fitness_score=0.6
            ),
            # Instruction genes
            PromptGene(
                gene_id="instruction_test_thoroughly",
                gene_type="instruction",
                content="Test your changes thoroughly, including edge cases",
                fitness_score=0.8
            ),
            PromptGene(
                gene_id="instruction_minimal_changes",
                gene_type="instruction",
                content="Make minimal, surgical changes to reduce risk",
                fitness_score=0.75
            ),
            PromptGene(
                gene_id="instruction_document_decisions",
                gene_type="instruction",
                content="Document all design decisions and trade-offs",
                fitness_score=0.65
            ),
            # Constraint genes
            PromptGene(
                gene_id="constraint_follow_conventions",
                gene_type="constraint",
                content="Follow existing code patterns and conventions",
                fitness_score=0.7
            ),
            PromptGene(
                gene_id="constraint_handle_errors",
                gene_type="constraint",
                content="Handle all error conditions gracefully",
                fitness_score=0.7
            ),
        ]
        
        for gene in default_genes:
            self.prompt_genes[gene.gene_id] = gene
        
        self._save_data()
    
    def assess_prompt_quality(self, prompt_text: str, historical_success_rate: float = 0.5) -> PromptQualityScore:
        """
        Assess prompt quality across multiple dimensions.
        
        Args:
            prompt_text: The prompt to assess
            historical_success_rate: Success rate from usage data
        
        Returns:
            Multi-dimensional quality score
        """
        # Clarity: Based on sentence structure and readability
        clarity = self._calculate_clarity(prompt_text)
        
        # Completeness: Based on presence of key sections
        completeness = self._calculate_completeness(prompt_text)
        
        # Actionability: Based on imperative verbs and concrete instructions
        actionability = self._calculate_actionability(prompt_text)
        
        # Specificity: Based on detail level and examples
        specificity = self._calculate_specificity(prompt_text)
        
        return PromptQualityScore(
            clarity=clarity,
            completeness=completeness,
            actionability=actionability,
            specificity=specificity,
            success_rate=historical_success_rate
        )
    
    def _calculate_clarity(self, text: str) -> float:
        """Calculate clarity score based on text structure"""
        score = 0.5  # Base score
        
        # Positive indicators
        if "**" in text:  # Has emphasis/headers
            score += 0.1
        if re.search(r'\d+\.\s+', text):  # Has numbered lists
            score += 0.1
        if len(text.split('\n\n')) >= 3:  # Has paragraph breaks
            score += 0.1
        
        # Negative indicators
        avg_sentence_length = len(text) / max(1, text.count('.'))
        if avg_sentence_length > 200:  # Very long sentences
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_completeness(self, text: str) -> float:
        """Calculate completeness based on key sections"""
        score = 0.3  # Base score
        
        # Check for important sections
        if "**Key Principles:**" in text or "**Standards:**" in text:
            score += 0.2
        if re.search(r'\d+\.\s+\*\*', text):  # Numbered steps with headers
            score += 0.2
        if "Issue details:" in text or "request:" in text:  # Context reference
            score += 0.15
        if any(word in text.lower() for word in ["test", "validate", "verify"]):
            score += 0.15
        
        return min(1.0, score)
    
    def _calculate_actionability(self, text: str) -> float:
        """Calculate how actionable the instructions are"""
        score = 0.3  # Base score
        
        # Count imperative verbs
        action_verbs = [
            "implement", "create", "build", "test", "validate", 
            "analyze", "review", "fix", "refactor", "document",
            "ensure", "follow", "handle", "design", "plan"
        ]
        
        verb_count = sum(1 for verb in action_verbs if verb in text.lower())
        score += min(0.4, verb_count * 0.05)
        
        # Check for specific instructions
        if ":" in text and "-" in text:  # Has structured lists
            score += 0.2
        
        # Check for concrete examples
        if "example" in text.lower() or "```" in text:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_specificity(self, text: str) -> float:
        """Calculate how specific vs generic the prompt is"""
        score = 0.4  # Base score
        
        # Specific indicators
        if "{agent}" in text:  # Agent-specific
            score += 0.1
        if "{issue_body}" in text:  # Context-aware
            score += 0.1
        
        # Check for specific constraints
        specific_terms = ["minimal", "surgical", "comprehensive", "thorough", "defensive"]
        term_count = sum(1 for term in specific_terms if term in text.lower())
        score += min(0.3, term_count * 0.1)
        
        # Generic indicators (penalty)
        generic_phrases = ["do your best", "try to", "if possible", "maybe"]
        if any(phrase in text.lower() for phrase in generic_phrases):
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def extract_feedback_from_pr_review(self, review_body: str) -> Dict[str, Any]:
        """
        Extract actionable feedback from PR review comments.
        
        Args:
            review_body: The review comment text
        
        Returns:
            Structured feedback with sentiment and suggestions
        """
        feedback = {
            "sentiment": "neutral",
            "positive_patterns": [],
            "negative_patterns": [],
            "suggestions": []
        }
        
        # Sentiment analysis (simple keyword-based)
        positive_keywords = ["good", "great", "excellent", "clear", "thorough", "comprehensive"]
        negative_keywords = ["unclear", "missing", "incomplete", "confusing", "insufficient"]
        
        text_lower = review_body.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            feedback["sentiment"] = "positive"
        elif negative_count > positive_count:
            feedback["sentiment"] = "negative"
        
        # Extract positive patterns
        if "clear" in text_lower:
            feedback["positive_patterns"].append("clarity")
        if "thorough" in text_lower or "comprehensive" in text_lower:
            feedback["positive_patterns"].append("completeness")
        if "good test" in text_lower:
            feedback["positive_patterns"].append("testing")
        
        # Extract negative patterns
        if "unclear" in text_lower or "confusing" in text_lower:
            feedback["negative_patterns"].append("clarity_issue")
        if "missing" in text_lower:
            feedback["negative_patterns"].append("incompleteness")
        if "no test" in text_lower or "needs test" in text_lower:
            feedback["negative_patterns"].append("missing_tests")
        
        # Extract suggestions (lines starting with suggestion keywords)
        suggestion_patterns = [
            r"(?:should|could|consider|suggest|recommend)\s+(.+)",
            r"(?:please|try to)\s+(.+)",
            r"(?:add|include|ensure)\s+(.+)"
        ]
        
        for pattern in suggestion_patterns:
            matches = re.findall(pattern, text_lower, re.MULTILINE)
            feedback["suggestions"].extend(matches[:3])  # Limit to 3 per pattern
        
        return feedback
    
    def genetic_crossover(self, parent1_text: str, parent2_text: str) -> str:
        """
        Perform genetic crossover between two prompt templates.
        
        Combines successful elements from both parents to create offspring.
        
        Args:
            parent1_text: First parent prompt
            parent2_text: Second parent prompt
        
        Returns:
            New offspring prompt
        """
        # Split prompts into sections
        p1_sections = self._split_prompt_sections(parent1_text)
        p2_sections = self._split_prompt_sections(parent2_text)
        
        # Combine sections: take best from each
        offspring_sections = []
        
        # Header (take from parent1 if exists, otherwise parent2)
        if "header" in p1_sections:
            offspring_sections.append(p1_sections["header"])
        elif "header" in p2_sections:
            offspring_sections.append(p2_sections["header"])
        
        # Steps (alternate or merge)
        if "steps" in p1_sections and "steps" in p2_sections:
            # Merge steps from both
            p1_steps = p1_sections["steps"].split('\n')
            p2_steps = p2_sections["steps"].split('\n')
            
            # Take first 60% from p1, last 40% from p2
            split_point = int(len(p1_steps) * 0.6)
            merged_steps = p1_steps[:split_point] + p2_steps[split_point:]
            offspring_sections.append('\n'.join(merged_steps))
        elif "steps" in p1_sections:
            offspring_sections.append(p1_sections["steps"])
        elif "steps" in p2_sections:
            offspring_sections.append(p2_sections["steps"])
        
        # Principles (combine unique items)
        if "principles" in p1_sections or "principles" in p2_sections:
            p1_principles = p1_sections.get("principles", "")
            p2_principles = p2_sections.get("principles", "")
            
            # Extract bullet points
            p1_bullets = re.findall(r'-\s+(.+)', p1_principles)
            p2_bullets = re.findall(r'-\s+(.+)', p2_principles)
            
            # Combine unique bullets
            all_bullets = list(set(p1_bullets + p2_bullets))[:5]  # Max 5
            
            if all_bullets:
                principles_section = "**Key Principles:**\n" + '\n'.join(f"- {b}" for b in all_bullets)
                offspring_sections.append(principles_section)
        
        # Footer (issue context)
        if "footer" in p1_sections:
            offspring_sections.append(p1_sections["footer"])
        elif "footer" in p2_sections:
            offspring_sections.append(p2_sections["footer"])
        
        return '\n\n'.join(offspring_sections)
    
    def _split_prompt_sections(self, prompt_text: str) -> Dict[str, str]:
        """Split prompt into logical sections"""
        sections = {}
        
        # Header (everything before first numbered list)
        header_match = re.match(r'^(.*?)(?=\n1\.\s+)', prompt_text, re.DOTALL)
        if header_match:
            sections["header"] = header_match.group(1).strip()
        
        # Steps (numbered list)
        steps_match = re.search(r'((?:\n\d+\.\s+\*\*.*?\n.*?)+)', prompt_text, re.DOTALL)
        if steps_match:
            sections["steps"] = steps_match.group(1).strip()
        
        # Principles (section with Key Principles or Standards)
        principles_match = re.search(r'(\*\*(?:Key Principles|Standards):\*\*.*?)(?=\n\n|\Z)', prompt_text, re.DOTALL)
        if principles_match:
            sections["principles"] = principles_match.group(1).strip()
        
        # Footer (issue context reference)
        footer_match = re.search(r'((?:Issue details|Feature request|Refactoring target):.*)', prompt_text, re.DOTALL)
        if footer_match:
            sections["footer"] = footer_match.group(1).strip()
        
        return sections
    
    def mutate_prompt(self, prompt_text: str, mutation_strength: float = 0.3) -> str:
        """
        Apply random mutations to a prompt.
        
        Args:
            prompt_text: The prompt to mutate
            mutation_strength: How aggressive the mutation (0-1)
        
        Returns:
            Mutated prompt
        """
        # Choose mutation type based on strength
        if mutation_strength < 0.3:
            # Minor mutation: swap order of some steps
            return self._mutate_reorder(prompt_text)
        elif mutation_strength < 0.6:
            # Medium mutation: add or remove a section
            return self._mutate_add_remove(prompt_text)
        else:
            # Major mutation: inject high-performing genes
            return self._mutate_inject_genes(prompt_text)
    
    def _mutate_reorder(self, text: str) -> str:
        """Reorder steps in the prompt"""
        lines = text.split('\n')
        
        # Find numbered steps
        step_indices = [i for i, line in enumerate(lines) if re.match(r'^\d+\.\s+', line)]
        
        if len(step_indices) >= 3:
            # Swap two random steps
            i, j = random.sample(step_indices, 2)
            lines[i], lines[j] = lines[j], lines[i]
            
            # Renumber
            for idx, step_idx in enumerate(sorted(step_indices), 1):
                lines[step_idx] = re.sub(r'^\d+\.', f'{idx}.', lines[step_idx])
        
        return '\n'.join(lines)
    
    def _mutate_add_remove(self, text: str) -> str:
        """Add or remove a section"""
        # Randomly decide to add or remove
        if random.random() < 0.5 and "**Additional" not in text:
            # Add a section
            addition = "\n**Additional Focus:**\n- Verify edge cases\n- Ensure error handling\n"
            return text + addition
        else:
            # Remove optional sections (those after main content)
            if "**Additional" in text:
                text = text.split("**Additional")[0]
        
        return text
    
    def _mutate_inject_genes(self, text: str) -> str:
        """Inject high-performing genes into prompt"""
        # Get top performing genes
        top_genes = sorted(
            self.prompt_genes.values(),
            key=lambda g: g.fitness_score,
            reverse=True
        )[:3]
        
        # Add their content to the prompt
        additions = [f"- {gene.content}" for gene in top_genes if gene.gene_type == "instruction"]
        
        if additions and "**Key Principles:**" in text:
            # Inject into principles section
            text = text.replace(
                "**Key Principles:**",
                "**Key Principles:**\n" + '\n'.join(additions)
            )
        
        return text
    
    def evolve_generation(self, population: List[Tuple[str, float]], target_size: int = 5) -> List[str]:
        """
        Evolve a generation of prompts using genetic algorithm.
        
        Args:
            population: List of (prompt_text, fitness_score) tuples
            target_size: Target population size
        
        Returns:
            New generation of prompts
        """
        if len(population) < 2:
            return [p[0] for p in population]
        
        # Sort by fitness
        population = sorted(population, key=lambda x: x[1], reverse=True)
        
        new_generation = []
        
        # Elitism: Keep top 20%
        elite_count = max(1, int(len(population) * 0.2))
        new_generation.extend([p[0] for p in population[:elite_count]])
        
        # Crossover: Create offspring from top performers
        while len(new_generation) < target_size:
            # Select two parents (weighted by fitness)
            parent1 = random.choices(population[:len(population)//2], k=1)[0][0]
            parent2 = random.choices(population[:len(population)//2], k=1)[0][0]
            
            # Crossover
            offspring = self.genetic_crossover(parent1, parent2)
            
            # Maybe mutate (30% chance)
            if random.random() < 0.3:
                offspring = self.mutate_prompt(offspring, mutation_strength=0.4)
            
            new_generation.append(offspring)
        
        # Record evolution event
        self.evolution_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "generation_size": len(population),
            "top_fitness": population[0][1] if population else 0,
            "avg_fitness": sum(p[1] for p in population) / len(population) if population else 0
        })
        self._save_data()
        
        return new_generation[:target_size]
    
    def update_gene_fitness(self, gene_id: str, success: bool):
        """Update fitness score for a gene based on outcome"""
        if gene_id in self.prompt_genes:
            gene = self.prompt_genes[gene_id]
            
            # Update fitness using simple moving average
            if success:
                gene.fitness_score = gene.fitness_score * 0.9 + 0.1  # Move towards 1.0
            else:
                gene.fitness_score = gene.fitness_score * 0.9  # Move towards 0.0
            
            self._save_data()
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Generate evolution performance report"""
        return {
            "total_genes": len(self.prompt_genes),
            "avg_gene_fitness": sum(g.fitness_score for g in self.prompt_genes.values()) / len(self.prompt_genes) if self.prompt_genes else 0,
            "top_genes": sorted(
                [{"id": gid, "type": g.gene_type, "fitness": g.fitness_score} 
                 for gid, g in self.prompt_genes.items()],
                key=lambda x: x["fitness"],
                reverse=True
            )[:10],
            "evolution_history": self.evolution_history[-20:],  # Last 20 events
            "quality_scores_tracked": len(self.quality_scores)
        }


def main():
    """Demo of self-improvement capabilities"""
    improver = PromptSelfImprover()
    
    # Demo 1: Quality assessment
    print("=" * 60)
    print("Demo: Prompt Quality Assessment")
    print("=" * 60)
    
    sample_prompt = """**@engineer-master** - Please fix this bug:

1. **Analyze**: Understand the root cause
2. **Plan**: Design minimal fix
3. **Test**: Validate thoroughly

**Key Principles:**
- Make minimal changes
- Add regression tests
- Document the fix"""
    
    quality = improver.assess_prompt_quality(sample_prompt, historical_success_rate=0.75)
    print(f"\nPrompt Quality Scores:")
    print(f"  Clarity:       {quality.clarity:.2f}")
    print(f"  Completeness:  {quality.completeness:.2f}")
    print(f"  Actionability: {quality.actionability:.2f}")
    print(f"  Specificity:   {quality.specificity:.2f}")
    print(f"  Success Rate:  {quality.success_rate:.2f}")
    print(f"  OVERALL:       {quality.overall_score:.2f}")
    
    # Demo 2: Genetic evolution
    print("\n" + "=" * 60)
    print("Demo: Genetic Evolution")
    print("=" * 60)
    
    population = [
        (sample_prompt, 0.75),
        (sample_prompt.replace("minimal", "comprehensive"), 0.68),
        (sample_prompt + "\n\n**Additional:** Check edge cases", 0.80)
    ]
    
    print(f"\nStarting population: {len(population)} prompts")
    new_gen = improver.evolve_generation(population, target_size=5)
    print(f"New generation: {len(new_gen)} prompts created")
    print(f"Evolution events: {len(improver.evolution_history)}")


if __name__ == "__main__":
    main()
