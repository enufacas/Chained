#!/usr/bin/env python3
"""
GitHub Copilot Learning Fetcher

Fetches content from multiple GitHub Copilot sources for the learning system:
1. GitHub Docs (https://docs.github.com/en/copilot) - Official documentation
2. Reddit r/GithubCopilot - Community discussions
3. GitHub Discussions - Community forum posts

Extracts relevant content about GitHub Copilot features, best practices, and use cases.
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import re
from urllib.parse import urljoin, urlparse


class GitHubCopilotFetcher:
    """Fetches GitHub Copilot learning content from multiple sources"""
    
    GITHUB_DOCS_BASE = "https://docs.github.com/en/copilot"
    REDDIT_BASE = "https://www.reddit.com/r/GithubCopilot"
    GITHUB_DISCUSSIONS_API = "https://api.github.com/search/issues"
    
    def __init__(self, timeout=15, github_token=None):
        self.timeout = timeout
        self.github_token = github_token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ChainedAI/1.0; +https://github.com/enufacas/Chained)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Add GitHub token for API requests if provided
        if self.github_token:
            self.api_headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'ChainedAI/1.0'
            }
        else:
            self.api_headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'ChainedAI/1.0'
            }
    
    def fetch_github_docs(self, max_topics=10):
        """
        Fetch content from GitHub Copilot documentation
        
        Args:
            max_topics: Maximum number of documentation topics to fetch
        
        Returns:
            List of learning dictionaries
        """
        learnings = []
        
        print(f"Fetching GitHub Copilot documentation from: {self.GITHUB_DOCS_BASE}", file=sys.stderr)
        
        try:
            # Fetch the main Copilot docs page
            response = self.session.get(self.GITHUB_DOCS_BASE, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find documentation links
            # GitHub docs structure: look for article links in navigation or main content
            doc_links = []
            
            # Try to find links in the main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                links = main_content.find_all('a', href=re.compile(r'/en/copilot/'))
                for link in links[:max_topics * 2]:  # Get extra links to filter
                    href = link.get('href', '')
                    if href and href not in doc_links:
                        full_url = urljoin(self.GITHUB_DOCS_BASE, href)
                        # Skip anchor links, just get unique pages
                        if '#' not in href:
                            doc_links.append(full_url)
            
            # Limit to max_topics
            doc_links = doc_links[:max_topics]
            
            print(f"  Found {len(doc_links)} documentation links", file=sys.stderr)
            
            # Fetch content from each documentation page
            for url in doc_links:
                try:
                    print(f"  Fetching: {url}", file=sys.stderr)
                    time.sleep(0.5)  # Rate limiting
                    
                    page_response = self.session.get(url, timeout=self.timeout)
                    page_response.raise_for_status()
                    
                    page_soup = BeautifulSoup(page_response.text, 'html.parser')
                    
                    # Extract title
                    title_elem = page_soup.find('h1') or page_soup.find('title')
                    title = title_elem.get_text(strip=True) if title_elem else url.split('/')[-1]
                    
                    # Clean title
                    title = title.replace(' - GitHub Docs', '').strip()
                    
                    # Extract main content
                    article = page_soup.find('article') or page_soup.find('main')
                    if article:
                        # Remove navigation, footers, scripts
                        for elem in article.find_all(['nav', 'footer', 'script', 'style']):
                            elem.decompose()
                        
                        # Get text content
                        content = article.get_text(separator='\n', strip=True)
                        
                        # Clean up excessive whitespace
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        content = '\n'.join(lines)
                        
                        # Truncate if too long
                        if len(content) > 2000:
                            content = content[:2000] + '\n\n[Content truncated...]'
                        
                        learning = {
                            'title': f"GitHub Copilot Docs: {title}",
                            'description': content[:500],  # First 500 chars as description
                            'content': content,
                            'url': url,
                            'source': 'GitHub Copilot Docs',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                        
                        learnings.append(learning)
                        print(f"    ✓ Fetched: {title[:60]}...", file=sys.stderr)
                
                except Exception as e:
                    print(f"    ✗ Error fetching {url}: {e}", file=sys.stderr)
                    continue
            
            print(f"✓ Fetched {len(learnings)} documentation topics", file=sys.stderr)
            return learnings
            
        except requests.RequestException as e:
            print(f"✗ Error fetching GitHub Docs: {e}", file=sys.stderr)
            return []
    
    def fetch_reddit(self, max_posts=10):
        """
        Fetch posts from r/GithubCopilot subreddit
        
        Args:
            max_posts: Maximum number of posts to fetch
        
        Returns:
            List of learning dictionaries
        """
        learnings = []
        
        print(f"Fetching Reddit posts from: {self.REDDIT_BASE}", file=sys.stderr)
        
        try:
            # Fetch hot posts from the subreddit (JSON API)
            url = f"{self.REDDIT_BASE}/hot.json"
            params = {'limit': max_posts}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                posts = data['data']['children']
                
                for post in posts[:max_posts]:
                    try:
                        post_data = post.get('data', {})
                        
                        title = post_data.get('title', 'Untitled')
                        selftext = post_data.get('selftext', '')
                        url = post_data.get('url', '')
                        permalink = f"https://www.reddit.com{post_data.get('permalink', '')}"
                        score = post_data.get('score', 0)
                        num_comments = post_data.get('num_comments', 0)
                        
                        # Skip if no content
                        if not selftext and not url:
                            continue
                        
                        # Build description
                        description = selftext[:500] if selftext else f"Link post: {url}"
                        
                        learning = {
                            'title': f"Reddit: {title}",
                            'description': description,
                            'content': selftext or f"External link: {url}",
                            'url': permalink,
                            'external_url': url if url != permalink else None,
                            'source': 'Reddit r/GithubCopilot',
                            'metadata': {
                                'score': score,
                                'comments': num_comments
                            },
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                        
                        learnings.append(learning)
                        print(f"  ✓ {title[:60]}... (score: {score})", file=sys.stderr)
                    
                    except Exception as e:
                        print(f"  ✗ Error parsing post: {e}", file=sys.stderr)
                        continue
                
                print(f"✓ Fetched {len(learnings)} Reddit posts", file=sys.stderr)
            
            return learnings
            
        except requests.RequestException as e:
            print(f"✗ Error fetching Reddit: {e}", file=sys.stderr)
            return []
    
    def fetch_github_discussions(self, max_discussions=10):
        """
        Fetch GitHub Community Discussions filtered by 'copilot'
        
        Args:
            max_discussions: Maximum number of discussions to fetch
        
        Returns:
            List of learning dictionaries
        """
        learnings = []
        
        print("Fetching GitHub Discussions about Copilot", file=sys.stderr)
        
        try:
            # Use GitHub Search API to find discussions
            # Search in community discussions about copilot
            query = "copilot in:title is:open"
            
            params = {
                'q': query,
                'sort': 'interactions',  # Most active discussions
                'order': 'desc',
                'per_page': max_discussions
            }
            
            response = requests.get(
                self.GITHUB_DISCUSSIONS_API,
                params=params,
                headers=self.api_headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' in data:
                discussions = data['items']
                
                for disc in discussions[:max_discussions]:
                    try:
                        title = disc.get('title', 'Untitled')
                        body = disc.get('body', '')
                        url = disc.get('html_url', '')
                        comments = disc.get('comments', 0)
                        
                        # Truncate body for description
                        description = body[:500] if body else 'No description'
                        
                        learning = {
                            'title': f"GitHub Discussion: {title}",
                            'description': description,
                            'content': body[:2000] if body else '',
                            'url': url,
                            'source': 'GitHub Community Discussions',
                            'metadata': {
                                'comments': comments
                            },
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                        
                        learnings.append(learning)
                        print(f"  ✓ {title[:60]}... ({comments} comments)", file=sys.stderr)
                    
                    except Exception as e:
                        print(f"  ✗ Error parsing discussion: {e}", file=sys.stderr)
                        continue
                
                print(f"✓ Fetched {len(learnings)} GitHub discussions", file=sys.stderr)
            
            return learnings
            
        except requests.RequestException as e:
            print(f"✗ Error fetching GitHub Discussions: {e}", file=sys.stderr)
            return []
    
    def fetch_all(self, docs_count=5, reddit_count=5, discussions_count=5):
        """
        Fetch from all sources
        
        Args:
            docs_count: Number of documentation topics
            reddit_count: Number of Reddit posts
            discussions_count: Number of GitHub discussions
        
        Returns:
            Dictionary with all learnings and metadata
        """
        print("=" * 70, file=sys.stderr)
        print("GitHub Copilot Learning Fetcher", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(file=sys.stderr)
        
        all_learnings = []
        source_counts = {}
        
        # Fetch from GitHub Docs
        docs_learnings = self.fetch_github_docs(max_topics=docs_count)
        all_learnings.extend(docs_learnings)
        source_counts['GitHub Copilot Docs'] = len(docs_learnings)
        print(file=sys.stderr)
        
        # Fetch from Reddit
        reddit_learnings = self.fetch_reddit(max_posts=reddit_count)
        all_learnings.extend(reddit_learnings)
        source_counts['Reddit r/GithubCopilot'] = len(reddit_learnings)
        print(file=sys.stderr)
        
        # Fetch from GitHub Discussions
        discussions_learnings = self.fetch_github_discussions(max_discussions=discussions_count)
        all_learnings.extend(discussions_learnings)
        source_counts['GitHub Community Discussions'] = len(discussions_learnings)
        print(file=sys.stderr)
        
        # Build result
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'GitHub Copilot (Combined)',
            'learnings': all_learnings,
            'source_counts': source_counts,
            'total_learnings': len(all_learnings)
        }
        
        print("=" * 70, file=sys.stderr)
        print(f"Total learnings collected: {len(all_learnings)}", file=sys.stderr)
        for source, count in source_counts.items():
            print(f"  {source}: {count}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        
        return result


def main():
    """Main entry point for CLI usage"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Fetch GitHub Copilot learning content')
    parser.add_argument('--docs', type=int, default=5, help='Number of documentation topics')
    parser.add_argument('--reddit', type=int, default=5, help='Number of Reddit posts')
    parser.add_argument('--discussions', type=int, default=5, help='Number of GitHub discussions')
    parser.add_argument('--output', type=str, help='Output JSON file path')
    parser.add_argument('--github-token', type=str, help='GitHub API token (or use GITHUB_TOKEN env)')
    
    args = parser.parse_args()
    
    # Get GitHub token from args or environment
    github_token = args.github_token or os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    
    # Create fetcher and fetch content
    fetcher = GitHubCopilotFetcher(github_token=github_token)
    result = fetcher.fetch_all(
        docs_count=args.docs,
        reddit_count=args.reddit,
        discussions_count=args.discussions
    )
    
    # Output result as JSON
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Saved to: {args.output}", file=sys.stderr)
    else:
        # Print to stdout
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
