#!/usr/bin/env python3
"""
Multi-Source Trend Aggregator - Proof of Concept
By @coach-master for AI/ML Innovation Mission (idea:27)

Demonstrates fetching and correlating trends from multiple sources:
- GitHub Trending
- Reddit r/programming
- Hacker News
- Future: Dev.to, ProductHunt, etc.

Usage:
    python3 tools/multi_source_aggregator.py

Output:
    - Console: Top cross-source trends
    - File: multi_source_trends.json
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional
import json
import os


class TrendSource:
    """Base class for trend sources"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def fetch(self) -> List[Dict]:
        """Fetch trends from source - to be implemented by subclasses"""
        raise NotImplementedError
    
    def format_trend(self, **kwargs) -> Dict:
        """Standard trend format"""
        return {
            "source": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }


class GitHubTrendingSource(TrendSource):
    """Fetch from GitHub Trending via API"""
    
    def __init__(self):
        super().__init__("github_trending")
        self.api_url = "https://api.github.com/search/repositories"
    
    async def fetch(self) -> List[Dict]:
        """Fetch trending repositories from GitHub"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for recently starred repos
                params = {
                    "q": "stars:>50 created:>2025-11-01",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 30
                }
                
                headers = {}
                # Use GitHub token if available
                github_token = os.environ.get("GITHUB_TOKEN")
                if github_token:
                    headers["Authorization"] = f"token {github_token}"
                
                async with session.get(
                    self.api_url, 
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        print(f"⚠️  GitHub API error: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    trends = []
                    for repo in data.get("items", []):
                        trends.append(self.format_trend(
                            title=repo["full_name"],
                            description=repo.get("description", ""),
                            url=repo["html_url"],
                            stars=repo["stargazers_count"],
                            language=repo.get("language", "Unknown"),
                            topics=repo.get("topics", [])
                        ))
                    
                    print(f"✅ Fetched {len(trends)} trends from GitHub")
                    return trends
                    
        except Exception as e:
            print(f"❌ Error fetching from GitHub: {e}")
            return []


class RedditSource(TrendSource):
    """Fetch from Reddit subreddit"""
    
    def __init__(self, subreddit: str = "programming"):
        super().__init__(f"reddit_{subreddit}")
        self.subreddit = subreddit
        self.api_url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    
    async def fetch(self) -> List[Dict]:
        """Fetch hot posts from Reddit"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": "Chained-Trend-Bot/1.0"}
                
                async with session.get(
                    self.api_url,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        print(f"⚠️  Reddit API error: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    trends = []
                    for post in data["data"]["children"][:30]:
                        post_data = post["data"]
                        trends.append(self.format_trend(
                            title=post_data["title"],
                            description=post_data.get("selftext", "")[:300],
                            url=post_data["url"],
                            score=post_data["score"],
                            comments=post_data["num_comments"]
                        ))
                    
                    print(f"✅ Fetched {len(trends)} trends from Reddit")
                    return trends
                    
        except Exception as e:
            print(f"❌ Error fetching from Reddit: {e}")
            return []


class HackerNewsSource(TrendSource):
    """Fetch from Hacker News"""
    
    def __init__(self):
        super().__init__("hacker_news")
        self.api_url = "https://hacker-news.firebaseio.com/v0"
    
    async def fetch(self) -> List[Dict]:
        """Fetch top stories from Hacker News"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get top story IDs
                async with session.get(f"{self.api_url}/topstories.json") as response:
                    if response.status != 200:
                        print(f"⚠️  HN API error: {response.status}")
                        return []
                    
                    story_ids = await response.json()
                    top_ids = story_ids[:30]  # Top 30 stories
                
                # Fetch story details
                trends = []
                for story_id in top_ids:
                    async with session.get(f"{self.api_url}/item/{story_id}.json") as response:
                        if response.status == 200:
                            story = await response.json()
                            if story and story.get("type") == "story":
                                trends.append(self.format_trend(
                                    title=story.get("title", ""),
                                    description=story.get("text", "")[:300] if story.get("text") else "",
                                    url=story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                                    score=story.get("score", 0),
                                    comments=story.get("descendants", 0)
                                ))
                
                print(f"✅ Fetched {len(trends)} trends from Hacker News")
                return trends
                
        except Exception as e:
            print(f"❌ Error fetching from Hacker News: {e}")
            return []


class TrendAggregator:
    """Aggregate and correlate trends from multiple sources"""
    
    def __init__(self):
        self.sources = {
            "github": GitHubTrendingSource(),
            "reddit": RedditSource("programming"),
            "hackernews": HackerNewsSource()
        }
    
    async def aggregate(self) -> List[Dict]:
        """Fetch from all sources in parallel"""
        print("\n🔍 Fetching trends from multiple sources...")
        
        results = await asyncio.gather(*[
            source.fetch() for source in self.sources.values()
        ], return_exceptions=True)
        
        all_trends = []
        for result in results:
            if isinstance(result, list):
                all_trends.extend(result)
            elif isinstance(result, Exception):
                print(f"⚠️  Source error: {result}")
        
        print(f"\n✅ Total trends fetched: {len(all_trends)}")
        return all_trends
    
    def correlate(self, trends: List[Dict]) -> List[Dict]:
        """
        Find topics appearing in multiple sources
        Uses simple keyword extraction and matching
        """
        print("\n🔗 Correlating trends across sources...")
        
        # Extract keywords from all trends
        keyword_sources = {}
        keyword_trends = {}
        
        for trend in trends:
            text = f"{trend.get('title', '')} {trend.get('description', '')}"
            keywords = self.extract_keywords(text)
            
            for keyword in keywords:
                if keyword not in keyword_sources:
                    keyword_sources[keyword] = set()
                    keyword_trends[keyword] = []
                
                keyword_sources[keyword].add(trend["source"])
                keyword_trends[keyword].append(trend)
        
        # Find cross-source keywords (appear in 2+ sources)
        cross_source_keywords = {
            kw: sources for kw, sources in keyword_sources.items()
            if len(sources) >= 2
        }
        
        print(f"✅ Found {len(cross_source_keywords)} cross-source keywords")
        
        # Calculate relevance score for each trend
        for trend in trends:
            text = f"{trend.get('title', '')} {trend.get('description', '')}"
            keywords = self.extract_keywords(text)
            
            # Score based on cross-source keyword presence
            cross_source_score = sum(
                len(cross_source_keywords.get(kw, set())) 
                for kw in keywords
            )
            
            # Bonus for high engagement
            engagement_score = (
                trend.get("stars", 0) / 100 +
                trend.get("score", 0) / 10 +
                trend.get("comments", 0) / 10
            )
            
            trend["relevance_score"] = cross_source_score + engagement_score
            trend["cross_source_keywords"] = [
                kw for kw in keywords if kw in cross_source_keywords
            ]
        
        # Sort by relevance
        trends.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return trends
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text
        Simple word filtering - can be enhanced with NLP
        """
        # Common programming/tech stopwords to exclude
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", 
            "for", "of", "with", "as", "is", "was", "are", "be", "have",
            "has", "had", "do", "does", "did", "will", "can", "could",
            "should", "would", "may", "might", "this", "that", "these",
            "those", "i", "you", "he", "she", "it", "we", "they", "what",
            "which", "who", "when", "where", "why", "how", "all", "each",
            "every", "some", "any", "few", "more", "most", "other", "some",
            "such", "no", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "now"
        }
        
        # Clean and split text
        text = text.lower()
        words = text.split()
        
        # Filter and deduplicate
        keywords = []
        seen = set()
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum() or c == '-')
            
            # Filter criteria
            if (clean_word and 
                len(clean_word) > 3 and 
                clean_word not in stop_words and
                clean_word not in seen):
                keywords.append(clean_word)
                seen.add(clean_word)
        
        return keywords
    
    def analyze_trends(self, trends: List[Dict]) -> Dict:
        """Analyze aggregated trends for insights"""
        
        # Count by source
        sources = {}
        for trend in trends:
            source = trend["source"]
            sources[source] = sources.get(source, 0) + 1
        
        # Count programming languages (from GitHub)
        languages = {}
        for trend in trends:
            lang = trend.get("language")
            if lang and lang != "Unknown":
                languages[lang] = languages.get(lang, 0) + 1
        
        # Top keywords overall
        all_keywords = {}
        for trend in trends:
            for kw in trend.get("cross_source_keywords", []):
                all_keywords[kw] = all_keywords.get(kw, 0) + 1
        
        top_keywords = sorted(
            all_keywords.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]
        
        return {
            "total_trends": len(trends),
            "by_source": sources,
            "top_languages": dict(sorted(
                languages.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]),
            "top_keywords": dict(top_keywords),
            "cross_source_trends": len([
                t for t in trends 
                if t.get("cross_source_keywords")
            ])
        }


