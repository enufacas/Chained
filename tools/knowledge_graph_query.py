#!/usr/bin/env python3
"""
Knowledge Graph Query Interface - Query codebase relationships

Provides simple queries:
- "What files import X?"
- "Which agent worked on Y?"
- "What tests cover Z?"
- "Show files that frequently change together"
- Impact analysis and blast radius estimation
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Any, Optional
from collections import defaultdict


class KnowledgeGraphQuery:
    """Query interface for knowledge graph"""
    
    def __init__(self, graph_path: str = 'docs/data/codebase-graph.json'):
        self.graph_path = Path(graph_path)
        self.graph = self._load_graph()
        self._build_indices()
    
    def _load_graph(self) -> Dict[str, Any]:
        """Load knowledge graph from file"""
        if not self.graph_path.exists():
            raise FileNotFoundError(f"Knowledge graph not found at {self.graph_path}")
        
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_indices(self):
        """Build indices for fast queries"""
        self.nodes_by_id = {node['id']: node for node in self.graph['nodes']}
        self.nodes_by_type = defaultdict(list)
        
        for node in self.graph['nodes']:
            self.nodes_by_type[node['type']].append(node)
        
        # Build relationship indices
        self.relationships_by_source = defaultdict(list)
        self.relationships_by_target = defaultdict(list)
        self.relationships_by_type = defaultdict(list)
        
        for rel in self.graph['relationships']:
            self.relationships_by_source[rel['source']].append(rel)
            self.relationships_by_target[rel['target']].append(rel)
            self.relationships_by_type[rel['type']].append(rel)
    
    # === Basic Queries ===
    
    def what_imports(self, filepath: str) -> List[Dict[str, Any]]:
        """Find all files that import the specified file"""
        results = []
        
        for rel in self.relationships_by_target.get(filepath, []):
            if rel['type'] == 'imports':
                source_node = self.nodes_by_id.get(rel['source'])
                if source_node:
                    results.append({
                        'file': rel['source'],
                        'type': source_node['type'],
                        'label': source_node['label']
                    })
        
        return results
    
    def what_does_import(self, filepath: str) -> List[Dict[str, Any]]:
        """Find all files that this file imports"""
        results = []
        
        for rel in self.relationships_by_source.get(filepath, []):
            if rel['type'] == 'imports':
                target_node = self.nodes_by_id.get(rel['target'])
                if target_node:
                    results.append({
                        'file': rel['target'],
                        'type': target_node['type'],
                        'label': target_node['label']
                    })
        
        return results
    
    def which_agent_worked_on(self, filepath: str) -> List[Dict[str, Any]]:
        """Find agents that worked on the specified file"""
        results = []
        
        for rel in self.relationships_by_target.get(filepath, []):
            if rel['type'] == 'worked_on' and rel['source'].startswith('agent:'):
                agent_node = self.nodes_by_id.get(rel['source'])
                if agent_node:
                    results.append({
                        'agent': agent_node['label'],
                        'files_worked_on': agent_node.get('files_worked_on', 0),
                        'expertise': agent_node.get('expertise', [])
                    })
        
        return results
    
    def what_agent_worked_on(self, agent_name: str) -> List[Dict[str, Any]]:
        """Find all files an agent worked on"""
        agent_id = f'agent:{agent_name}'
        results = []
        
        for rel in self.relationships_by_source.get(agent_id, []):
            if rel['type'] == 'worked_on':
                file_node = self.nodes_by_id.get(rel['target'])
                if file_node:
                    results.append({
                        'file': rel['target'],
                        'type': file_node['type'],
                        'label': file_node['label'],
                        'functions': file_node.get('functions', 0),
                        'classes': file_node.get('classes', 0)
                    })
        
        return results
    
    def what_tests_cover(self, filepath: str) -> List[Dict[str, Any]]:
        """Find tests that cover the specified file"""
        results = []
        
        for rel in self.relationships_by_target.get(filepath, []):
            if rel['type'] == 'tests':
                test_node = self.nodes_by_id.get(rel['source'])
                if test_node:
                    results.append({
                        'test_file': rel['source'],
                        'label': test_node['label'],
                        'functions': test_node.get('functions', 0)
                    })
        
        return results
    
    def what_does_test_cover(self, test_filepath: str) -> List[Dict[str, Any]]:
        """Find what code a test file covers"""
        results = []
        
        for rel in self.relationships_by_source.get(test_filepath, []):
            if rel['type'] == 'tests':
                code_node = self.nodes_by_id.get(rel['target'])
                if code_node:
                    results.append({
                        'file': rel['target'],
                        'type': code_node['type'],
                        'label': code_node['label']
                    })
        
        return results
    
    def files_changed_together(self, filepath: str, min_weight: int = 3) -> List[Dict[str, Any]]:
        """Find files that frequently change with the specified file"""
        results = []
        
        # Check both directions
        for rel in self.relationships_by_source.get(filepath, []):
            if rel['type'] == 'changes_with' and rel['weight'] >= min_weight:
                target_node = self.nodes_by_id.get(rel['target'])
                if target_node:
                    results.append({
                        'file': rel['target'],
                        'label': target_node['label'],
                        'change_frequency': rel['weight']
                    })
        
        for rel in self.relationships_by_target.get(filepath, []):
            if rel['type'] == 'changes_with' and rel['weight'] >= min_weight:
                source_node = self.nodes_by_id.get(rel['source'])
                if source_node:
                    results.append({
                        'file': rel['source'],
                        'label': source_node['label'],
                        'change_frequency': rel['weight']
                    })
        
        # Sort by frequency
        results.sort(key=lambda x: x['change_frequency'], reverse=True)
        return results
    
    # === Impact Analysis ===
    
    def impact_analysis(self, filepath: str, depth: int = 2) -> Dict[str, Any]:
        """Analyze the impact of changes to a file"""
        visited = set()
        impact = {
            'directly_affected': [],
            'indirectly_affected': [],
            'tests_to_run': [],
            'agents_to_notify': [],
            'blast_radius': 0
        }
        
        def traverse(current_file: str, current_depth: int):
            if current_file in visited or current_depth > depth:
                return
            
            visited.add(current_file)
            
            # Find files that import this one
            for rel in self.relationships_by_target.get(current_file, []):
                if rel['type'] == 'imports':
                    affected_file = rel['source']
                    
                    if current_depth == 1:
                        impact['directly_affected'].append(affected_file)
                    else:
                        impact['indirectly_affected'].append(affected_file)
                    
                    traverse(affected_file, current_depth + 1)
            
            # Find tests
            for rel in self.relationships_by_target.get(current_file, []):
                if rel['type'] == 'tests':
                    impact['tests_to_run'].append(rel['source'])
            
            # Find agents
            for rel in self.relationships_by_target.get(current_file, []):
                if rel['type'] == 'worked_on':
                    agent_name = rel['source'].replace('agent:', '')
                    if agent_name not in impact['agents_to_notify']:
                        impact['agents_to_notify'].append(agent_name)
        
        traverse(filepath, 1)
        
        # Calculate blast radius
        impact['blast_radius'] = len(impact['directly_affected']) + len(impact['indirectly_affected'])
        
        # Deduplicate and sort
        impact['directly_affected'] = sorted(list(set(impact['directly_affected'])))
        impact['indirectly_affected'] = sorted(list(set(impact['indirectly_affected'])))
        impact['tests_to_run'] = sorted(list(set(impact['tests_to_run'])))
        
        return impact
    
    def find_dependencies(self, filepath: str) -> Dict[str, List[str]]:
        """Find all dependencies of a file (imports tree)"""
        dependencies = {
            'direct': [],
            'transitive': []
        }
        visited = set()
        
        def traverse(current_file: str, depth: int = 0):
            if current_file in visited:
                return
            
            visited.add(current_file)
            
            for rel in self.relationships_by_source.get(current_file, []):
                if rel['type'] == 'imports':
                    dep = rel['target']
                    
                    if depth == 0:
                        dependencies['direct'].append(dep)
                    else:
                        dependencies['transitive'].append(dep)
                    
                    traverse(dep, depth + 1)
        
        traverse(filepath)
        
        dependencies['direct'] = sorted(list(set(dependencies['direct'])))
        dependencies['transitive'] = sorted(list(set(dependencies['transitive'])))
        
        return dependencies
    
    # === Advanced Queries ===
    
    def find_expert_agents(self, topic: str) -> List[Dict[str, Any]]:
        """Find agents with expertise in a specific topic"""
        results = []
        
        for node in self.nodes_by_type['agent']:
            expertise = node.get('expertise', [])
            if topic.lower() in [e.lower() for e in expertise]:
                results.append({
                    'agent': node['label'],
                    'expertise': expertise,
                    'files_worked_on': node.get('files_worked_on', 0)
                })
        
        results.sort(key=lambda x: x['files_worked_on'], reverse=True)
        return results
    
    def find_complex_files(self, min_functions: int = 10) -> List[Dict[str, Any]]:
        """Find complex files with many functions"""
        results = []
        
        for node in self.nodes_by_type['code_file']:
            if node.get('functions', 0) >= min_functions:
                results.append({
                    'file': node['id'],
                    'functions': node['functions'],
                    'classes': node.get('classes', 0),
                    'lines_of_code': node.get('lines_of_code', 0),
                    'label': node['label']
                })
        
        results.sort(key=lambda x: x['functions'], reverse=True)
        return results
    
    def find_central_files(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find most central files (most connections)"""
        file_connections = defaultdict(int)
        
        for rel in self.graph['relationships']:
            if rel['type'] in ['imports', 'tests', 'changes_with']:
                file_connections[rel['source']] += 1
                file_connections[rel['target']] += 1
        
        results = []
        for file_id, connections in file_connections.items():
            node = self.nodes_by_id.get(file_id)
            if node and node['type'] in ['code_file', 'test_file']:
                results.append({
                    'file': file_id,
                    'connections': connections,
                    'label': node['label'],
                    'type': node['type']
                })
        
        results.sort(key=lambda x: x['connections'], reverse=True)
        return results[:top_n]
    
    def find_orphan_files(self) -> List[Dict[str, Any]]:
        """Find files with no relationships"""
        files_with_relationships = set()
        
        for rel in self.graph['relationships']:
            files_with_relationships.add(rel['source'])
            files_with_relationships.add(rel['target'])
        
        results = []
        for node in self.nodes_by_type['code_file'] + self.nodes_by_type.get('test_file', []):
            if node['id'] not in files_with_relationships:
                results.append({
                    'file': node['id'],
                    'label': node['label'],
                    'type': node['type']
                })
        
        return results
    
    # === Statistics ===
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return self.graph.get('statistics', {})
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get graph metadata"""
        return self.graph.get('metadata', {})
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get identified patterns"""
        return self.graph.get('patterns', {})
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get calculated metrics"""
        return self.graph.get('metrics', {})
    
    # === Predictive Intelligence ===
    
    def predict_bug_likelihood(self, filepath: str) -> Dict[str, Any]:
        """Predict likelihood of bugs in a file based on patterns"""
        node = self.nodes_by_id.get(filepath)
        if not node:
            return {"error": "File not found"}
        
        risk_score = 0
        risk_factors = []
        
        # Complexity risk
        complexity = node.get('complexity_score', 0)
        if complexity > 10:
            risk_score += 3
            risk_factors.append(f"High complexity ({complexity:.1f})")
        elif complexity > 5:
            risk_score += 1
            risk_factors.append(f"Moderate complexity ({complexity:.1f})")
        
        # Code smells
        smells = node.get('code_smells', [])
        if smells:
            risk_score += len(smells)
            risk_factors.append(f"Code smells detected: {', '.join(smells)}")
        
        # Large file risk
        lines = node.get('lines_of_code', 0)
        if lines > 500:
            risk_score += 2
            risk_factors.append(f"Large file ({lines} lines)")
        
        # High coupling risk
        imports = node.get('imports', 0)
        if imports > 10:
            risk_score += 1
            risk_factors.append(f"High coupling ({imports} imports)")
        
        # Historical refactoring (indicates troubled area)
        refactor_count = node.get('refactoring_count', 0)
        if refactor_count > 3:
            risk_score += 2
            risk_factors.append(f"Frequently refactored ({refactor_count} times)")
        
        # Error pattern history
        patterns = self.get_patterns()
        error_fixes = patterns.get('error_fixes', {})
        if filepath in error_fixes:
            error_count = len(error_fixes[filepath])
            risk_score += min(error_count, 3)
            risk_factors.append(f"Historical errors ({error_count} fixes)")
        
        # Calculate likelihood
        if risk_score >= 8:
            likelihood = "high"
        elif risk_score >= 4:
            likelihood = "medium"
        else:
            likelihood = "low"
        
        return {
            'file': filepath,
            'likelihood': likelihood,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendation': self._get_bug_likelihood_recommendation(likelihood, risk_factors)
        }
    
    def _get_bug_likelihood_recommendation(self, likelihood: str, factors: List[str]) -> str:
        """Generate recommendation based on bug likelihood"""
        if likelihood == "high":
            return "⚠️ High risk: Consider refactoring, adding tests, or breaking into smaller modules"
        elif likelihood == "medium":
            return "⚡ Medium risk: Review code quality and consider improvements"
        else:
            return "✅ Low risk: Code appears healthy"
    
    def suggest_expert_agent(self, filepath: str) -> Dict[str, Any]:
        """Suggest which agent should handle work on this file"""
        node = self.nodes_by_id.get(filepath)
        if not node:
            return {"error": "File not found"}
        
        # Find agents who worked on this file
        agents_worked_on = self.which_agent_worked_on(filepath)
        
        # Find agents with expertise in related areas
        expertise_needed = []
        if 'test' in filepath:
            expertise_needed.append('testing')
        if 'workflow' in filepath or '.github' in filepath:
            expertise_needed.append('automation')
        if 'agent' in filepath:
            expertise_needed.append('agent-system')
        if node.get('code_smells'):
            expertise_needed.append('refactoring')
        if node.get('complexity_score', 0) > 8:
            expertise_needed.append('optimization')
        
        suggestions = []
        
        # Prioritize agents who have worked on this file
        for agent_data in agents_worked_on:
            suggestions.append({
                'agent': agent_data['agent'],
                'reason': f"Previously worked on this file",
                'confidence': 'high',
                'expertise': agent_data.get('expertise', [])
            })
        
        # Find agents with matching expertise
        for expertise in expertise_needed:
            expert_agents = self.find_expert_agents(expertise)
            for agent_data in expert_agents[:2]:  # Top 2
                if not any(s['agent'] == agent_data['agent'] for s in suggestions):
                    suggestions.append({
                        'agent': agent_data['agent'],
                        'reason': f"Expert in {expertise}",
                        'confidence': 'medium',
                        'expertise': agent_data.get('expertise', [])
                    })
        
        return {
            'file': filepath,
            'suggestions': suggestions[:3],  # Top 3 suggestions
            'needed_expertise': expertise_needed
        }
    
    def identify_technical_debt(self, min_score: int = 5) -> List[Dict[str, Any]]:
        """Identify files with technical debt"""
        debt_files = []
        
        for node in self.nodes_by_type.get('code_file', []):
            debt_score = 0
            debt_indicators = []
            
            # Code smells
            smells = node.get('code_smells', [])
            if smells:
                debt_score += len(smells) * 2
                debt_indicators.extend(smells)
            
            # High complexity
            complexity = node.get('complexity_score', 0)
            if complexity > 10:
                debt_score += 3
                debt_indicators.append('high_complexity')
            
            # Large file
            if node.get('lines_of_code', 0) > 500:
                debt_score += 2
                debt_indicators.append('large_file')
            
            # No tests
            tests = self.what_tests_cover(node['id'])
            if not tests:
                debt_score += 2
                debt_indicators.append('no_test_coverage')
            
            # Frequent errors
            patterns = self.get_patterns()
            error_fixes = patterns.get('error_fixes', {})
            if node['id'] in error_fixes and len(error_fixes[node['id']]) > 2:
                debt_score += 3
                debt_indicators.append('error_prone')
            
            if debt_score >= min_score:
                debt_files.append({
                    'file': node['id'],
                    'label': node['label'],
                    'debt_score': debt_score,
                    'indicators': debt_indicators,
                    'lines': node.get('lines_of_code', 0),
                    'priority': 'high' if debt_score >= 10 else 'medium'
                })
        
        # Sort by debt score
        debt_files.sort(key=lambda x: x['debt_score'], reverse=True)
        return debt_files
    
    def find_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Find files that could benefit from optimization"""
        opportunities = []
        
        metrics = self.get_metrics()
        complexity_data = metrics.get('complexity', {})
        
        for filepath, complexity in complexity_data.items():
            node = self.nodes_by_id.get(filepath)
            if not node:
                continue
            
            opportunity_reasons = []
            
            # Large average function size
            if complexity.get('avg_function_size', 0) > 50:
                opportunity_reasons.append('Large functions that could be split')
            
            # High function count
            if complexity.get('functions', 0) > 20:
                opportunity_reasons.append('Many functions, consider modularization')
            
            # High complexity score
            if complexity.get('complexity_score', 0) > 8:
                opportunity_reasons.append('High complexity, simplification needed')
            
            # Files that change frequently together (might indicate coupling)
            changes_with = self.files_changed_together(filepath, min_weight=5)
            if len(changes_with) > 3:
                opportunity_reasons.append(f'High coupling with {len(changes_with)} files')
            
            if opportunity_reasons:
                opportunities.append({
                    'file': filepath,
                    'label': node['label'],
                    'opportunities': opportunity_reasons,
                    'complexity': complexity
                })
        
        return opportunities[:10]  # Top 10
    
    # === Interactive Query ===
    
    def query(self, query_string: str) -> Any:
        """Natural language-style query parser"""
        query_lower = query_string.lower()
        
        # Check for predictive/analytical queries (no file needed)
        if 'technical debt' in query_lower or 'debt' in query_lower:
            return self.identify_technical_debt()
        
        if 'optimization' in query_lower and 'opportunit' in query_lower:
            return self.find_optimization_opportunities()
        
        # Extract file path from query
        words = query_string.split()
        potential_file = None
        for word in words:
            if '.py' in word or '/' in word:
                potential_file = word.strip('?"\'')
                break
        
        if not potential_file:
            # Check for general queries
            if 'central' in query_lower or 'important' in query_lower:
                return self.find_central_files()
            elif 'complex' in query_lower:
                return self.find_complex_files()
            elif 'orphan' in query_lower:
                return self.find_orphan_files()
            else:
                return {"error": "No file specified in query"}
        
        # Route to appropriate query
        if 'bug' in query_lower and ('likelihood' in query_lower or 'risk' in query_lower):
            return self.predict_bug_likelihood(potential_file)
        
        elif 'expert' in query_lower or 'suggest agent' in query_lower or 'who should' in query_lower:
            return self.suggest_expert_agent(potential_file)
        
        elif 'import' in query_lower and 'what' in query_lower:
            if 'imports' in query_lower or 'does' in query_lower:
                return self.what_does_import(potential_file)
            else:
                return self.what_imports(potential_file)
        
        elif 'agent' in query_lower:
            if 'which' in query_lower or 'who' in query_lower:
                return self.which_agent_worked_on(potential_file)
            else:
                return self.what_agent_worked_on(potential_file)
        
        elif 'test' in query_lower:
            if 'what' in query_lower and 'cover' in query_lower:
                return self.what_tests_cover(potential_file)
            elif 'does' in query_lower:
                return self.what_does_test_cover(potential_file)
        
        elif 'impact' in query_lower or 'affect' in query_lower:
            return self.impact_analysis(potential_file)
        
        elif 'depend' in query_lower:
            return self.find_dependencies(potential_file)
        
        elif 'change' in query_lower and 'together' in query_lower:
            return self.files_changed_together(potential_file)
        
        else:
            return {"error": f"Could not parse query: {query_string}"}


