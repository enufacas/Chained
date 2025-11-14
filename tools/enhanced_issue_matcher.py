#!/usr/bin/env python3
"""
Enhanced Issue Matcher with Semantic Similarity

Integrates the semantic similarity engine with the existing agent matching system.
When matching issues to agents, it now also searches for similar historical issues
and provides context about past solutions.

Created by @engineer-master with systematic approach to integration.
"""

import sys
import json
from pathlib import Path

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

try:
    from semantic_similarity_engine import SemanticSimilarityEngine
    SIMILARITY_AVAILABLE = True
except ImportError:
    SIMILARITY_AVAILABLE = False
    print("Warning: Semantic similarity engine not available", file=sys.stderr)


def enhance_issue_match(title, body="", agent_match=None):
    """
    Enhance agent matching with historical similarity search.
    
    Args:
        title: Issue title
        body: Issue body
        agent_match: Result from match-issue-to-agent.py (optional)
        
    Returns:
        Enhanced match result with historical context
    """
    result = {
        'title': title,
        'body': body,
        'agent_match': agent_match,
        'similar_issues': [],
        'recommendations': []
    }
    
    if not SIMILARITY_AVAILABLE:
        result['similarity_note'] = "Semantic similarity engine not available"
        return result
    
    # Initialize similarity engine
    try:
        engine = SemanticSimilarityEngine()
    except Exception as e:
        result['similarity_note'] = f"Could not initialize engine: {e}"
        return result
    
    # Search for similar issues
    try:
        matches = engine.find_similar_issues(
            title=title,
            body=body,
            top_k=5,
            min_similarity=0.15
        )
        
        # Convert matches to dict
        result['similar_issues'] = [match.to_dict() for match in matches]
        
        # Generate recommendations based on historical data
        if matches:
            # Most similar issue
            top_match = matches[0]
            result['recommendations'].append({
                'type': 'historical_solution',
                'confidence': 'high' if top_match.similarity_score > 0.5 else 'medium',
                'message': f"Similar issue #{top_match.issue_number} was resolved by {top_match.agent_assigned}",
                'suggestion': top_match.solution_summary,
                'similarity': top_match.similarity_score
            })
            
            # Check if historical agent matches suggested agent
            if agent_match and top_match.agent_assigned:
                suggested_agent = agent_match.get('agent', '')
                if suggested_agent == top_match.agent_assigned:
                    result['recommendations'].append({
                        'type': 'agent_confirmation',
                        'confidence': 'high',
                        'message': f"Agent suggestion confirmed by historical data: @{suggested_agent}",
                        'past_successes': sum(1 for m in matches if m.agent_assigned == suggested_agent)
                    })
                elif top_match.similarity_score > 0.6:
                    result['recommendations'].append({
                        'type': 'agent_alternative',
                        'confidence': 'medium',
                        'message': f"Historical data suggests @{top_match.agent_assigned} (solved similar issue)",
                        'current_suggestion': suggested_agent,
                        'historical_suggestion': top_match.agent_assigned
                    })
            
            # Check for patterns in solutions
            solution_agents = {}
            for match in matches[:3]:
                if match.agent_assigned:
                    solution_agents[match.agent_assigned] = solution_agents.get(match.agent_assigned, 0) + 1
            
            if solution_agents:
                most_common_agent = max(solution_agents, key=solution_agents.get)
                count = solution_agents[most_common_agent]
                if count > 1:
                    result['recommendations'].append({
                        'type': 'pattern_detection',
                        'confidence': 'high' if count >= 3 else 'medium',
                        'message': f"@{most_common_agent} has successfully resolved {count} similar issues",
                        'agent': most_common_agent
                    })
        
        # Statistics
        stats = engine.get_statistics()
        result['history_stats'] = stats
        
    except Exception as e:
        result['similarity_error'] = str(e)
    
    return result


