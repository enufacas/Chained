#!/usr/bin/env python3
"""
Architecture Tracker - Automated architecture evolution tracking system

Analyzes the repository structure and tracks how the architecture evolves over time.
Generates data for visual diagrams and maintains a historical record of changes.

Features:
- Tracks directory structure and file organization
- Analyzes module dependencies and imports
- Monitors component growth and changes
- Generates Mermaid diagrams for documentation
- Exports data for D3.js visualizations
"""

import ast
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional


class ArchitectureTracker:
    """Main class for tracking architecture evolution"""
    
    def __init__(self, repo_path: str = ".", output_dir: str = "analysis/architecture"):
        self.repo_path = Path(repo_path)
        self.output_dir = output_dir
        self.timestamp = datetime.now().isoformat()
        self.git_commit = self._get_git_commit()
        self.architecture_data = {
            "timestamp": self.timestamp,
            "commit": self.git_commit,
            "structure": {},
            "dependencies": {},
            "metrics": {},
            "components": {}
        }
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    def _get_commit_message(self) -> str:
        """Get current commit message"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze the directory structure of the repository"""
        structure = {
            "directories": {},
            "files_by_type": defaultdict(int),
            "total_files": 0,
            "total_lines": 0
        }
        
        # Key directories to track
        key_dirs = [
            "tools", "docs", ".github/workflows", ".github/agents",
            "analysis", "learnings", "test_files"
        ]
        
        for dir_name in key_dirs:
            dir_path = self.repo_path / dir_name
            if dir_path.exists():
                dir_info = self._analyze_directory(dir_path)
                structure["directories"][dir_name] = dir_info
                structure["total_files"] += dir_info["file_count"]
                structure["total_lines"] += dir_info["line_count"]
        
        # Count test files in root
        test_files = list(self.repo_path.glob("test_*.py"))
        if test_files:
            test_info = {
                "file_count": len(test_files),
                "line_count": sum(self._count_lines(f) for f in test_files),
                "files": [f.name for f in test_files]
            }
            structure["directories"]["root_tests"] = test_info
            structure["total_files"] += test_info["file_count"]
            structure["total_lines"] += test_info["line_count"]
        
        self.architecture_data["structure"] = structure
        return structure
    
    def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Analyze a single directory"""
        if not dir_path.exists() or not dir_path.is_dir():
            return {"file_count": 0, "line_count": 0, "files": []}
        
        files = []
        line_count = 0
        
        try:
            for item in dir_path.rglob("*"):
                if item.is_file() and not self._should_ignore(item):
                    files.append(item.name)
                    line_count += self._count_lines(item)
        except (PermissionError, OSError):
            pass
        
        return {
            "file_count": len(files),
            "line_count": line_count,
            "files": sorted(files)[:50]  # Limit to first 50 files
        }
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            ".git", "__pycache__", "node_modules", ".pytest_cache",
            ".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib"
        ]
        path_str = str(path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze Python module dependencies"""
        dependencies = {
            "internal_imports": defaultdict(list),
            "external_imports": defaultdict(int),
            "module_graph": []
        }
        
        # Analyze Python files in tools directory
        tools_dir = self.repo_path / "tools"
        if tools_dir.exists():
            for py_file in tools_dir.glob("*.py"):
                if py_file.name.startswith("test_"):
                    continue
                
                imports = self._extract_imports(py_file)
                if imports:
                    dependencies["internal_imports"][py_file.name] = imports["internal"]
                    for ext in imports["external"]:
                        dependencies["external_imports"][ext] += 1
        
        # Create module graph for visualization
        for module, imported in dependencies["internal_imports"].items():
            for imp in imported:
                dependencies["module_graph"].append({
                    "source": module,
                    "target": imp,
                    "type": "imports"
                })
        
        # Convert defaultdict to regular dict for JSON serialization
        dependencies["internal_imports"] = dict(dependencies["internal_imports"])
        dependencies["external_imports"] = dict(dependencies["external_imports"])
        
        self.architecture_data["dependencies"] = dependencies
        return dependencies
    
    def _extract_imports(self, file_path: Path) -> Dict[str, List[str]]:
        """Extract imports from a Python file"""
        imports = {"internal": [], "external": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        imports["external"].append(module)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        # Check if it's an internal import (relative or tools/)
                        if node.level > 0 or module in ["tools", "analysis"]:
                            imports["internal"].append(module)
                        else:
                            imports["external"].append(module)
        
        except Exception:
            pass
        
        return imports
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate architecture metrics"""
        structure = self.architecture_data.get("structure", {})
        dependencies = self.architecture_data.get("dependencies", {})
        
        metrics = {
            "total_components": len(structure.get("directories", {})),
            "total_files": structure.get("total_files", 0),
            "total_lines": structure.get("total_lines", 0),
            "total_dependencies": len(dependencies.get("module_graph", [])),
            "external_libraries": len(dependencies.get("external_imports", {})),
            "coupling_score": self._calculate_coupling(dependencies),
            "complexity_score": self._calculate_complexity(structure)
        }
        
        self.architecture_data["metrics"] = metrics
        return metrics
    
    def _calculate_coupling(self, dependencies: Dict[str, Any]) -> float:
        """Calculate coupling score (0-1, lower is better)"""
        module_graph = dependencies.get("module_graph", [])
        internal_imports = dependencies.get("internal_imports", {})
        
        if not internal_imports:
            return 0.0
        
        total_modules = len(internal_imports)
        total_connections = len(module_graph)
        
        # Max possible connections in a fully connected graph
        max_connections = total_modules * (total_modules - 1)
        
        if max_connections == 0:
            return 0.0
        
        return min(1.0, total_connections / max_connections)
    
    def _calculate_complexity(self, structure: Dict[str, Any]) -> float:
        """Calculate complexity score (0-1, higher means more complex)"""
        total_files = structure.get("total_files", 0)
        total_lines = structure.get("total_lines", 0)
        
        if total_files == 0:
            return 0.0
        
        # Average lines per file
        avg_lines = total_lines / total_files
        
        # Normalize to 0-1 scale (200 lines per file = 0.5)
        return min(1.0, avg_lines / 400)
    
    def identify_components(self) -> Dict[str, Any]:
        """Identify major architectural components"""
        components = {}
        
        # Define component categories based on file patterns and directories
        component_mappings = {
            "learning_system": {
                "dirs": ["learnings"],
                "file_patterns": ["learn-from", "archaeology-learner"]
            },
            "agent_system": {
                "dirs": [".github/agents"],
                "file_patterns": ["agent-spawner", "match-issue-to-agent", "generate-new-agent", "agent-"]
            },
            "analysis_tools": {
                "dirs": ["analysis"],
                "file_patterns": ["code-analyzer", "pattern-matcher", "knowledge_graph", "analyzer", "archaeology"]
            },
            "workflows": {
                "dirs": [".github/workflows"],
                "file_patterns": []
            },
            "documentation": {
                "dirs": ["docs"],
                "file_patterns": []
            },
            "testing": {
                "dirs": ["root_tests"],
                "file_patterns": ["test_"]
            },
            "tools": {
                "dirs": ["tools"],
                "file_patterns": []
            }
        }
        
        structure = self.architecture_data.get("structure", {})
        directories = structure.get("directories", {})
        
        for component_name, config in component_mappings.items():
            component_files = []
            component_lines = 0
            matched_dirs = []
            
            # Check directory matches
            for dir_name, dir_info in directories.items():
                # Check if directory matches any configured directory
                for pattern_dir in config["dirs"]:
                    if pattern_dir in dir_name:
                        component_files.extend(dir_info.get("files", []))
                        component_lines += dir_info.get("line_count", 0)
                        matched_dirs.append(dir_name)
                        break
                
                # Also check file patterns within any directory
                if not matched_dirs or component_name in ["learning_system", "agent_system", "analysis_tools", "testing"]:
                    for file_name in dir_info.get("files", []):
                        for file_pattern in config["file_patterns"]:
                            if file_pattern in file_name:
                                if file_name not in component_files:
                                    component_files.append(file_name)
                                    # Estimate lines (we don't have per-file data, so this is approximate)
                                    if dir_info.get("file_count", 0) > 0:
                                        component_lines += dir_info.get("line_count", 0) // dir_info.get("file_count", 1)
                                break
            
            if component_files or component_lines > 0:
                # Remove duplicates
                component_files = list(set(component_files))
                components[component_name] = {
                    "file_count": len(component_files),
                    "line_count": component_lines,
                    "files": sorted(component_files)[:20]  # Limit for JSON size
                }
        
        self.architecture_data["components"] = components
        return components
    
    def generate_mermaid_diagram(self) -> str:
        """Generate a Mermaid diagram of the architecture"""
        components = self.architecture_data.get("components", {})
        dependencies = self.architecture_data.get("dependencies", {})
        
        mermaid = ["graph TD"]
        
        # Add component nodes
        for comp_name, comp_data in components.items():
            display_name = comp_name.replace("_", " ").title()
            file_count = comp_data.get("file_count", 0)
            mermaid.append(f"    {comp_name}[{display_name}<br/>{file_count} files]")
        
        # Add some logical relationships
        relationships = [
            ("learning_system", "agent_system", "feeds"),
            ("agent_system", "workflows", "triggers"),
            ("analysis_tools", "documentation", "generates"),
            ("workflows", "testing", "validates")
        ]
        
        for source, target, label in relationships:
            if source in components and target in components:
                mermaid.append(f"    {source} -->|{label}| {target}")
        
        return "\n".join(mermaid)
    
    def save_snapshot(self, output_dir: Optional[str] = None) -> str:
        """Save architecture snapshot to file"""
        if output_dir is None:
            output_dir = self.output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed snapshot with timestamp
        snapshot_file = output_path / f"snapshot_{self.timestamp.replace(':', '-').split('.')[0]}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(self.architecture_data, f, indent=2)
        
        # Update the latest snapshot
        latest_file = output_path / "latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(self.architecture_data, f, indent=2)
        
        # Update the evolution history
        history_file = output_path / "evolution.json"
        self._update_history(history_file)
        
        return str(snapshot_file)
    
    def _update_history(self, history_file: Path):
        """Update the evolution history file"""
        # Load existing history
        history = {"snapshots": []}
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass
        
        # Add current snapshot summary
        summary = {
            "timestamp": self.timestamp,
            "commit": self.git_commit,
            "commit_message": self._get_commit_message(),
            "metrics": self.architecture_data.get("metrics", {}),
            "component_count": len(self.architecture_data.get("components", {})),
            "file_count": self.architecture_data.get("structure", {}).get("total_files", 0)
        }
        
        history["snapshots"].append(summary)
        
        # Keep only last 100 snapshots
        history["snapshots"] = history["snapshots"][-100:]
        
        # Save updated history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    
    def generate_comparison(self, previous_snapshot: Optional[str] = None) -> Dict[str, Any]:
        """Generate comparison with previous snapshot"""
        if not previous_snapshot:
            # Try to load latest snapshot
            latest_file = Path("analysis/architecture/latest.json")
            if not latest_file.exists():
                return {"status": "no_previous_snapshot"}
            previous_snapshot = str(latest_file)
        
        try:
            with open(previous_snapshot, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
        except Exception:
            return {"status": "error_loading_previous"}
        
        # Compare metrics
        current_metrics = self.architecture_data.get("metrics", {})
        prev_metrics = prev_data.get("metrics", {})
        
        comparison = {
            "status": "success",
            "changes": {
                "files": current_metrics.get("total_files", 0) - prev_metrics.get("total_files", 0),
                "lines": current_metrics.get("total_lines", 0) - prev_metrics.get("total_lines", 0),
                "components": current_metrics.get("total_components", 0) - prev_metrics.get("total_components", 0),
                "dependencies": current_metrics.get("total_dependencies", 0) - prev_metrics.get("total_dependencies", 0)
            },
            "current_metrics": current_metrics,
            "previous_metrics": prev_metrics
        }
        
        return comparison
    
    def run_full_analysis(self, verbose: bool = True) -> Dict[str, Any]:
        """Run complete architecture analysis"""
        if verbose:
            print("🏗️  Starting architecture analysis...")
        
        if verbose:
            print("  📁 Analyzing structure...")
        self.analyze_structure()
        
        if verbose:
            print("  🔗 Analyzing dependencies...")
        self.analyze_dependencies()
        
        if verbose:
            print("  📊 Calculating metrics...")
        self.calculate_metrics()
        
        if verbose:
            print("  🧩 Identifying components...")
        self.identify_components()
        
        if verbose:
            print("  💾 Saving snapshot...")
        snapshot_file = self.save_snapshot()
        
        if verbose:
            print(f"  ✅ Analysis complete! Saved to {snapshot_file}")
        
        return self.architecture_data


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Track architecture evolution over time"
    )
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        "--output-dir",
        default="analysis/architecture",
        help="Output directory for snapshots (default: analysis/architecture)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare with previous snapshot"
    )
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help="Generate Mermaid diagram"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Run analysis
    tracker = ArchitectureTracker(args.repo_path, args.output_dir)
    verbose = not args.json  # Don't show progress in JSON mode
    data = tracker.run_full_analysis(verbose=verbose)
    
    # Generate comparison if requested
    if args.compare:
        if not args.json:
            print("\n📊 Comparing with previous snapshot...")
        comparison = tracker.generate_comparison()
        if comparison["status"] == "success":
            changes = comparison["changes"]
            if not args.json:
                print(f"  Files: {changes['files']:+d}")
                print(f"  Lines: {changes['lines']:+d}")
                print(f"  Components: {changes['components']:+d}")
                print(f"  Dependencies: {changes['dependencies']:+d}")
        else:
            if not args.json:
                print(f"  ⚠️  {comparison['status']}")
    
    # Generate Mermaid diagram if requested
    if args.mermaid:
        if not args.json:
            print("\n🎨 Generating Mermaid diagram...")
        diagram = tracker.generate_mermaid_diagram()
        mermaid_file = Path(args.output_dir) / "architecture.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(diagram)
        if not args.json:
            print(f"  Saved to {mermaid_file}")
    
    # Output JSON if requested
    if args.json:
        print(json.dumps(data, indent=2))
    
    # Print summary
    if not args.json:
        print("\n📈 Architecture Summary:")
        metrics = data.get("metrics", {})
        print(f"  Total Files: {metrics.get('total_files', 0)}")
        print(f"  Total Lines: {metrics.get('total_lines', 0)}")
        print(f"  Components: {metrics.get('total_components', 0)}")
        print(f"  Dependencies: {metrics.get('total_dependencies', 0)}")
        print(f"  Coupling Score: {metrics.get('coupling_score', 0):.2f}")
        print(f"  Complexity Score: {metrics.get('complexity_score', 0):.2f}")


if __name__ == "__main__":
    main()
