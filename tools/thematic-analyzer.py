#!/usr/bin/env python3
"""
Thematic Analysis Engine

Analyzes trending topics across learnings to identify hot technologies, frameworks,
companies, and tech personalities. Calculates trend scores and momentum.

Part of the Chained autonomous AI ecosystem.
Created by Create Guru - inspired by Nikola Tesla's vision for pattern recognition.
"""

import json
import re
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class TrendMetrics:
    """Metrics for a trending topic"""
    name: str
    category: str
    mention_count: int
    sources: List[str]
    momentum: float  # Trend velocity (recent vs older mentions)
    score: float  # Overall trend score (0-100)
    sample_titles: List[str]
    keywords: List[str]


@dataclass
class PersonalityMention:
    """Mention of a tech personality in the news"""
    name: str
    mention_count: int
    context: List[str]  # Sample contexts where mentioned
    relevance_score: float


@dataclass
class ThematicAnalysis:
    """Complete thematic analysis results"""
    timestamp: str
    analysis_period_days: int
    total_learnings_analyzed: int
    top_technologies: List[TrendMetrics]
    top_companies: List[TrendMetrics]
    top_frameworks: List[TrendMetrics]
    notable_personalities: List[PersonalityMention]
    emerging_topics: List[TrendMetrics]
    hot_themes: List[str]  # High-level themes for agent spawning