async def main():
    """Main execution - demonstrate multi-source trend aggregation"""
    
    print("=" * 70)
    print("🎯 Multi-Source Trend Aggregator - @coach-master POC")
    print("   Mission: AI/ML Innovation (idea:27)")
    print("=" * 70)
    
    aggregator = TrendAggregator()
    
    # Step 1: Aggregate from all sources
    all_trends = await aggregator.aggregate()
    
    if not all_trends:
        print("\n❌ No trends fetched. Check API connectivity.")
        return
    
    # Step 2: Correlate across sources
    correlated = aggregator.correlate(all_trends)
    
    # Step 3: Analyze
    analysis = aggregator.analyze_trends(correlated)
    
    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 70)
    
    print(f"\n📈 Total Trends: {analysis['total_trends']}")
    print("\n📦 By Source:")
    for source, count in analysis['by_source'].items():
        print(f"   - {source}: {count}")
    
    print(f"\n🔗 Cross-Source Trends: {analysis['cross_source_trends']}")
    
    if analysis['top_languages']:
        print("\n💻 Top Programming Languages:")
        for lang, count in list(analysis['top_languages'].items())[:5]:
            print(f"   - {lang}: {count}")
    
    if analysis['top_keywords']:
        print("\n🔑 Top Cross-Source Keywords:")
        for kw, count in list(analysis['top_keywords'].items())[:10]:
            print(f"   - {kw}: {count} sources")
    
    # Step 4: Display top trends
    print("\n" + "=" * 70)
    print("🏆 TOP 15 CROSS-SOURCE TRENDS")
    print("=" * 70)
    
    for i, trend in enumerate(correlated[:15], 1):
        print(f"\n{i}. {trend['title']}")
        print(f"   📍 Source: {trend['source']}")
        print(f"   ⭐ Relevance Score: {trend.get('relevance_score', 0):.1f}")
        
        if trend.get('cross_source_keywords'):
            keywords = ', '.join(trend['cross_source_keywords'][:5])
            print(f"   🔑 Keywords: {keywords}")
        
        if trend.get('stars'):
            print(f"   ⭐ Stars: {trend['stars']}")
        elif trend.get('score'):
            print(f"   👍 Score: {trend['score']}")
        
        print(f"   🔗 {trend['url']}")
    
    # Step 5: Save results
    output_file = "learnings/multi_source_trends.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    output_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "analysis": analysis,
        "trends": correlated[:50]  # Top 50 trends
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"💾 Results saved to: {output_file}")
    print("=" * 70)
    
    print("\n✅ Multi-source trend aggregation complete!")
    print("\n💡 Next steps:")
    print("   1. Review correlated trends in output file")
    print("   2. Identify relevant technologies for Chained")
    print("   3. Create agent missions for high-relevance trends")
    print("   4. Update world model with geographic data")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
