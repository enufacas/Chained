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
    
    # === Interactive Query ===
    
    def query(self, query_string: str) -> Any:
        """Natural language-style query parser"""
        query_lower = query_string.lower()
        
        # Extract file path from query
        words = query_string.split()
        potential_file = None
        for word in words:
            if '.py' in word or '/' in word:
                potential_file = word.strip('?"\'')
                break
        
        if not potential_file:
            return {"error": "No file specified in query"}
        
        # Route to appropriate query
        if 'import' in query_lower and 'what' in query_lower:
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