def format_enhanced_output(result, format='text'):
    """
    Format enhanced match result for output.
    
    Args:
        result: Enhanced match result
        format: Output format ('text' or 'json')
        
    Returns:
        Formatted string
    """
    if format == 'json':
        return json.dumps(result, indent=2)
    
    # Text format
    lines = []
    lines.append("=" * 80)
    lines.append("Enhanced Issue Matching with Semantic Similarity")
    lines.append("=" * 80)
    lines.append("")
    
    # Original agent match
    if result.get('agent_match'):
        agent_match = result['agent_match']
        lines.append("🤖 Suggested Agent:")
        lines.append(f"   Agent: @{agent_match.get('agent', 'unknown')}")
        lines.append(f"   Confidence: {agent_match.get('confidence', 'unknown')}")
        lines.append(f"   Score: {agent_match.get('score', 0)}")
        lines.append("")
    
    # Similar issues
    if result.get('similar_issues'):
        lines.append("📚 Similar Historical Issues:")
        lines.append("")
        for i, issue in enumerate(result['similar_issues'][:3], 1):
            lines.append(f"{i}. Issue #{issue['issue_number']}: {issue['title']}")
            lines.append(f"   Similarity: {issue['similarity_score']:.1%}")
            lines.append(f"   Resolved by: @{issue['agent_assigned']}")
            lines.append(f"   Solution: {issue['solution_summary'][:80]}...")
            lines.append(f"   Matching terms: {', '.join(issue['matching_terms'][:5])}")
            lines.append("")
    else:
        lines.append("📚 No similar historical issues found")
        lines.append("")
    
    # Recommendations
    if result.get('recommendations'):
        lines.append("💡 Recommendations:")
        lines.append("")
        for rec in result['recommendations']:
            icon = {'high': '✅', 'medium': '⚠️', 'low': 'ℹ️'}.get(rec['confidence'], '📌')
            lines.append(f"{icon} {rec['message']}")
            if rec.get('suggestion'):
                lines.append(f"   Suggestion: {rec['suggestion'][:80]}...")
            lines.append("")
    
    # Statistics
    if result.get('history_stats'):
        stats = result['history_stats']
        lines.append("📊 History Statistics:")
        lines.append(f"   Total issues in history: {stats.get('total_issues', 0)}")
        if 'total_unique_terms' in stats:
            lines.append(f"   Unique terms indexed: {stats['total_unique_terms']}")
        if 'avg_terms_per_issue' in stats:
            lines.append(f"   Average terms per issue: {stats['avg_terms_per_issue']}")
        lines.append("")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def main():
    """Command-line interface for enhanced matching."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced Issue Matching with Semantic Similarity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic matching with similarity
  %(prog)s "API endpoint bug" --body "Getting 500 errors"
  
  # With JSON output
  %(prog)s "Performance issue" --body "Slow queries" --format json
  
  # Pipe from match-issue-to-agent.py
  ./match-issue-to-agent.py "API bug" | %(prog)s --from-stdin
        """
    )
    
    parser.add_argument('title', nargs='?', help='Issue title')
    parser.add_argument('--body', default='', help='Issue body')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    parser.add_argument('--from-stdin', action='store_true',
                       help='Read agent match from stdin')
    
    args = parser.parse_args()
    
    # Get title and body
    title = args.title
    body = args.body
    agent_match = None
    
    if args.from_stdin:
        # Read agent match from stdin
        try:
            stdin_data = sys.stdin.read()
            agent_match = json.loads(stdin_data)
            if not title:
                # Try to get title from agent match
                title = "Unknown"
        except json.JSONDecodeError:
            print("Error: Invalid JSON from stdin", file=sys.stderr)
            sys.exit(1)
    
    if not title:
        parser.print_help()
        sys.exit(1)
    
    # Enhance the match
    result = enhance_issue_match(title, body, agent_match)
    
    # Format and print output
    output = format_enhanced_output(result, args.format)
    print(output)


if __name__ == '__main__':
    main()
