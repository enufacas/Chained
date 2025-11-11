#!/usr/bin/env python3
"""
Example: Using GitHub Integration Utilities

This example demonstrates how to use the GitHub integration utilities
to build reliable integrations with proper error handling and retry logic.
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from github_integration import (
    GitHubAPIClient,
    GitHubAPIException,
    RetryConfig,
    RetryStrategy,
    validate_response
)


def example_basic_usage():
    """Example 1: Basic API usage"""
    print("=" * 60)
    print("Example 1: Basic API Usage")
    print("=" * 60)
    
    # Initialize client (uses GITHUB_TOKEN or GH_TOKEN from environment)
    client = GitHubAPIClient()
    
    try:
        # Get repository information
        repo = client.get('/repos/github/docs')
        
        # Validate response has required fields
        validate_response(repo, ['id', 'name', 'full_name'])
        
        print(f"✓ Repository: {repo['full_name']}")
        print(f"  Stars: {repo['stargazers_count']}")
        print(f"  Language: {repo['language']}")
        print(f"  Open Issues: {repo['open_issues_count']}")
        
    except GitHubAPIException as e:
        print(f"✗ API Error: {e.error.message}")
        if e.error.documentation_url:
            print(f"  See: {e.error.documentation_url}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_retry_logic():
    """Example 2: Custom retry configuration"""
    print("=" * 60)
    print("Example 2: Custom Retry Configuration")
    print("=" * 60)
    
    # Configure aggressive retry for critical operations
    retry_config = RetryConfig(
        max_attempts=5,
        initial_delay=1.0,
        max_delay=30.0,
        backoff_factor=2.0,
        strategy=RetryStrategy.EXPONENTIAL
    )
    
    client = GitHubAPIClient(retry_config=retry_config)
    
    try:
        # This will automatically retry on transient failures
        issues = client.get('/repos/github/docs/issues', params={
            'state': 'open',
            'per_page': 5
        })
        
        print(f"✓ Retrieved {len(issues)} open issues")
        for issue in issues[:3]:
            print(f"  #{issue['number']}: {issue['title'][:50]}")
        
    except GitHubAPIException as e:
        print(f"✗ API Error: {e.error.message}")
    
    print()


def example_error_handling():
    """Example 3: Comprehensive error handling"""
    print("=" * 60)
    print("Example 3: Error Handling")
    print("=" * 60)
    
    client = GitHubAPIClient()
    
    # Try to access a non-existent repository
    try:
        repo = client.get('/repos/nonexistent-owner/nonexistent-repo-12345')
        print(f"Repository: {repo['name']}")
        
    except GitHubAPIException as e:
        error = e.error
        
        print(f"✓ Caught API error:")
        print(f"  Status: {error.status_code}")
        print(f"  Message: {error.message}")
        
        # Handle different error types
        if error.is_not_found:
            print(f"  → Repository not found (404)")
        elif error.is_auth_error:
            print(f"  → Authentication required")
        elif error.is_rate_limited:
            print(f"  → Rate limited")
            print(f"  → Resets at: {error.rate_limit_reset}")
        
    print()


def example_graphql():
    """Example 4: GraphQL queries"""
    print("=" * 60)
    print("Example 4: GraphQL Queries")
    print("=" * 60)
    
    client = GitHubAPIClient()
    
    query = '''
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        name
        description
        stargazerCount
        forkCount
        issues(first: 3, states: OPEN) {
          totalCount
          nodes {
            number
            title
          }
        }
      }
    }
    '''
    
    try:
        result = client.graphql(query, variables={
            'owner': 'github',
            'name': 'docs'
        })
        
        repo = result['repository']
        
        print(f"✓ Repository: {repo['name']}")
        print(f"  Description: {repo['description'][:60]}...")
        print(f"  Stars: {repo['stargazerCount']}")
        print(f"  Forks: {repo['forkCount']}")
        print(f"  Open Issues: {repo['issues']['totalCount']}")
        
        print("\n  Recent Issues:")
        for issue in repo['issues']['nodes']:
            print(f"    #{issue['number']}: {issue['title'][:50]}")
        
    except GitHubAPIException as e:
        print(f"✗ API Error: {e.error.message}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_rate_limit_monitoring():
    """Example 5: Rate limit monitoring"""
    print("=" * 60)
    print("Example 5: Rate Limit Monitoring")
    print("=" * 60)
    
    client = GitHubAPIClient()
    
    try:
        rate_limit = client.get('/rate_limit')
        
        for resource_type, limits in rate_limit['resources'].items():
            remaining = limits['remaining']
            total = limits['limit']
            percentage = (remaining / total * 100) if total > 0 else 0
            
            print(f"✓ {resource_type.capitalize()} API:")
            print(f"  Remaining: {remaining}/{total} ({percentage:.1f}%)")
            
            if remaining < 100:
                print(f"  ⚠️  Low rate limit!")
        
    except GitHubAPIException as e:
        print(f"✗ API Error: {e.error.message}")
    
    print()


def example_bulk_operations():
    """Example 6: Bulk operations with error handling"""
    print("=" * 60)
    print("Example 6: Bulk Operations")
    print("=" * 60)
    
    client = GitHubAPIClient(retry_config=RetryConfig(max_attempts=3))
    
    # List of popular repositories
    repos = [
        'github/docs',
        'microsoft/vscode',
        'vercel/next.js'
    ]
    
    results = []
    
    for repo_name in repos:
        try:
            repo = client.get(f'/repos/{repo_name}')
            results.append({
                'name': repo['full_name'],
                'stars': repo['stargazers_count'],
                'language': repo['language']
            })
            
        except GitHubAPIException as e:
            if e.error.is_rate_limited:
                print(f"  ⚠️  Rate limited on {repo_name}, will retry automatically")
            else:
                print(f"  ✗ Error fetching {repo_name}: {e.error.message}")
    
    print(f"✓ Successfully fetched {len(results)} repositories")
    
    # Sort by stars
    results.sort(key=lambda x: x['stars'], reverse=True)
    
    print("\n  Top repositories by stars:")
    for repo in results:
        print(f"    {repo['name']}: {repo['stars']:,} stars ({repo['language']})")
    
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "GitHub Integration Utilities Examples" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Check for token
    if not os.environ.get('GITHUB_TOKEN') and not os.environ.get('GH_TOKEN'):
        print("⚠️  Warning: No GitHub token found in environment")
        print("   Set GITHUB_TOKEN or GH_TOKEN for higher rate limits")
        print()
    
    # Run examples
    example_basic_usage()
    example_retry_logic()
    example_error_handling()
    example_graphql()
    example_rate_limit_monitoring()
    example_bulk_operations()
    
    print("=" * 60)
    print("✓ All examples completed!")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
