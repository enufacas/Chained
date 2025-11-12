#!/usr/bin/env python3
"""
Web Content Fetcher

Fetches and extracts readable content from URLs for the learnings system.
Handles common issues like paywalls, JavaScript, and formatting.
"""

import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import json


class WebContentFetcher:
    """Fetches and extracts readable content from web pages"""
    
    def __init__(self, timeout=10, user_agent=None):
        self.timeout = timeout
        self.user_agent = user_agent or (
            'Mozilla/5.0 (compatible; ChainedAI/1.0; +https://github.com/enufacas/Chained)'
        )
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def fetch(self, url, max_retries=3):
        """
        Fetch content from a URL with retry logic
        
        Args:
            url: The URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict with 'success', 'content', 'title', 'error' keys
        """
        result = {
            'success': False,
            'url': url,
            'content': None,
            'title': None,
            'error': None
        }
        
        # Skip certain domains that are problematic
        skip_domains = ['twitter.com', 'x.com', 'facebook.com', 'instagram.com']
        domain = urlparse(url).netloc.lower()
        if any(skip in domain for skip in skip_domains):
            result['error'] = 'Social media domain skipped'
            return result
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                
                if response.status_code == 200:
                    result['success'] = True
                    result['content'] = self._extract_content(response.text, url)
                    result['title'] = self._extract_title(response.text)
                    return result
                elif response.status_code == 403:
                    result['error'] = 'Access forbidden (403)'
                    return result
                elif response.status_code == 404:
                    result['error'] = 'Not found (404)'
                    return result
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    time.sleep(2 ** attempt)
                    continue
                else:
                    result['error'] = f'HTTP {response.status_code}'
                    return result
                    
            except requests.Timeout:
                result['error'] = 'Request timeout'
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            except requests.RequestException as e:
                result['error'] = f'Request error: {str(e)}'
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            except Exception as e:
                result['error'] = f'Unexpected error: {str(e)}'
                return result
        
        return result
    
    def _extract_title(self, html):
        """Extract the page title"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try different title sources
            title = None
            
            # Try og:title meta tag
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title['content']
            
            # Try regular title tag
            if not title and soup.title:
                title = soup.title.string
            
            # Try h1
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text()
            
            return title.strip() if title else None
            
        except Exception:
            return None
    
    def _extract_content(self, html, url):
        """Extract readable content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script, style, nav, footer, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 
                                'noscript', 'header', 'aside', 'form']):
                element.decompose()
            
            # Try to find main content area
            content_candidates = []
            
            # Look for article tag
            article = soup.find('article')
            if article:
                content_candidates.append(article)
            
            # Look for main tag
            main = soup.find('main')
            if main:
                content_candidates.append(main)
            
            # Look for common content class/id patterns
            for pattern in ['content', 'article', 'post', 'entry', 'story']:
                for tag in ['div', 'section']:
                    elements = soup.find_all(tag, class_=lambda c: c and pattern in c.lower())
                    content_candidates.extend(elements)
                    
                    elements = soup.find_all(tag, id=lambda i: i and pattern in i.lower())
                    content_candidates.extend(elements)
            
            # If we found candidates, use the one with most text
            if content_candidates:
                content = max(content_candidates, key=lambda x: len(x.get_text()))
            else:
                # Fall back to body
                content = soup.find('body') or soup
            
            # Extract text
            text = content.get_text(separator='\n', strip=True)
            
            # Clean up the text
            lines = [line.strip() for line in text.split('\n')]
            lines = [line for line in lines if line]  # Remove empty lines
            
            # Remove duplicate consecutive lines
            cleaned_lines = []
            prev_line = None
            for line in lines:
                if line != prev_line:
                    cleaned_lines.append(line)
                prev_line = line
            
            text = '\n'.join(cleaned_lines)
            
            # Truncate if too long (keep first ~5000 chars for summary)
            if len(text) > 5000:
                text = text[:5000] + '\n\n[Content truncated for brevity...]'
            
            return text
            
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    def fetch_batch(self, urls, delay=1.0):
        """
        Fetch multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to fetch
            delay: Delay between requests in seconds
            
        Returns:
            List of results
        """
        results = []
        
        for i, url in enumerate(urls):
            if i > 0:
                time.sleep(delay)
            
            result = self.fetch(url)
            results.append(result)
            
            status = '✓' if result['success'] else '✗'
            print(f"{status} {url}")
            if result['error']:
                print(f"  Error: {result['error']}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and extract readable content from web URLs'
    )
    parser.add_argument('urls', nargs='+', help='URLs to fetch')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
    
    args = parser.parse_args()
    
    fetcher = WebContentFetcher(timeout=args.timeout)
    
    if len(args.urls) == 1:
        result = fetcher.fetch(args.urls[0])
        
        if result['success']:
            print(f"\nTitle: {result['title']}")
            print(f"\nContent:\n{result['content']}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\nSaved to {args.output}")
        else:
            print(f"Failed to fetch: {result['error']}", file=sys.stderr)
            sys.exit(1)
    else:
        results = fetcher.fetch_batch(args.urls, delay=args.delay)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nSaved {len(results)} results to {args.output}")
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\nSuccess: {success_count}/{len(results)}")


if __name__ == '__main__':
    main()
