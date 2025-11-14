#!/usr/bin/env python3
"""
Prompt Learning Integration Module

Integrates learning insights from TLDR, Hacker News, and other sources
into the prompt generation system for continuous improvement.

Part of the self-improving prompt generator system.
Created by @engineer-master with systematic approach to learning integration.
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LearningInsight:
    """Represents a learning insight extracted from external sources"""
    title: str
    description: str
    source: str
    relevance_score: float  # 0-1 indicating relevance to prompting
    category: str  # e.g., "ai_ml", "programming", "devops", "security"
    keywords: List[str]
    url: Optional[str] = None
    timestamp: str = ""


class PromptLearningIntegrator:
    """
    Integrates external learning insights into prompt generation.
    
    Features:
    - Extract learnings from TLDR and HN files
    - Calculate relevance scores for different prompt categories
    - Identify trending technologies and patterns
    - Generate context-aware prompt enhancements
    - Track which learnings improve prompt effectiveness
    """
    
    def __init__(self, learnings_dir: str = "learnings", cache_dir: str = "tools/data/prompts"):
        """Initialize the learning integrator"""
        self.learnings_dir = Path(learnings_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.insights_cache_file = self.cache_dir / "learning_insights.json"
        self.trends_file = self.cache_dir / "trending_topics.json"
        
        self.insights: List[LearningInsight] = []
        self.trending_topics: Dict[str, Any] = {}
        
        # Category keywords for relevance scoring
        self.category_keywords = {
            "bug_fix": ["debug", "fix", "error", "bug", "issue", "troubleshoot", "crash"],
            "feature": ["implement", "build", "create", "develop", "feature", "functionality"],
            "refactor": ["refactor", "optimize", "clean", "improve", "restructure", "maintainability"],
            "documentation": ["document", "readme", "guide", "tutorial", "explain", "docs"],
            "investigation": ["analyze", "investigate", "research", "explore", "study", "audit"],
            "security": ["security", "vulnerability", "exploit", "auth", "encryption", "secure"],
            "ai_ml": ["ai", "ml", "llm", "gpt", "model", "agent", "neural", "training"],
            "devops": ["deploy", "ci", "cd", "infrastructure", "pipeline", "docker", "kubernetes"],
            "performance": ["performance", "speed", "optimize", "latency", "throughput", "scale"]
        }
        
        self._load_cache()
    
    def _load_cache(self):
        """Load cached insights and trends"""
        if self.insights_cache_file.exists():
            try:
                with open(self.insights_cache_file, 'r') as f:
                    data = json.load(f)
                    self.insights = [LearningInsight(**i) for i in data]
            except Exception as e:
                print(f"Warning: Could not load insights cache: {e}")
        
        if self.trends_file.exists():
            try:
                with open(self.trends_file, 'r') as f:
                    self.trending_topics = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load trends cache: {e}")
    
    def _save_cache(self):
        """Save insights and trends to cache"""
        try:
            with open(self.insights_cache_file, 'w') as f:
                json.dump([asdict(i) for i in self.insights], f, indent=2)
            
            with open(self.trends_file, 'w') as f:
                json.dump(self.trending_topics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def extract_learnings_from_tldr(self, days: int = 7) -> List[LearningInsight]:
        """
        Extract learnings from TLDR files.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of LearningInsight objects
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        new_insights = []
        
        # Find TLDR files from recent days
        tldr_files = sorted(self.learnings_dir.glob("tldr_*.json"), reverse=True)
        
        for tldr_file in tldr_files[:days * 3]:  # Check multiple files per day
            try:
                with open(tldr_file, 'r') as f:
                    data = json.load(f)
                
                # Check timestamp
                file_timestamp = data.get("timestamp", "")
                if file_timestamp:
                    file_date = datetime.fromisoformat(file_timestamp.replace('+00:00', '+00:00'))
                    if file_date < cutoff_date:
                        continue
                
                # Extract learnings
                learnings = data.get("learnings", [])
                for learning in learnings:
                    insight = self._create_insight_from_tldr(learning, data.get("source", "TLDR"))
                    if insight:
                        new_insights.append(insight)
                
                # Extract trends as potential learnings
                trends = data.get("trends", [])
                for trend in trends:
                    insight = self._create_insight_from_trend(trend, data.get("source", "TLDR"))
                    if insight:
                        new_insights.append(insight)
            
            except Exception as e:
                print(f"Warning: Could not process {tldr_file}: {e}")
                continue
        
        # Deduplicate and merge with existing insights
        self._merge_insights(new_insights)
        self._save_cache()
        
        return new_insights
    
    def _create_insight_from_tldr(self, learning: Dict[str, Any], source: str) -> Optional[LearningInsight]:
        """Create a LearningInsight from a TLDR learning entry"""
        title = learning.get("title", "")
        description = learning.get("description", "")
        content = learning.get("content", "")
        
        if not title:
            return None
        
        # Extract keywords
        keywords = self._extract_keywords(title + " " + description + " " + content)
        
        # Categorize and calculate relevance
        category = self._categorize_learning(title, description, content)
        relevance_score = self._calculate_relevance_score(keywords, category)
        
        return LearningInsight(
            title=title,
            description=description,
            source=source,
            relevance_score=relevance_score,
            category=category,
            keywords=keywords,
            url=learning.get("url"),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _create_insight_from_trend(self, trend: str, source: str) -> Optional[LearningInsight]:
        """Create a LearningInsight from a trend string"""
        if not trend or len(trend) < 10:
            return None
        
        # Extract keywords
        keywords = self._extract_keywords(trend)
        
        # Categorize
        category = self._categorize_learning(trend, "", "")
        relevance_score = self._calculate_relevance_score(keywords, category)
        
        return LearningInsight(
            title=trend,
            description="Trending topic from learning data",
            source=source,
            relevance_score=relevance_score,
            category=category,
            keywords=keywords,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter for meaningful keywords (length > 3)
        keywords = [w for w in words if len(w) > 3]
        
        # Get unique keywords
        return list(set(keywords))[:20]  # Limit to top 20
    
    def _categorize_learning(self, title: str, description: str, content: str) -> str:
        """Categorize a learning based on content"""
        combined_text = (title + " " + description + " " + content).lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            category_scores[category] = score
        
        # Return category with highest score, default to "ai_ml"
        if not category_scores or max(category_scores.values()) == 0:
            return "ai_ml"
        
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_relevance_score(self, keywords: List[str], category: str) -> float:
        """Calculate relevance score for prompt generation (0-1)"""
        # Base score from category relevance
        base_score = 0.5
        
        # Boost for AI/ML and programming topics
        if category in ["ai_ml", "feature", "bug_fix", "refactor"]:
            base_score += 0.2
        
        # Check for prompt-relevant keywords
        prompt_keywords = ["prompt", "agent", "copilot", "llm", "gpt", "ai", "automation"]
        relevance_boost = sum(0.05 for kw in keywords if any(pk in kw for pk in prompt_keywords))
        
        return min(1.0, base_score + relevance_boost)
    
    def _merge_insights(self, new_insights: List[LearningInsight]):
        """Merge new insights with existing, avoiding duplicates"""
        existing_titles = {insight.title for insight in self.insights}
        
        for insight in new_insights:
            if insight.title not in existing_titles:
                self.insights.append(insight)
                existing_titles.add(insight.title)
    
    def get_relevant_insights(
        self,
        prompt_category: str,
        limit: int = 5,
        min_relevance: float = 0.5
    ) -> List[LearningInsight]:
        """
        Get relevant insights for a specific prompt category.
        
        Args:
            prompt_category: The category of prompt (bug_fix, feature, etc.)
            limit: Maximum number of insights to return
            min_relevance: Minimum relevance score threshold
        
        Returns:
            List of relevant LearningInsight objects
        """
        # Filter by category and relevance
        relevant = [
            insight for insight in self.insights
            if (insight.category == prompt_category or prompt_category in ["investigation", "ai_ml"])
            and insight.relevance_score >= min_relevance
        ]
        
        # Sort by relevance score
        relevant.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant[:limit]
    
    def analyze_trending_topics(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze trending topics from recent learnings.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary of trending topics with counts and categories
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Filter recent insights
        recent_insights = [
            insight for insight in self.insights
            if datetime.fromisoformat(insight.timestamp) > cutoff_date
        ]
        
        # Count keyword frequencies
        keyword_counts = {}
        category_counts = {}
        
        for insight in recent_insights:
            # Count keywords
            for keyword in insight.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Count categories
            category_counts[insight.category] = category_counts.get(insight.category, 0) + 1
        
        # Get top trending keywords
        top_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        # Update trending topics
        self.trending_topics = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "analysis_period_days": days,
            "total_insights": len(recent_insights),
            "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords],
            "category_distribution": category_counts
        }
        
        self._save_cache()
        
        return self.trending_topics
    
    def generate_prompt_enhancements(
        self,
        prompt_category: str,
        base_prompt: str,
        max_enhancements: int = 3
    ) -> List[str]:
        """
        Generate prompt enhancements based on recent learnings.
        
        Args:
            prompt_category: Category of the prompt
            base_prompt: The base prompt text
            max_enhancements: Maximum number of enhancements to generate
        
        Returns:
            List of enhancement suggestions
        """
        relevant_insights = self.get_relevant_insights(prompt_category, limit=max_enhancements)
        
        enhancements = []
        for insight in relevant_insights:
            # Create enhancement based on insight
            enhancement = self._create_enhancement_from_insight(insight, prompt_category)
            if enhancement:
                enhancements.append(enhancement)
        
        return enhancements
    
    def _create_enhancement_from_insight(
        self,
        insight: LearningInsight,
        prompt_category: str
    ) -> Optional[str]:
        """Create a prompt enhancement from a learning insight"""
        # Map categories to enhancement templates
        if prompt_category == "feature" and "agent" in insight.keywords:
            return f"Consider implementing agentic patterns as seen in recent trends: {insight.title}"
        
        if prompt_category == "bug_fix" and "debug" in insight.keywords:
            return f"Apply modern debugging approaches: {insight.title}"
        
        if prompt_category == "security" and insight.category == "security":
            return f"Follow latest security best practices: {insight.title}"
        
        # Generic enhancement
        if insight.relevance_score > 0.7:
            return f"Recent insight: {insight.title}"
        
        return None
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected learnings"""
        return {
            "total_insights": len(self.insights),
            "categories": {
                category: sum(1 for i in self.insights if i.category == category)
                for category in set(i.category for i in self.insights)
            },
            "avg_relevance_score": sum(i.relevance_score for i in self.insights) / len(self.insights) if self.insights else 0,
            "trending_topics": self.trending_topics
        }


def main():
    """CLI interface for learning integration"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Integrate external learnings into prompt generation"
    )
    parser.add_argument(
        "command",
        choices=["extract", "analyze", "enhance", "stats"],
        help="Command to execute"
    )
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--category", help="Prompt category")
    parser.add_argument("--prompt", help="Base prompt text")
    
    args = parser.parse_args()
    
    integrator = PromptLearningIntegrator()
    
    if args.command == "extract":
        print(f"Extracting learnings from last {args.days} days...")
        insights = integrator.extract_learnings_from_tldr(args.days)
        print(f"Extracted {len(insights)} new insights")
        print(json.dumps([asdict(i) for i in insights[:5]], indent=2))
    
    elif args.command == "analyze":
        print(f"Analyzing trends from last {args.days} days...")
        trends = integrator.analyze_trending_topics(args.days)
        print(json.dumps(trends, indent=2))
    
    elif args.command == "enhance":
        if not args.category:
            print("Error: --category required for enhance")
            return 1
        
        base_prompt = args.prompt or "Implement this feature"
        enhancements = integrator.generate_prompt_enhancements(args.category, base_prompt)
        
        print("Prompt Enhancements:")
        for idx, enhancement in enumerate(enhancements, 1):
            print(f"{idx}. {enhancement}")
    
    elif args.command == "stats":
        stats = integrator.get_learning_statistics()
        print(json.dumps(stats, indent=2))
    
    return 0


if __name__ == "__main__":
    exit(main())
