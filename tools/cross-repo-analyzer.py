#!/usr/bin/env python3
"""
Cross-Repository Analyzer

Extends the pattern matcher to analyze multiple repositories across GitHub.
Uses GitHub API to fetch and analyze code from multiple repos.
"""

import argparse
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import urllib.request
import urllib.error


class GitHubRepoAnalyzer:
    """Analyze multiple GitHub repositories for best practices"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.temp_dir = None
        
    def _make_api_request(self, url: str) -> Dict:
        """Make authenticated GitHub API request"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Chained-Pattern-Matcher/1.0'
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"Rate limit exceeded or authentication required", file=sys.stderr)
            else:
                print(f"API request failed: {e}", file=sys.stderr)
            return {}
        except Exception as e:
            print(f"Error making API request: {e}", file=sys.stderr)
            return {}
    
    def search_repositories(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for repositories on GitHub"""
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded_query}&per_page={max_results}&sort=stars"
        
        data = self._make_api_request(url)
        return data.get('items', [])
    
    def clone_or_download_repo(self, owner: str, repo: str, output_dir: str) -> Optional[str]:
        """Clone or download a repository"""
        repo_path = os.path.join(output_dir, f"{owner}_{repo}")
        
        # Try to use git if available
        git_available = shutil.which('git') is not None
        
        if git_available:
            try:
                import subprocess
                clone_url = f"https://github.com/{owner}/{repo}.git"
                subprocess.run(['git', 'clone', '--depth', '1', clone_url, repo_path],
                             check=True, capture_output=True)
                return repo_path
            except Exception as e:
                print(f"Git clone failed, falling back to download: {e}", file=sys.stderr)
        
        # Fallback: Download as zip using GitHub API
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
            print(f"Downloading {owner}/{repo}...")
            
            headers = {'User-Agent': 'Chained-Pattern-Matcher/1.0'}
            if self.token:
                headers['Authorization'] = f'token {self.token}'
            
            req = urllib.request.Request(url, headers=headers)
            
            zip_path = f"{repo_path}.zip"
            with urllib.request.urlopen(req) as response:
                with open(zip_path, 'wb') as f:
                    f.write(response.read())
            
            # Extract zip
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            
            os.remove(zip_path)
            
            # Find extracted directory (GitHub adds a hash to the name)
            extracted_dirs = [d for d in os.listdir(output_dir) 
                            if d.startswith(f"{owner}-{repo}")]
            if extracted_dirs:
                extracted_path = os.path.join(output_dir, extracted_dirs[0])
                os.rename(extracted_path, repo_path)
                return repo_path
            
        except Exception as e:
            print(f"Failed to download {owner}/{repo}: {e}", file=sys.stderr)
        
        return None
    
    def analyze_repositories(self, repos: List[Dict], pattern_matcher) -> Dict:
        """Analyze multiple repositories"""
        self.temp_dir = tempfile.mkdtemp()
        results = {
            'repositories': [],
            'summary': {
                'total_repos': len(repos),
                'successful_scans': 0,
                'failed_scans': 0,
                'total_issues': 0,
                'by_severity': {'error': 0, 'warning': 0, 'info': 0},
                'by_category': {}
            }
        }
        
        try:
            for repo_data in repos:
                owner = repo_data['owner']['login']
                repo = repo_data['name']
                
                print(f"\n{'='*80}")
                print(f"Analyzing {owner}/{repo}...")
                print(f"{'='*80}")
                
                repo_path = self.clone_or_download_repo(owner, repo, self.temp_dir)
                
                if not repo_path:
                    results['summary']['failed_scans'] += 1
                    continue
                
                # Scan repository
                matches = pattern_matcher.scan_directory(repo_path, recursive=True)
                stats = pattern_matcher.get_statistics(matches)
                
                results['repositories'].append({
                    'owner': owner,
                    'name': repo,
                    'url': repo_data['html_url'],
                    'stars': repo_data['stargazers_count'],
                    'language': repo_data.get('language', 'Unknown'),
                    'issues_found': len(matches),
                    'statistics': stats
                })
                
                results['summary']['successful_scans'] += 1
                results['summary']['total_issues'] += len(matches)
                
                # Aggregate statistics
                for severity, count in stats['by_severity'].items():
                    results['summary']['by_severity'][severity] += count
                
                for category, count in stats['by_category'].items():
                    if category not in results['summary']['by_category']:
                        results['summary']['by_category'][category] = 0
                    results['summary']['by_category'][category] += count
                
                print(f"Found {len(matches)} issues in {owner}/{repo}")
                
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        
        return results
    
    def generate_cross_repo_report(self, results: Dict) -> str:
        """Generate cross-repository analysis report"""
        report = []
        report.append("="*80)
        report.append("Cross-Repository Pattern Analysis Report")
        report.append("="*80)
        report.append("")
        
        summary = results['summary']
        report.append(f"Repositories Analyzed: {summary['total_repos']}")
        report.append(f"Successful Scans: {summary['successful_scans']}")
        report.append(f"Failed Scans: {summary['failed_scans']}")
        report.append(f"Total Issues Found: {summary['total_issues']}")
        report.append("")
        
        report.append("Overall Severity Distribution:")
        report.append(f"  - Errors: {summary['by_severity']['error']}")
        report.append(f"  - Warnings: {summary['by_severity']['warning']}")
        report.append(f"  - Info: {summary['by_severity']['info']}")
        report.append("")
        
        report.append("Top Issue Categories Across All Repos:")
        sorted_categories = sorted(summary['by_category'].items(), 
                                  key=lambda x: x[1], reverse=True)[:10]
        for category, count in sorted_categories:
            report.append(f"  - {category.title()}: {count}")
        report.append("")
        
        report.append("-"*80)
        report.append("Per-Repository Results")
        report.append("-"*80)
        report.append("")
        
        # Sort repositories by issue count
        sorted_repos = sorted(results['repositories'], 
                            key=lambda x: x['issues_found'], reverse=True)
        
        for repo in sorted_repos:
            report.append(f"📦 {repo['owner']}/{repo['name']}")
            report.append(f"   URL: {repo['url']}")
            report.append(f"   Language: {repo['language']}")
            report.append(f"   Stars: ⭐ {repo['stars']}")
            report.append(f"   Issues Found: {repo['issues_found']}")
            
            stats = repo['statistics']
            report.append(f"   Severity: "
                        f"❌ {stats['by_severity']['error']} | "
                        f"⚠️  {stats['by_severity']['warning']} | "
                        f"ℹ️  {stats['by_severity']['info']}")
            
            # Top categories for this repo
            top_cats = sorted(stats['by_category'].items(), 
                            key=lambda x: x[1], reverse=True)[:3]
            if top_cats:
                report.append(f"   Top Issues: {', '.join(f'{cat} ({count})' for cat, count in top_cats)}")
            
            report.append("")
        
        report.append("="*80)
        
        return "\n".join(report)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Cross-Repository Pattern Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search and analyze Python repos with "machine-learning" topic
  %(prog)s --search "language:python topic:machine-learning" --max 5
  
  # Analyze specific repositories
  %(prog)s --repos "owner1/repo1,owner2/repo2"
  
  # Save results as JSON
  %(prog)s --search "language:javascript stars:>1000" --format json -o results.json
        """
    )
    
    parser.add_argument('--search', help='GitHub search query')
    parser.add_argument('--repos', help='Comma-separated list of owner/repo')
    parser.add_argument('--max', type=int, default=5,
                       help='Maximum repositories to analyze (default: 5)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--token', help='GitHub API token (or use GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    if not args.search and not args.repos:
        parser.error("Either --search or --repos must be specified")
    
    # Import pattern matcher
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pattern_matcher",
        os.path.join(os.path.dirname(__file__), "pattern-matcher.py")
    )
    pattern_matcher_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pattern_matcher_module)
    
    pattern_matcher = pattern_matcher_module.PatternMatcher()
    analyzer = GitHubRepoAnalyzer(token=args.token)
    
    # Get repositories to analyze
    repos = []
    
    if args.search:
        print(f"Searching GitHub for: {args.search}")
        repos = analyzer.search_repositories(args.search, args.max)
        print(f"Found {len(repos)} repositories")
    elif args.repos:
        # Parse repo list
        for repo_str in args.repos.split(','):
            repo_str = repo_str.strip()
            if '/' in repo_str:
                owner, name = repo_str.split('/', 1)
                repos.append({
                    'owner': {'login': owner},
                    'name': name,
                    'html_url': f'https://github.com/{owner}/{name}',
                    'stargazers_count': 0,
                    'language': 'Unknown'
                })
    
    if not repos:
        print("No repositories to analyze", file=sys.stderr)
        sys.exit(1)
    
    # Analyze repositories
    print(f"\nAnalyzing {len(repos)} repositories...")
    results = analyzer.analyze_repositories(repos, pattern_matcher)
    
    # Generate output
    if args.format == 'json':
        output = json.dumps(results, indent=2)
    else:
        output = analyzer.generate_cross_repo_report(results)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\nReport written to {args.output}")
    else:
        print("\n" + output)
    
    # Exit with appropriate code
    total_errors = results['summary']['by_severity']['error']
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == '__main__':
    main()
