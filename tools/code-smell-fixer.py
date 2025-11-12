#!/usr/bin/env python3
"""
Code Smell Fixer with Auto-Fix Capabilities for Chained

This tool detects and automatically fixes common code smells in Python code,
including long functions, deep nesting, magic numbers, unused imports, and more.
"""

import os
import sys
import ast
import re
import json
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import importlib.util

# Import the existing code analyzer for detection capabilities
spec = importlib.util.spec_from_file_location(
    "code_analyzer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-analyzer.py")
)
code_analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_analyzer)

CodeAnalyzer = code_analyzer.CodeAnalyzer


class CodeSmellFixer:
    """Detects and auto-fixes common code smells in Python code"""
    
    def __init__(self, dry_run: bool = False, interactive: bool = False, backup: bool = True):
        """
        Initialize the Code Smell Fixer.
        
        Args:
            dry_run: If True, preview changes without applying them
            interactive: If True, ask before applying each fix
            backup: If True, create backups before modifying files
        """
        self.dry_run = dry_run
        self.interactive = interactive
        self.backup = backup
        self.analyzer = CodeAnalyzer()
        self.fixes_applied = []
        self.fixes_skipped = []
        
    def _create_backup(self, filepath: str) -> Optional[str]:
        """Create a backup of the file before modification"""
        if not self.backup or self.dry_run:
            return None
            
        backup_dir = os.path.join(os.path.dirname(filepath), '.smell_fixer_backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    def _read_file(self, filepath: str) -> str:
        """Read file content"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _write_file(self, filepath: str, content: str):
        """Write content to file"""
        if not self.dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _should_apply_fix(self, fix_description: str) -> bool:
        """Ask user if fix should be applied in interactive mode"""
        if not self.interactive:
            return True
        
        response = input(f"\n{fix_description}\nApply this fix? (y/n/q): ").strip().lower()
        if response == 'q':
            print("Quitting...")
            sys.exit(0)
        return response == 'y'
    
    def fix_unused_imports(self, filepath: str) -> Dict[str, Any]:
        """
        Detect and remove unused imports.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with fix information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        # Collect all imports
        imports = []
        import_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_name = alias.asname if alias.asname else alias.name
                    imports.append((node, import_name, node.lineno))
                    import_names.add(import_name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == '*':
                        continue  # Skip wildcard imports
                    import_name = alias.asname if alias.asname else alias.name
                    imports.append((node, import_name, node.lineno))
                    import_names.add(import_name)
        
        # Find which imports are actually used
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For module.function calls
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Identify unused imports
        unused_imports = []
        for node, import_name, lineno in imports:
            if import_name not in used_names:
                unused_imports.append((import_name, lineno))
        
        if not unused_imports:
            return {"success": True, "changes": 0, "unused_imports": []}
        
        # Remove unused imports
        lines = content.split('\n')
        lines_to_remove = set()
        
        for import_name, lineno in unused_imports:
            if lineno <= len(lines):
                lines_to_remove.add(lineno - 1)  # Convert to 0-indexed
        
        if lines_to_remove:
            fix_desc = f"Remove {len(unused_imports)} unused import(s) in {filepath}"
            if self._should_apply_fix(fix_desc):
                new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
                new_content = '\n'.join(new_lines)
                
                backup_path = self._create_backup(filepath)
                self._write_file(filepath, new_content)
                
                fix_info = {
                    "success": True,
                    "changes": len(unused_imports),
                    "unused_imports": [name for name, _ in unused_imports],
                    "backup": backup_path
                }
                self.fixes_applied.append({"type": "unused_imports", "file": filepath, "details": fix_info})
                return fix_info
            else:
                self.fixes_skipped.append({"type": "unused_imports", "file": filepath})
                return {"success": False, "skipped": True}
        
        return {"success": True, "changes": 0, "unused_imports": []}
    
    def fix_magic_numbers(self, filepath: str) -> Dict[str, Any]:
        """
        Detect and extract magic numbers into named constants.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with fix information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        # Find magic numbers
        magic_numbers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                # Skip common values
                if node.value not in [0, 1, -1, 2, 10, 100, 1000]:
                    if hasattr(node, 'lineno'):
                        magic_numbers.append((node.value, node.lineno))
        
        if not magic_numbers:
            return {"success": True, "changes": 0, "magic_numbers": []}
        
        # Group by value and count occurrences
        number_counts = defaultdict(list)
        for value, lineno in magic_numbers:
            number_counts[value].append(lineno)
        
        # Only fix numbers that appear multiple times or are significant
        constants_to_add = []
        for value, linenos in number_counts.items():
            if len(linenos) >= 2 or abs(value) >= 100:
                constant_name = f"CONSTANT_{abs(int(value))}"
                constants_to_add.append((constant_name, value))
        
        if not constants_to_add:
            return {"success": True, "changes": 0, "magic_numbers": []}
        
        fix_desc = f"Extract {len(constants_to_add)} magic number(s) to constants in {filepath}"
        if self._should_apply_fix(fix_desc):
            lines = content.split('\n')
            
            # Find where to insert constants (after imports, before first function/class)
            insert_line = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import') and not line.strip().startswith('from'):
                    insert_line = i
                    break
            
            # Add constants
            constant_lines = [f"# Constants extracted by code-smell-fixer"]
            for name, value in constants_to_add:
                constant_lines.append(f"{name} = {value}")
            constant_lines.append("")  # Empty line after constants
            
            new_lines = lines[:insert_line] + constant_lines + lines[insert_line:]
            new_content = '\n'.join(new_lines)
            
            backup_path = self._create_backup(filepath)
            self._write_file(filepath, new_content)
            
            fix_info = {
                "success": True,
                "changes": len(constants_to_add),
                "constants_added": [(name, value) for name, value in constants_to_add],
                "backup": backup_path
            }
            self.fixes_applied.append({"type": "magic_numbers", "file": filepath, "details": fix_info})
            return fix_info
        else:
            self.fixes_skipped.append({"type": "magic_numbers", "file": filepath})
            return {"success": False, "skipped": True}
    
    def fix_missing_docstrings(self, filepath: str) -> Dict[str, Any]:
        """
        Add skeleton docstrings to functions and classes missing them.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with fix information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        lines = content.split('\n')
        functions_needing_docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    # Skip private functions (starting with _) unless they're special methods
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.startswith('_') and not node.name.startswith('__'):
                            continue
                    functions_needing_docstrings.append((node, type(node).__name__))
        
        if not functions_needing_docstrings:
            return {"success": True, "changes": 0, "docstrings_added": []}
        
        fix_desc = f"Add {len(functions_needing_docstrings)} docstring(s) in {filepath}"
        if self._should_apply_fix(fix_desc):
            # Sort by line number in reverse to maintain line numbers during insertion
            functions_needing_docstrings.sort(key=lambda x: x[0].lineno, reverse=True)
            
            for node, node_type in functions_needing_docstrings:
                def_line = node.lineno - 1
                indent = len(lines[def_line]) - len(lines[def_line].lstrip())
                
                if node_type == 'ClassDef':
                    docstring = f'{" " * (indent + 4)}"""TODO: Add class docstring."""'
                else:
                    docstring = f'{" " * (indent + 4)}"""TODO: Add function docstring."""'
                
                # Insert docstring after the def line
                lines.insert(def_line + 1, docstring)
            
            new_content = '\n'.join(lines)
            backup_path = self._create_backup(filepath)
            self._write_file(filepath, new_content)
            
            fix_info = {
                "success": True,
                "changes": len(functions_needing_docstrings),
                "docstrings_added": [node.name for node, _ in functions_needing_docstrings],
                "backup": backup_path
            }
            self.fixes_applied.append({"type": "missing_docstrings", "file": filepath, "details": fix_info})
            return fix_info
        else:
            self.fixes_skipped.append({"type": "missing_docstrings", "file": filepath})
            return {"success": False, "skipped": True}
    
    def fix_poor_variable_names(self, filepath: str) -> Dict[str, Any]:
        """
        Suggest improvements for poor variable names (single letters, etc).
        Note: This is mostly detection with suggestions, not automatic fixes.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with fix information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        poor_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                name = node.id
                # Check for poor naming patterns
                if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z', '_']:
                    if hasattr(node, 'lineno'):
                        poor_names.append((name, node.lineno, "single_letter"))
                elif name.lower() in ['temp', 'tmp', 'data', 'var', 'value']:
                    if hasattr(node, 'lineno'):
                        poor_names.append((name, node.lineno, "generic"))
        
        # For now, we just report poor names rather than auto-fixing
        # Auto-fixing variable names requires sophisticated analysis
        return {
            "success": True,
            "changes": 0,
            "poor_names_detected": poor_names,
            "note": "Variable renaming requires manual review for safety"
        }
    
    def fix_missing_type_hints(self, filepath: str) -> Dict[str, Any]:
        """
        Add basic type hints to functions where they're obvious.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with fix information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        functions_needing_hints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if already has type hints
                if node.returns or any(arg.annotation for arg in node.args.args):
                    continue
                
                # Skip private functions
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
                functions_needing_hints.append(node)
        
        # For now, we detect but don't auto-fix type hints
        # Adding correct type hints requires understanding the code context
        return {
            "success": True,
            "changes": 0,
            "functions_without_hints": [f.name for f in functions_needing_hints],
            "note": "Type hint additions require manual review for correctness"
        }
    
    def detect_long_functions(self, filepath: str) -> Dict[str, Any]:
        """
        Detect long functions (>50 lines).
        Note: Breaking down functions requires understanding logic flow.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with detection information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        long_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    long_functions.append((node.name, node.lineno, func_lines))
        
        return {
            "success": True,
            "long_functions": long_functions,
            "note": "Breaking down long functions requires manual refactoring"
        }
    
    def detect_deep_nesting(self, filepath: str) -> Dict[str, Any]:
        """
        Detect deep nesting (>4 levels).
        Note: Reducing nesting requires understanding control flow.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with detection information
        """
        content = self._read_file(filepath)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        
        def get_max_depth(node, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    child_depth = get_max_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_max_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        deep_nesting_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                max_depth = get_max_depth(node)
                if max_depth > 4:
                    deep_nesting_functions.append((node.name, node.lineno, max_depth))
        
        return {
            "success": True,
            "deep_nesting_functions": deep_nesting_functions,
            "note": "Reducing nesting requires manual refactoring"
        }
    
    def fix_file(self, filepath: str) -> Dict[str, Any]:
        """
        Apply all applicable fixes to a single file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary with all fix results
        """
        if not filepath.endswith('.py'):
            return {"error": "Only Python files are supported"}
        
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}
        
        print(f"\n{'='*60}")
        print(f"Processing: {filepath}")
        print(f"{'='*60}")
        
        results = {
            "file": filepath,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fixes": {}
        }
        
        # Apply auto-fixes
        print("\n[1/7] Checking for unused imports...")
        results["fixes"]["unused_imports"] = self.fix_unused_imports(filepath)
        
        print("[2/7] Checking for magic numbers...")
        results["fixes"]["magic_numbers"] = self.fix_magic_numbers(filepath)
        
        print("[3/7] Checking for missing docstrings...")
        results["fixes"]["missing_docstrings"] = self.fix_missing_docstrings(filepath)
        
        # Detection-only checks
        print("[4/7] Checking for poor variable names...")
        results["fixes"]["poor_variable_names"] = self.fix_poor_variable_names(filepath)
        
        print("[5/7] Checking for missing type hints...")
        results["fixes"]["missing_type_hints"] = self.fix_missing_type_hints(filepath)
        
        print("[6/7] Detecting long functions...")
        results["fixes"]["long_functions"] = self.detect_long_functions(filepath)
        
        print("[7/7] Detecting deep nesting...")
        results["fixes"]["deep_nesting"] = self.detect_deep_nesting(filepath)
        
        return results
    
    def fix_directory(self, directory: str) -> Dict[str, Any]:
        """
        Apply fixes to all Python files in a directory.
        
        Args:
            directory: Path to the directory
            
        Returns:
            Dictionary with all fix results
        """
        if not os.path.exists(directory):
            return {"error": f"Directory not found: {directory}"}
        
        if not os.path.isdir(directory):
            return {"error": f"Not a directory: {directory}"}
        
        results = {
            "directory": directory,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files": [],
            "summary": {
                "total_files": 0,
                "files_modified": 0,
                "total_fixes": 0
            }
        }
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and common excludes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.smell_fixer_backups']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    file_result = self.fix_file(filepath)
                    results["files"].append(file_result)
                    results["summary"]["total_files"] += 1
        
        # Calculate summary
        for file_result in results["files"]:
            if "fixes" in file_result:
                file_modified = False
                for fix_type, fix_result in file_result["fixes"].items():
                    if isinstance(fix_result, dict) and fix_result.get("success") and fix_result.get("changes", 0) > 0:
                        results["summary"]["total_fixes"] += fix_result["changes"]
                        file_modified = True
                if file_modified:
                    results["summary"]["files_modified"] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable report of fixes applied"""
        report = []
        report.append("# Code Smell Fixer Report")
        report.append(f"\n**Generated:** {results.get('timestamp', 'N/A')}")
        
        if "directory" in results:
            report.append(f"\n**Directory:** {results['directory']}")
            report.append(f"\n## Summary")
            report.append(f"- Total files processed: {results['summary']['total_files']}")
            report.append(f"- Files modified: {results['summary']['files_modified']}")
            report.append(f"- Total fixes applied: {results['summary']['total_fixes']}")
            
            if self.dry_run:
                report.append(f"\n**Note:** This was a DRY RUN. No changes were actually made.")
            
            report.append(f"\n## Details")
            for file_result in results["files"]:
                if "fixes" in file_result:
                    has_changes = any(
                        isinstance(fix, dict) and fix.get("success") and fix.get("changes", 0) > 0
                        for fix in file_result["fixes"].values()
                    )
                    if has_changes:
                        report.append(f"\n### {file_result['file']}")
                        for fix_type, fix_result in file_result["fixes"].items():
                            if isinstance(fix_result, dict) and fix_result.get("success") and fix_result.get("changes", 0) > 0:
                                report.append(f"- {fix_type}: {fix_result['changes']} fix(es)")
        
        elif "file" in results:
            report.append(f"\n**File:** {results['file']}")
            report.append(f"\n## Fixes Applied")
            
            if self.dry_run:
                report.append(f"\n**Note:** This was a DRY RUN. No changes were actually made.")
            
            for fix_type, fix_result in results.get("fixes", {}).items():
                if isinstance(fix_result, dict):
                    if fix_result.get("success"):
                        changes = fix_result.get("changes", 0)
                        if changes > 0:
                            report.append(f"\n### {fix_type}")
                            report.append(f"- Changes: {changes}")
                            if "backup" in fix_result and fix_result["backup"]:
                                report.append(f"- Backup: {fix_result['backup']}")
        
        report.append(f"\n## Fixes Applied")
        report.append(f"Total: {len(self.fixes_applied)}")
        
        report.append(f"\n## Fixes Skipped")
        report.append(f"Total: {len(self.fixes_skipped)}")
        
        return '\n'.join(report)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Code Smell Fixer - Detect and auto-fix common code smells',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and fix a single file (with backup)
  python code-smell-fixer.py -f myfile.py
  
  # Dry-run on a directory (preview changes)
  python code-smell-fixer.py -d src/ --dry-run
  
  # Interactive mode (ask before each fix)
  python code-smell-fixer.py -f myfile.py --interactive
  
  # Fix directory without backups
  python code-smell-fixer.py -d src/ --no-backup
  
  # Generate JSON report
  python code-smell-fixer.py -d src/ -o report.json --format json
        """
    )
    
    parser.add_argument('-f', '--file', help='Single file to analyze and fix')
    parser.add_argument('-d', '--directory', help='Directory to analyze and fix')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('--format', choices=['text', 'json'], default='text', 
                       help='Report format (default: text)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without applying them')
    parser.add_argument('--interactive', action='store_true',
                       help='Ask before applying each fix')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backups before modifying files')
    
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        parser.error("Either --file or --directory must be specified")
    
    # Create fixer instance
    fixer = CodeSmellFixer(
        dry_run=args.dry_run,
        interactive=args.interactive,
        backup=not args.no_backup
    )
    
    # Process files
    if args.file:
        results = fixer.fix_file(args.file)
    else:
        results = fixer.fix_directory(args.directory)
    
    # Generate report
    if args.format == 'json':
        report = json.dumps(results, indent=2)
    else:
        report = fixer.generate_report(results)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n✓ Report saved to: {args.output}")
    else:
        print("\n" + report)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  Fixes applied: {len(fixer.fixes_applied)}")
    print(f"  Fixes skipped: {len(fixer.fixes_skipped)}")
    if args.dry_run:
        print("  Mode: DRY RUN (no changes made)")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
