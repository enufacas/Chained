#!/usr/bin/env python3
"""
GitHub Trending Repos Fetcher

Fetches trending repositories from GitHub for the learning system.
Extracts repository information including name, description, stars, language, and trends.
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import re


class GitHubTrendingFetcher:
    """Fetches trending repositories from GitHub"""
    
    BASE_URL = "https://github.com/trending"
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ChainedAI/1.0; +https://github.com/enufacas/Chained)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def fetch_trending(self, language=None, since='daily', max_repos=25):
        """
        Fetch trending repositories from GitHub
        
        Args:
            language: Programming language filter (e.g., 'python', 'javascript', None for all)
            since: Time range - 'daily', 'weekly', or 'monthly'
            max_repos: Maximum number of repositories to fetch (default 25)
        
        Returns:
            List of repository dictionaries
        """
        # Build URL
        url = self.BASE_URL
        if language:
            url = f"{url}/{language}"
        
        params = {'since': since}
        
        print(f"Fetching trending repos from: {url} (since={since})", file=sys.stderr)
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            
            # Find all repository articles
            articles = soup.find_all('article', class_='Box-row')
            
            for article in articles[:max_repos]:
                try:
                    repo_info = self._parse_repo_article(article)
                    if repo_info:
                        repos.append(repo_info)
                except Exception as e:
                    print(f"Warning: Failed to parse repository: {e}", file=sys.stderr)
                    continue
            
            print(f"✓ Fetched {len(repos)} trending repositories", file=sys.stderr)
            return repos
            
        except requests.RequestException as e:
            print(f"✗ Error fetching trending repos: {e}", file=sys.stderr)
            return []
    
    def _parse_repo_article(self, article):
        """Parse a single repository article element"""
        repo_info = {}
        
        # Get repo name and URL
        h2 = article.find('h2', class_='h3')
        if not h2:
            return None
        
        link = h2.find('a')
        if not link:
            return None
        
        href = link.get('href', '')
        if href:
            repo_info['url'] = f"https://github.com{href}"
            # Extract owner/repo from href
            parts = href.strip('/').split('/')
            if len(parts) >= 2:
                repo_info['owner'] = parts[0]
                repo_info['name'] = parts[1]
                repo_info['full_name'] = f"{parts[0]}/{parts[1]}"
        
        # Get description
        desc_elem = article.find('p', class_='col-9')
        if desc_elem:
            repo_info['description'] = desc_elem.get_text(strip=True)
        else:
            repo_info['description'] = ''
        
        # Get language
        lang_elem = article.find('span', itemprop='programmingLanguage')
        if lang_elem:
            repo_info['language'] = lang_elem.get_text(strip=True)
        else:
            repo_info['language'] = 'Unknown'
        
        # Get stars count
        stars_elem = article.find('svg', class_='octicon-star')
        if stars_elem and stars_elem.parent:
            stars_text = stars_elem.parent.get_text(strip=True)
            repo_info['stars'] = self._parse_count(stars_text)
            repo_info['stars_text'] = stars_text
        else:
            repo_info['stars'] = 0
            repo_info['stars_text'] = '0'
        
        # Get forks count
        forks_elem = article.find('svg', class_='octicon-repo-forked')
        if forks_elem and forks_elem.parent:
            forks_text = forks_elem.parent.get_text(strip=True)
            repo_info['forks'] = self._parse_count(forks_text)
            repo_info['forks_text'] = forks_text
        else:
            repo_info['forks'] = 0
            repo_info['forks_text'] = '0'
        
        # Get stars today/this week/this month
        stars_today_elem = article.find('span', class_='d-inline-block float-sm-right')
        if stars_today_elem:
            stars_today_text = stars_today_elem.get_text(strip=True)
            repo_info['stars_period'] = stars_today_text
            # Try to extract number
            match = re.search(r'([\d,]+)', stars_today_text)
            if match:
                repo_info['stars_period_count'] = self._parse_count(match.group(1))
        
        # Get built by (contributors)
        built_by = []
        built_by_elem = article.find('span', string=re.compile(r'Built by'))
        if built_by_elem:
            imgs = built_by_elem.parent.find_all('img')
            for img in imgs:
                alt = img.get('alt', '')
                if alt.startswith('@'):
                    built_by.append(alt[1:])
        
        if built_by:
            repo_info['built_by'] = built_by
        
        return repo_info
    
    def _parse_count(self, text):
        """Parse a count string like '1,234' or '1.2k' to integer"""
        # Remove whitespace
        text = text.strip().replace(',', '')
        
        # Handle k suffix (thousands)
        if 'k' in text.lower():
            text = text.lower().replace('k', '')
            try:
                return int(float(text) * 1000)
            except ValueError:
                return 0
        
        # Try to parse as integer
        try:
            return int(text)
        except ValueError:
            return 0
    
    def fetch_multiple_languages(self, languages, since='daily', max_per_lang=10):
        """
        Fetch trending repos for multiple languages
        
        Args:
            languages: List of language names (e.g., ['python', 'javascript', 'rust'])
            since: Time range
            max_per_lang: Max repos per language
        
        Returns:
            Dictionary mapping language to list of repos
        """
        results = {}
        
        for lang in languages:
            print(f"Fetching trending {lang} repos...", file=sys.stderr)
            repos = self.fetch_trending(language=lang, since=since, max_repos=max_per_lang)
            results[lang] = repos
            time.sleep(1)  # Rate limiting
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch trending GitHub repositories')
    parser.add_argument('--language', '-l', help='Programming language filter')
    parser.add_argument('--since', '-s', default='daily', 
                       choices=['daily', 'weekly', 'monthly'],
                       help='Time range (default: daily)')
    parser.add_argument('--max-repos', '-n', type=int, default=25,
                       help='Maximum number of repos to fetch (default: 25)')
    parser.add_argument('--languages', nargs='+',
                       help='Fetch for multiple languages')
    parser.add_argument('--output', '-o', help='Output JSON file')
    
    args = parser.parse_args()
    
    fetcher = GitHubTrendingFetcher()
    
    # Fetch repos
    if args.languages:
        # Multiple languages
        all_repos = fetcher.fetch_multiple_languages(
            args.languages, 
            since=args.since,
            max_per_lang=args.max_repos
        )
        
        # Flatten to single list with language tag
        repos = []
        for lang, lang_repos in all_repos.items():
            for repo in lang_repos:
                repo['trending_language_filter'] = lang
                repos.append(repo)
    else:
        # Single language or all
        repos = fetcher.fetch_trending(
            language=args.language,
            since=args.since,
            max_repos=args.max_repos
        )
    
    # Prepare output
    output_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'GitHub Trending',
        'since': args.since,
        'language_filter': args.language or args.languages or 'all',
        'repository_count': len(repos),
        'repositories': repos
    }
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"✓ Saved {len(repos)} repositories to {args.output}", file=sys.stderr)
    else:
        # Print to stdout
        print(json.dumps(output_data, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