class ThematicAnalyzer:
    """
    Analyzes learning content to identify trends and hot topics.
    
    Features:
    - Track technology mentions and trends
    - Identify hot companies and products
    - Detect framework and tool popularity
    - Find tech personalities in the news
    - Calculate trend momentum and scores
    - Generate themes for agent spawning
    """
    
    # Technology categories with keywords
    TECHNOLOGIES = {
        'AI/ML': [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'neural network',
            'deep learning', 'llm', 'large language model', 'gpt', 'chatgpt', 'claude',
            'gemini', 'copilot', 'transformer', 'bert', 'diffusion', 'stable diffusion',
            'midjourney', 'dall-e', 'generative ai', 'genai', 'rag', 'fine-tuning',
            'prompt engineering', 'embedding', 'vector database', 'agents'
        ],
        'Languages': [
            'python', 'javascript', 'typescript', 'rust', 'go', 'golang', 'java',
            'c++', 'cpp', 'c#', 'csharp', 'ruby', 'php', 'swift', 'kotlin',
            'dart', 'scala', 'elixir', 'haskell', 'zig', 'lua', 'r'
        ],
        'Web': [
            'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt', 'gatsby',
            'html', 'css', 'tailwind', 'bootstrap', 'webassembly', 'wasm',
            'pwa', 'web components', 'http', 'rest', 'graphql', 'api'
        ],
        'Backend': [
            'node.js', 'express', 'fastapi', 'django', 'flask', 'spring',
            'asp.net', 'rails', 'laravel', 'microservices', 'serverless',
            'lambda', 'edge computing'
        ],
        'Database': [
            'postgres', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'sqlite', 'dynamodb', 'cassandra', 'neo4j', 'supabase', 'firebase',
            'planetscale', 'cockroachdb', 'sql', 'nosql'
        ],
        'DevOps': [
            'docker', 'kubernetes', 'k8s', 'ci/cd', 'github actions', 'jenkins',
            'terraform', 'ansible', 'helm', 'argocd', 'prometheus', 'grafana',
            'datadog', 'cloudwatch', 'deployment', 'cloud', 'aws', 'azure', 'gcp'
        ],
        'Security': [
            'security', 'vulnerability', 'cve', 'encryption', 'ssl', 'tls',
            'authentication', 'authorization', 'oauth', 'jwt', 'zero trust',
            'penetration testing', 'devsecops'
        ],
        'Blockchain': [
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'web3',
            'smart contract', 'nft', 'defi', 'solidity', 'crypto'
        ]
    }
    
    # Known companies and organizations
    COMPANIES = [
        'google', 'microsoft', 'amazon', 'meta', 'facebook', 'apple', 'openai',
        'anthropic', 'nvidia', 'intel', 'amd', 'spacex', 'tesla', 'uber',
        'airbnb', 'netflix', 'spotify', 'stripe', 'github', 'gitlab',
        'cloudflare', 'vercel', 'netlify', 'aws', 'azure', 'gcp'
    ]
    
    # Frameworks and tools
    FRAMEWORKS = [
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'hugging face',
        'langchain', 'llamaindex', 'react', 'vue', 'angular', 'django',
        'flask', 'express', 'spring boot', 'next.js', 'docker', 'kubernetes'
    ]
    
    # Tech personalities (CEO, founders, influential engineers)
    PERSONALITIES = {
        'elon musk': ['elon', 'musk'],
        'sam altman': ['sam altman', 'altman'],
        'satya nadella': ['satya', 'nadella'],
        'sundar pichai': ['sundar', 'pichai'],
        'jensen huang': ['jensen huang', 'huang'],
        'mark zuckerberg': ['zuckerberg'],
        'jeff bezos': ['bezos'],
        'tim cook': ['tim cook'],
        'linus torvalds': ['linus', 'torvalds'],
        'guido van rossum': ['guido'],
        'james gosling': ['gosling'],
        'rich hickey': ['rich hickey'],
        'yann lecun': ['lecun'],
        'geoffrey hinton': ['hinton'],
        'andrew ng': ['andrew ng'],
        'ilya sutskever': ['sutskever'],
    }
    
    def __init__(self, lookback_days: int = 7):
        """
        Initialize the analyzer.
        
        Args:
            lookback_days: Number of days to analyze for trends
        """
        self.lookback_days = lookback_days
        self.cutoff_date = datetime.now() - timedelta(days=lookback_days)
    
    def extract_keywords(self, text: str, min_word_length: int = 3) -> List[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter out short words and common stop words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 'has', 'have'}
        keywords = [w for w in words if len(w) >= min_word_length and w not in stop_words]
        
        return keywords
    
    def find_technology_mentions(self, learnings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Find all technology mentions across learnings"""
        mentions = defaultdict(list)
        
        for learning in learnings:
            text = (learning.get('title', '') + ' ' + 
                   learning.get('description', '') + ' ' + 
                   learning.get('content', '')).lower()
            
            # Check each technology category
            for category, techs in self.TECHNOLOGIES.items():
                for tech in techs:
                    # Use word boundaries for exact matches
                    pattern = r'\b' + re.escape(tech) + r'\b'
                    if re.search(pattern, text):
                        mentions[tech].append({
                            'category': category,
                            'title': learning.get('title', ''),
                            'source': learning.get('source', ''),
                            'timestamp': learning.get('timestamp', ''),
                            'score': learning.get('score', 0)
                        })
        
        return mentions
    
    def find_company_mentions(self, learnings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Find company mentions in learnings"""
        mentions = defaultdict(list)
        
        for learning in learnings:
            text = (learning.get('title', '') + ' ' + 
                   learning.get('description', '')).lower()
            
            for company in self.COMPANIES:
                pattern = r'\b' + re.escape(company) + r'\b'
                if re.search(pattern, text):
                    mentions[company].append({
                        'title': learning.get('title', ''),
                        'source': learning.get('source', ''),
                        'timestamp': learning.get('timestamp', ''),
                    })
        
        return mentions
    
    def find_personality_mentions(self, learnings: List[Dict[str, Any]]) -> Dict[str, PersonalityMention]:
        """Find tech personality mentions in news"""
        mentions = defaultdict(list)
        
        for learning in learnings:
            text = (learning.get('title', '') + ' ' + 
                   learning.get('description', '')).lower()
            
            for name, patterns in self.PERSONALITIES.items():
                for pattern in patterns:
                    if pattern in text:
                        mentions[name].append(learning.get('title', ''))
                        break  # Only count once per learning
        
        # Convert to PersonalityMention objects
        personalities = []
        for name, contexts in mentions.items():
            if len(contexts) >= 2:  # At least 2 mentions to be notable
                personalities.append(PersonalityMention(
                    name=name.title(),
                    mention_count=len(contexts),
                    context=contexts[:3],  # Sample contexts
                    relevance_score=min(len(contexts) * 10, 100)
                ))
        
        return {p.name: p for p in personalities}
    
    def calculate_momentum(self, mentions: List[Dict[str, Any]]) -> float:
        """
        Calculate trend momentum based on recent vs older mentions.
        
        Returns a value between -1.0 (declining) and 1.0 (accelerating)
        """
        if not mentions:
            return 0.0
        
        # Split into recent and older
        mid_date = self.cutoff_date + timedelta(days=self.lookback_days / 2)
        
        recent = []
        older = []
        
        for mention in mentions:
            timestamp_str = mention.get('timestamp', '')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if timestamp >= mid_date:
                        recent.append(mention)
                    else:
                        older.append(mention)
                except:
                    pass
        
        # Calculate momentum
        recent_count = len(recent)
        older_count = len(older)
        total = recent_count + older_count
        
        if total == 0:
            return 0.0
        
        # Momentum is the difference in ratios
        momentum = (recent_count - older_count) / total
        
        return momentum
    
    def calculate_trend_score(self, mentions: List[Dict[str, Any]], momentum: float) -> float:
        """Calculate overall trend score (0-100)"""
        # Base score on mention count
        mention_score = min(len(mentions) * 5, 60)
        
        # Add momentum bonus (up to 30 points)
        momentum_bonus = (momentum + 1) * 15  # Converts -1..1 to 0..30
        
        # Add source diversity bonus (up to 10 points)
        sources = set(m.get('source', '') for m in mentions)
        diversity_bonus = min(len(sources) * 3, 10)
        
        total_score = mention_score + momentum_bonus + diversity_bonus
        
        return min(total_score, 100)
    
    def analyze_learnings(self, learnings: List[Dict[str, Any]]) -> ThematicAnalysis:
        """
        Perform complete thematic analysis on learnings.
        
        Args:
            learnings: List of learning dictionaries
            
        Returns:
            ThematicAnalysis object with all trend data
        """
        # Find all mentions
        tech_mentions = self.find_technology_mentions(learnings)
        company_mentions = self.find_company_mentions(learnings)
        personality_mentions = self.find_personality_mentions(learnings)
        
        # Calculate trend metrics for technologies
        tech_trends = []
        for tech, mentions in tech_mentions.items():
            if len(mentions) >= 2:  # At least 2 mentions to be a trend
                momentum = self.calculate_momentum(mentions)
                score = self.calculate_trend_score(mentions, momentum)
                
                tech_trends.append(TrendMetrics(
                    name=tech,
                    category=mentions[0]['category'],
                    mention_count=len(mentions),
                    sources=list(set(m['source'] for m in mentions)),
                    momentum=momentum,
                    score=score,
                    sample_titles=[m['title'] for m in mentions[:3]],
                    keywords=[tech]
                ))
        
        # Sort by score
        tech_trends.sort(key=lambda x: x.score, reverse=True)
        
        # Calculate company trends
        company_trends = []
        for company, mentions in company_mentions.items():
            if len(mentions) >= 2:
                momentum = self.calculate_momentum(mentions)
                score = self.calculate_trend_score(mentions, momentum)
                
                company_trends.append(TrendMetrics(
                    name=company.title(),
                    category='Company',
                    mention_count=len(mentions),
                    sources=list(set(m['source'] for m in mentions)),
                    momentum=momentum,
                    score=score,
                    sample_titles=[m['title'] for m in mentions[:3]],
                    keywords=[company]
                ))
        
        company_trends.sort(key=lambda x: x.score, reverse=True)
        
        # Identify hot themes for agent spawning
        hot_themes = self._identify_hot_themes(tech_trends, company_trends)
        
        # Identify emerging topics (high momentum, moderate mentions)
        emerging = [t for t in tech_trends if t.momentum > 0.3 and 2 <= t.mention_count <= 5]
        emerging.sort(key=lambda x: x.momentum, reverse=True)
        
        return ThematicAnalysis(
            timestamp=datetime.now().isoformat(),
            analysis_period_days=self.lookback_days,
            total_learnings_analyzed=len(learnings),
            top_technologies=tech_trends[:10],
            top_companies=company_trends[:10],
            top_frameworks=[],  # Could be expanded
            notable_personalities=list(personality_mentions.values())[:5],
            emerging_topics=emerging[:5],
            hot_themes=hot_themes
        )
    
    def _identify_hot_themes(self, tech_trends: List[TrendMetrics], 
                            company_trends: List[TrendMetrics]) -> List[str]:
        """Identify hot themes suitable for spawning specialized agents"""
        themes = []
        
        # Check for AI/ML dominance
        ai_trends = [t for t in tech_trends[:10] if t.category == 'AI/ML']
        if len(ai_trends) >= 3:
            # Find specific AI sub-theme
            ai_keywords = []
            for t in ai_trends:
                ai_keywords.extend(t.keywords)
            
            keyword_counts = Counter(ai_keywords)
            if 'agents' in keyword_counts or 'agent' in str(ai_keywords):
                themes.append('ai-agents')
            elif 'llm' in keyword_counts or 'gpt' in keyword_counts:
                themes.append('llm-specialist')
            else:
                themes.append('ai-ml-integration')
        
        # Check for security trends
        security_trends = [t for t in tech_trends[:15] if t.category == 'Security']
        if len(security_trends) >= 2:
            themes.append('security-automation')
        
        # Check for specific languages trending
        lang_trends = [t for t in tech_trends[:10] if t.category == 'Languages']
        if lang_trends:
            top_lang = lang_trends[0].name
            if top_lang in ['rust', 'go', 'zig']:
                themes.append(f'{top_lang}-specialist')
        
        # Check for DevOps trends
        devops_trends = [t for t in tech_trends[:15] if t.category == 'DevOps']
        if len(devops_trends) >= 3:
            themes.append('cloud-infrastructure')
        
        # Check for database trends
        db_trends = [t for t in tech_trends[:15] if t.category == 'Database']
        if len(db_trends) >= 2:
            themes.append('data-engineering')
        
        return themes[:5]  # Limit to top 5 themes
    
    def load_learnings_from_files(self, learnings_dir: str) -> List[Dict[str, Any]]:
        """Load learnings from JSON files in a directory"""
        learnings_path = Path(learnings_dir)
        all_learnings = []
        
        # Find all JSON files
        json_files = list(learnings_path.glob('*.json'))
        json_files = [f for f in json_files if f.name not in ['index.json']]
        
        for json_file in json_files:
            try:
                # Check if file is recent enough
                file_mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
                if file_mtime < self.cutoff_date:
                    continue
                
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                learnings = data.get('learnings', [])
                all_learnings.extend(learnings)
                
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")
        
        return all_learnings


def main():
    """CLI interface for thematic analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze trends in learning content')
    parser.add_argument('learnings_dir', help='Directory containing learning JSON files')
    parser.add_argument('--output', '-o', help='Output file for analysis results')
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Analyze
    analyzer = ThematicAnalyzer(lookback_days=args.days)
    learnings = analyzer.load_learnings_from_files(args.learnings_dir)
    
    print(f"Loaded {len(learnings)} learnings from the last {args.days} days")
    
    analysis = analyzer.analyze_learnings(learnings)
    
    # Output
    if args.json:
        output_data = asdict(analysis)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"✓ Analysis written to {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
    else:
        # Pretty print
        print("\n=== THEMATIC ANALYSIS RESULTS ===\n")
        print(f"Analysis Period: {analysis.analysis_period_days} days")
        print(f"Total Learnings: {analysis.total_learnings_analyzed}\n")
        
        print("🔥 TOP TECHNOLOGIES:")
        for i, tech in enumerate(analysis.top_technologies[:5], 1):
            print(f"{i}. {tech.name.upper()} ({tech.category})")
            print(f"   Score: {tech.score:.1f} | Mentions: {tech.mention_count} | Momentum: {tech.momentum:+.2f}")
            print(f"   Sample: {tech.sample_titles[0][:80]}...")
            print()
        
        if analysis.top_companies:
            print("\n🏢 TOP COMPANIES:")
            for i, company in enumerate(analysis.top_companies[:5], 1):
                print(f"{i}. {company.name} - {company.mention_count} mentions (score: {company.score:.1f})")
        
        if analysis.notable_personalities:
            print("\n👤 NOTABLE PERSONALITIES:")
            for p in analysis.notable_personalities:
                print(f"- {p.name}: {p.mention_count} mentions")
                print(f"  Context: {p.context[0][:80]}...")
        
        if analysis.emerging_topics:
            print("\n🌟 EMERGING TOPICS:")
            for topic in analysis.emerging_topics:
                print(f"- {topic.name} (momentum: {topic.momentum:+.2f})")
        
        print("\n🎯 HOT THEMES FOR AGENT SPAWNING:")
        for theme in analysis.hot_themes:
            print(f"- {theme}")


if __name__ == '__main__':
    main()
