#!/usr/bin/env python3
"""
Learnings Book Builder

Reads learning JSON files and organizes them into a structured book with chapters.
Creates beautiful markdown files for easy reading and GitHub Pages integration.
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class LearningsBookBuilder:
    """Builds a structured learnings book from JSON files"""
    
    CHAPTERS = {
        'AI_ML': {
            'title': '🤖 AI & Machine Learning',
            'description': 'Artificial intelligence, machine learning, LLMs, and neural networks',
            'keywords': ['ai', 'ml', 'machine learning', 'neural', 'gpt', 'llm', 'copilot', 
                        'openai', 'anthropic', 'model', 'training', 'transformer']
        },
        'Programming': {
            'title': '💻 Programming Languages & Frameworks',
            'description': 'Programming languages, frameworks, libraries, and development tools',
            'keywords': ['python', 'rust', 'go', 'javascript', 'typescript', 'java', 'c++',
                        'framework', 'library', 'language', 'code', 'compiler', 'syntax']
        },
        'DevOps': {
            'title': '🚀 DevOps & Infrastructure',
            'description': 'CI/CD, containers, orchestration, and infrastructure automation',
            'keywords': ['devops', 'docker', 'kubernetes', 'k8s', 'ci/cd', 'github actions',
                        'terraform', 'ansible', 'deployment', 'infrastructure', 'cloud']
        },
        'Database': {
            'title': '🗄️ Databases & Data Management',
            'description': 'SQL, NoSQL, data storage, and data engineering',
            'keywords': ['database', 'sql', 'postgres', 'mysql', 'mongodb', 'redis',
                        'data', 'query', 'nosql', 'storage']
        },
        'Web': {
            'title': '🌐 Web Development',
            'description': 'Web technologies, browsers, APIs, and frontend frameworks',
            'keywords': ['web', 'browser', 'http', 'api', 'rest', 'graphql', 'react',
                        'vue', 'angular', 'frontend', 'backend', 'fullstack']
        },
        'Security': {
            'title': '🔒 Security & Privacy',
            'description': 'Security vulnerabilities, encryption, authentication, and privacy',
            'keywords': ['security', 'vulnerability', 'encryption', 'auth', 'authentication',
                        'cve', 'exploit', 'privacy', 'breach', 'hack']
        },
        'Performance': {
            'title': '⚡ Performance & Optimization',
            'description': 'Performance tuning, benchmarks, and optimization techniques',
            'keywords': ['performance', 'optimization', 'speed', 'benchmark', 'fast',
                        'latency', 'throughput', 'efficient', 'optimize']
        },
        'Tools': {
            'title': '🔧 Developer Tools',
            'description': 'IDEs, editors, debuggers, and productivity tools',
            'keywords': ['tool', 'ide', 'editor', 'vscode', 'vim', 'debugger', 'git',
                        'productivity', 'workflow']
        },
        'OpenSource': {
            'title': '🌟 Open Source & Community',
            'description': 'Open source projects, community insights, and collaboration',
            'keywords': ['open source', 'oss', 'github', 'community', 'contribution',
                        'collaborative', 'license', 'maintainer']
        },
        'Other': {
            'title': '📚 General Tech Insights',
            'description': 'General technology news and insights',
            'keywords': []
        }
    }
    
    def __init__(self, learnings_dir='learnings', book_dir='learnings/book'):
        self.learnings_dir = Path(learnings_dir)
        self.book_dir = Path(book_dir)
        self.book_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for categorized learnings
        self.chapters_content = defaultdict(list)
        self.stats = {
            'total_learnings': 0,
            'total_articles': 0,
            'by_source': defaultdict(int),
            'by_chapter': defaultdict(int)
        }
    
    def categorize_learning(self, learning):
        """Determine which chapter a learning belongs to"""
        text = (learning.get('title', '') + ' ' + learning.get('description', '')).lower()
        
        # Check each chapter's keywords
        for chapter_id, chapter_info in self.CHAPTERS.items():
            if chapter_id == 'Other':
                continue
            
            for keyword in chapter_info['keywords']:
                if keyword in text:
                    return chapter_id
        
        return 'Other'
    
    def load_learnings(self):
        """Load all learning JSON files"""
        json_files = list(self.learnings_dir.glob('*.json'))
        json_files = [f for f in json_files if f.name not in ['index.json']]
        
        print(f"Found {len(json_files)} learning files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                source = data.get('source', 'Unknown')
                timestamp = data.get('timestamp', '')
                learnings = data.get('learnings', [])
                
                self.stats['total_learnings'] += 1
                self.stats['by_source'][source] += 1
                self.stats['total_articles'] += len(learnings)
                
                # Categorize each learning
                for learning in learnings:
                    chapter = self.categorize_learning(learning)
                    
                    enriched_learning = {
                        **learning,
                        'source': source,
                        'timestamp': timestamp,
                        'file': json_file.name
                    }
                    
                    self.chapters_content[chapter].append(enriched_learning)
                    self.stats['by_chapter'][chapter] += 1
                    
            except Exception as e:
                print(f"Error loading {json_file}: {e}", file=sys.stderr)
        
        print(f"Loaded {self.stats['total_articles']} articles from {self.stats['total_learnings']} learning sessions")
    
    def build_chapter(self, chapter_id):
        """Build a chapter markdown file"""
        if chapter_id not in self.CHAPTERS:
            return
        
        chapter_info = self.CHAPTERS[chapter_id]
        learnings = self.chapters_content.get(chapter_id, [])
        
        if not learnings:
            return
        
        # Sort by timestamp (newest first)
        learnings.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Build markdown content
        md_lines = [
            f"# {chapter_info['title']}\n",
            f"> {chapter_info['description']}\n",
            f"**Total Insights:** {len(learnings)}\n",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}\n",
            "---\n"
        ]
        
        # Group by source
        by_source = defaultdict(list)
        for learning in learnings:
            by_source[learning.get('source', 'Unknown')].append(learning)
        
        # Add learnings
        for source in sorted(by_source.keys()):
            source_learnings = by_source[source]
            md_lines.append(f"\n## 📰 From {source}\n")
            
            for learning in source_learnings[:20]:  # Limit to 20 per source
                title = learning.get('title', 'Untitled')
                url = learning.get('url', '')
                content = learning.get('content', '')
                description = learning.get('description', '')
                score = learning.get('score', 0)
                
                md_lines.append(f"\n### {title}\n")
                
                if score:
                    md_lines.append(f"**Community Score:** {score} upvotes\n")
                
                if url:
                    md_lines.append(f"**Link:** {url}\n")
                
                if content:
                    # Add content summary
                    md_lines.append(f"\n**Content Summary:**\n")
                    # Truncate content if too long
                    if len(content) > 500:
                        content = content[:500] + '...'
                    md_lines.append(f"{content}\n")
                elif description:
                    md_lines.append(f"\n{description}\n")
                
                md_lines.append("---\n")
        
        # Write chapter file
        chapter_file = self.book_dir / f"{chapter_id}.md"
        with open(chapter_file, 'w') as f:
            f.write('\n'.join(md_lines))
        
        print(f"✓ Built chapter: {chapter_info['title']} ({len(learnings)} insights)")
    
    def build_index(self):
        """Build the master index/README"""
        md_lines = [
            "# 📖 The Learnings Book\n",
            "> A curated collection of insights from TLDR Tech, Hacker News, and other sources\n",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n",
            f"**Total Learning Sessions:** {self.stats['total_learnings']}\n",
            f"**Total Insights:** {self.stats['total_articles']}\n",
            "---\n",
            "\n## 📚 Chapters\n"
        ]
        
        # Add chapter links
        for chapter_id, chapter_info in self.CHAPTERS.items():
            count = self.stats['by_chapter'].get(chapter_id, 0)
            if count > 0:
                title = chapter_info['title']
                description = chapter_info['description']
                md_lines.append(f"\n### [{title}](./{chapter_id}.md)\n")
                md_lines.append(f"{description}\n")
                md_lines.append(f"**Insights:** {count}\n")
        
        # Add statistics
        md_lines.extend([
            "\n## 📊 Statistics\n",
            "\n### By Source\n"
        ])
        
        for source, count in sorted(self.stats['by_source'].items(), key=lambda x: x[1], reverse=True):
            md_lines.append(f"- **{source}:** {count} learning sessions\n")
        
        md_lines.extend([
            "\n### By Topic\n"
        ])
        
        for chapter_id, count in sorted(self.stats['by_chapter'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                title = self.CHAPTERS[chapter_id]['title']
                md_lines.append(f"- **{title}:** {count} insights\n")
        
        # Add usage guide
        md_lines.extend([
            "\n## 💡 How to Use This Book\n",
            "\n1. **Browse by Topic:** Click on any chapter to explore insights in that area\n",
            "2. **Stay Current:** This book is automatically updated with new learnings\n",
            "3. **Deep Dive:** Click through to original sources for full articles\n",
            "4. **Get Inspired:** Use these insights to generate new project ideas\n",
            "\n## 🔄 Update Frequency\n",
            "\n- **TLDR Tech:** Updated twice daily (8 AM, 8 PM UTC)\n",
            "- **Hacker News:** Updated three times daily (7 AM, 1 PM, 7 PM UTC)\n",
            "- **Book Rebuild:** Automatic on new learnings\n",
            "\n## 🤖 About\n",
            "\nThis learnings book is automatically curated by the Chained AI system. It continuously learns from:\n",
            "\n- 📰 **TLDR Tech newsletters** - Curated tech news and trends\n",
            "- 🔥 **Hacker News** - Community-driven tech discussions\n",
            "- 🌐 **Article content** - Full text extraction and summarization\n",
            "\nThe insights collected here influence idea generation, implementation decisions, and technology choices across the autonomous system.\n",
            "\n---\n",
            "\n*📖 Keep learning, keep growing. The future is built on knowledge shared.*\n"
        ])
        
        # Write index
        index_file = self.book_dir / "README.md"
        with open(index_file, 'w') as f:
            f.write('\n'.join(md_lines))
        
        print(f"✓ Built index with {len(self.CHAPTERS)} chapters")
    
    def build(self):
        """Build the complete learnings book"""
        print("Building learnings book...")
        
        # Load all learnings
        self.load_learnings()
        
        # Build each chapter
        for chapter_id in self.CHAPTERS:
            self.build_chapter(chapter_id)
        
        # Build index
        self.build_index()
        
        print(f"\n✅ Learnings book built successfully!")
        print(f"   Location: {self.book_dir}")
        print(f"   Chapters: {sum(1 for c in self.stats['by_chapter'].values() if c > 0)}")
        print(f"   Total Insights: {self.stats['total_articles']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build the learnings book from JSON files'
    )
    parser.add_argument(
        '--learnings-dir',
        default='learnings',
        help='Directory containing learning JSON files'
    )
    parser.add_argument(
        '--book-dir',
        default='learnings/book',
        help='Output directory for the book'
    )
    
    args = parser.parse_args()
    
    builder = LearningsBookBuilder(args.learnings_dir, args.book_dir)
    builder.build()


if __name__ == '__main__':
    main()