def main():
    """Interactive CLI for querying knowledge graph"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Query knowledge graph')
    parser.add_argument('--graph', default='docs/data/codebase-graph.json', help='Path to knowledge graph')
    parser.add_argument('--query', help='Query string')
    parser.add_argument('--file', help='File to query about')
    parser.add_argument('--agent', help='Agent to query about')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    try:
        kgq = KnowledgeGraphQuery(args.graph)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Run 'python tools/knowledge-graph-builder.py' first to generate the graph")
        return 1
    
    # Statistics mode
    if args.stats:
        print("📊 Knowledge Graph Statistics")
        print("=" * 60)
        stats = kgq.get_statistics()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
        
        print("\n🏆 Top Central Files:")
        for i, file in enumerate(kgq.find_central_files(5), 1):
            print(f"  {i}. {file['label']} ({file['connections']} connections)")
        
        return 0
    
    # Natural language query
    if args.query:
        print(f"🔍 Query: {args.query}")
        result = kgq.query(args.query)
        print("\n📋 Results:")
        print(json.dumps(result, indent=2))
        return 0
    
    # File-specific queries
    if args.file:
        print(f"📁 Analyzing: {args.file}")
        print("=" * 60)
        
        print("\n📥 Imports:")
        imports = kgq.what_does_import(args.file)
        if imports:
            for imp in imports:
                print(f"  • {imp['file']}")
        else:
            print("  None found")
        
        print("\n📤 Imported by:")
        imported_by = kgq.what_imports(args.file)
        if imported_by:
            for imp in imported_by:
                print(f"  • {imp['file']}")
        else:
            print("  None found")
        
        print("\n🧪 Tested by:")
        tests = kgq.what_tests_cover(args.file)
        if tests:
            for test in tests:
                print(f"  • {test['test_file']}")
        else:
            print("  No tests found")
        
        print("\n🤖 Agents who worked on this:")
        agents = kgq.which_agent_worked_on(args.file)
        if agents:
            for agent in agents:
                print(f"  • {agent['agent']} (expertise: {', '.join(agent['expertise'])})")
        else:
            print("  No agents tracked")
        
        print("\n💥 Impact Analysis:")
        impact = kgq.impact_analysis(args.file)
        print(f"  Blast radius: {impact['blast_radius']} files")
        print(f"  Directly affected: {len(impact['directly_affected'])} files")
        print(f"  Tests to run: {len(impact['tests_to_run'])} tests")
        
        return 0
    
    # Agent-specific queries
    if args.agent:
        print(f"🤖 Agent: {args.agent}")
        print("=" * 60)
        
        files = kgq.what_agent_worked_on(args.agent)
        if files:
            print(f"\n📁 Files worked on ({len(files)}):")
            for f in files[:10]:
                print(f"  • {f['label']} ({f['functions']} functions, {f['classes']} classes)")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
        else:
            print("  No files found")
        
        return 0
    
    # Interactive mode
    if args.interactive:
        print("🧠 Knowledge Graph Interactive Query")
        print("=" * 60)
        print("Examples:")
        print("  - What imports tools/code-analyzer.py?")
        print("  - Which agent worked on test_agent_system.py?")
        print("  - What tests cover tools/knowledge-graph-builder.py?")
        print("  - What does test_ai_knowledge_graph.py cover?")
        print("  - Show impact of tools/knowledge-graph-query.py")
        print("  - type 'quit' to exit")
        print()
        
        while True:
            try:
                query = input("📝 Query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                result = kgq.query(query)
                print("\n📋 Results:")
                print(json.dumps(result, indent=2))
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
        
        return 0
    
    # No arguments, show help
    parser.print_help()
    return 0


if __name__ == '__main__':
    exit(main())
