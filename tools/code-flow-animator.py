#!/usr/bin/env python3
"""
Visual Code Execution Flow Animator

Traces code execution and generates visualization data showing:
- Function call sequences
- Variable state changes
- Control flow (loops, conditions)
- Execution timeline

Supports Python and JavaScript code analysis.
"""

import ast
import json
import sys
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path


class ExecutionStep:
    """Represents a single step in code execution"""
    
    def __init__(self, step_type: str, line_number: int, description: str, 
                 variables: Optional[Dict[str, Any]] = None, 
                 function_name: Optional[str] = None):
        self.step_type = step_type  # 'call', 'return', 'assign', 'condition', 'loop'
        self.line_number = line_number
        self.description = description
        self.variables = variables or {}
        self.function_name = function_name
        self.timestamp = None  # Will be set during actual execution
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.step_type,
            'line': self.line_number,
            'description': self.description,
            'variables': self.variables,
            'function': self.function_name,
            'timestamp': self.timestamp
        }


class PythonFlowAnalyzer(ast.NodeVisitor):
    """Analyzes Python code to extract execution flow"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.steps: List[ExecutionStep] = []
        self.current_function = None
        self.function_calls = []
        self.control_flow = []
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze the code and return flow data"""
        tree = ast.parse(self.source_code)
        self.visit(tree)
        
        return {
            'language': 'python',
            'source_lines': self.source_lines,
            'steps': [step.to_dict() for step in self.steps],
            'function_calls': self.function_calls,
            'control_flow': self.control_flow,
            'statistics': self._get_statistics()
        }
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions"""
        self.current_function = node.name
        
        step = ExecutionStep(
            step_type='call',
            line_number=node.lineno,
            description=f"Function '{node.name}' defined with {len(node.args.args)} parameter(s)",
            function_name=node.name
        )
        self.steps.append(step)
        
        self.function_calls.append({
            'name': node.name,
            'line': node.lineno,
            'params': [arg.arg for arg in node.args.args]
        })
        
        self.generic_visit(node)
        self.current_function = None
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Track variable assignments"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                value_desc = self._get_value_description(node.value)
                
                step = ExecutionStep(
                    step_type='assign',
                    line_number=node.lineno,
                    description=f"Assign {var_name} = {value_desc}",
                    variables={var_name: value_desc},
                    function_name=self.current_function
                )
                self.steps.append(step)
        
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If) -> None:
        """Track conditional statements"""
        condition_desc = self._get_value_description(node.test)
        
        step = ExecutionStep(
            step_type='condition',
            line_number=node.lineno,
            description=f"If condition: {condition_desc}",
            function_name=self.current_function
        )
        self.steps.append(step)
        
        self.control_flow.append({
            'type': 'if',
            'line': node.lineno,
            'condition': condition_desc,
            'has_else': len(node.orelse) > 0
        })
        
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> None:
        """Track for loops"""
        target = node.target.id if isinstance(node.target, ast.Name) else 'item'
        iter_desc = self._get_value_description(node.iter)
        
        step = ExecutionStep(
            step_type='loop',
            line_number=node.lineno,
            description=f"For loop: {target} in {iter_desc}",
            function_name=self.current_function
        )
        self.steps.append(step)
        
        self.control_flow.append({
            'type': 'for',
            'line': node.lineno,
            'variable': target,
            'iterable': iter_desc
        })
        
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> None:
        """Track while loops"""
        condition_desc = self._get_value_description(node.test)
        
        step = ExecutionStep(
            step_type='loop',
            line_number=node.lineno,
            description=f"While loop: {condition_desc}",
            function_name=self.current_function
        )
        self.steps.append(step)
        
        self.control_flow.append({
            'type': 'while',
            'line': node.lineno,
            'condition': condition_desc
        })
        
        self.generic_visit(node)
    
    def visit_Return(self, node: ast.Return) -> None:
        """Track return statements"""
        value_desc = self._get_value_description(node.value) if node.value else 'None'
        
        step = ExecutionStep(
            step_type='return',
            line_number=node.lineno,
            description=f"Return {value_desc}",
            function_name=self.current_function
        )
        self.steps.append(step)
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Track function calls"""
        func_name = self._get_function_name(node.func)
        
        step = ExecutionStep(
            step_type='call',
            line_number=node.lineno,
            description=f"Call function: {func_name}()",
            function_name=self.current_function
        )
        self.steps.append(step)
        
        self.generic_visit(node)
    
    def _get_value_description(self, node: ast.AST) -> str:
        """Get a string description of an AST node value"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            left = self._get_value_description(node.left)
            right = self._get_value_description(node.right)
            op = self._get_operator(node.op)
            return f"{left} {op} {right}"
        elif isinstance(node, ast.Call):
            return f"{self._get_function_name(node.func)}()"
        elif isinstance(node, ast.List):
            return "[...]"
        elif isinstance(node, ast.Dict):
            return "{...}"
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else '...'
    
    def _get_function_name(self, node: ast.AST) -> str:
        """Extract function name from a call node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_value_description(node.value)}.{node.attr}"
        else:
            return "unknown"
    
    def _get_operator(self, op: ast.operator) -> str:
        """Get string representation of an operator"""
        ops = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**', ast.FloorDiv: '//',
            ast.Lt: '<', ast.Gt: '>', ast.LtE: '<=', ast.GtE: '>=',
            ast.Eq: '==', ast.NotEq: '!=', ast.And: 'and', ast.Or: 'or'
        }
        return ops.get(type(op), '?')
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about the code flow"""
        return {
            'total_steps': len(self.steps),
            'function_definitions': len(self.function_calls),
            'control_flow_statements': len(self.control_flow),
            'assignments': sum(1 for s in self.steps if s.step_type == 'assign'),
            'function_calls': sum(1 for s in self.steps if s.step_type == 'call'),
            'returns': sum(1 for s in self.steps if s.step_type == 'return')
        }


class JavaScriptFlowAnalyzer:
    """Analyzes JavaScript code to extract execution flow (simplified)"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze JavaScript code (basic pattern matching)"""
        steps = []
        function_calls = []
        control_flow = []
        
        for i, line in enumerate(self.source_lines, 1):
            line = line.strip()
            
            # Detect function definitions
            if 'function' in line or '=>' in line:
                func_name = self._extract_function_name(line)
                steps.append({
                    'type': 'call',
                    'line': i,
                    'description': f"Function '{func_name}' defined",
                    'function': func_name
                })
                function_calls.append({'name': func_name, 'line': i})
            
            # Detect variable assignments
            elif 'const' in line or 'let' in line or 'var' in line or '=' in line:
                var_name = self._extract_var_name(line)
                steps.append({
                    'type': 'assign',
                    'line': i,
                    'description': f"Variable assignment: {line[:50]}",
                    'variables': {var_name: 'value'}
                })
            
            # Detect conditionals
            elif 'if' in line or 'else' in line:
                steps.append({
                    'type': 'condition',
                    'line': i,
                    'description': f"Conditional: {line[:50]}"
                })
                control_flow.append({'type': 'if', 'line': i})
            
            # Detect loops
            elif 'for' in line or 'while' in line:
                loop_type = 'for' if 'for' in line else 'while'
                steps.append({
                    'type': 'loop',
                    'line': i,
                    'description': f"{loop_type.title()} loop: {line[:50]}"
                })
                control_flow.append({'type': loop_type, 'line': i})
            
            # Detect return statements
            elif 'return' in line:
                steps.append({
                    'type': 'return',
                    'line': i,
                    'description': f"Return: {line[:50]}"
                })
        
        return {
            'language': 'javascript',
            'source_lines': self.source_lines,
            'steps': steps,
            'function_calls': function_calls,
            'control_flow': control_flow,
            'statistics': {
                'total_steps': len(steps),
                'function_definitions': len(function_calls),
                'control_flow_statements': len(control_flow)
            }
        }
    
    def _extract_function_name(self, line: str) -> str:
        """Extract function name from a line"""
        if 'function' in line:
            parts = line.split('function')
            if len(parts) > 1:
                name_part = parts[1].strip().split('(')[0].strip()
                return name_part or 'anonymous'
        elif '=>' in line:
            parts = line.split('=>')[0].strip()
            if '=' in parts:
                return parts.split('=')[0].strip().split()[-1]
        return 'anonymous'
    
    def _extract_var_name(self, line: str) -> str:
        """Extract variable name from assignment"""
        if '=' in line:
            left = line.split('=')[0].strip()
            parts = left.split()
            if parts:
                return parts[-1]
        return 'var'


class CodeFlowAnimator:
    """Main class for code flow animation"""
    
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'js']
    
    def analyze_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a code file and return flow data"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Auto-detect language from extension if not provided
        if not language:
            ext = path.suffix.lower()
            if ext == '.py':
                language = 'python'
            elif ext in ['.js', '.mjs']:
                language = 'javascript'
            else:
                raise ValueError(f"Cannot detect language from extension: {ext}")
        
        return self.analyze_code(source_code, language)
    
    def analyze_code(self, source_code: str, language: str) -> Dict[str, Any]:
        """Analyze source code and return flow data"""
        language = language.lower()
        
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}. Supported: {self.supported_languages}")
        
        if language == 'python':
            analyzer = PythonFlowAnalyzer(source_code)
        elif language in ['javascript', 'js']:
            analyzer = JavaScriptFlowAnalyzer(source_code)
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        flow_data = analyzer.analyze()
        flow_data['metadata'] = {
            'total_lines': len(flow_data['source_lines']),
            'language': language,
            'analyzer': self.__class__.__name__
        }
        
        return flow_data
    
    def save_flow_data(self, flow_data: Dict[str, Any], output_path: str) -> None:
        """Save flow data to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(flow_data, f, indent=2)
    
    def generate_html_report(self, flow_data: Dict[str, Any], output_path: str) -> None:
        """Generate an HTML visualization report"""
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Execution Flow - {language}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .stat-card p {{
            margin: 5px 0 0;
            opacity: 0.9;
        }}
        .flow-container {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .code-panel {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
        }}
        .code-line {{
            font-family: 'Courier New', monospace;
            padding: 5px;
            border-left: 3px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .code-line:hover {{
            background: #e9ecef;
        }}
        .code-line.active {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        .steps-panel {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            overflow-y: auto;
            max-height: 600px;
        }}
        .step-item {{
            background: white;
            border-left: 4px solid #667eea;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .step-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .step-item.call {{
            border-left-color: #28a745;
        }}
        .step-item.assign {{
            border-left-color: #17a2b8;
        }}
        .step-item.condition {{
            border-left-color: #ffc107;
        }}
        .step-item.loop {{
            border-left-color: #fd7e14;
        }}
        .step-item.return {{
            border-left-color: #dc3545;
        }}
        .step-line {{
            font-size: 0.85em;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        .step-desc {{
            font-weight: 500;
            margin-bottom: 5px;
        }}
        .step-vars {{
            font-size: 0.9em;
            color: #495057;
            background: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Code Execution Flow Analysis</h1>
        <p><strong>Language:</strong> {language} | <strong>Lines:</strong> {total_lines}</p>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{total_steps}</h3>
                <p>Total Steps</p>
            </div>
            <div class="stat-card">
                <h3>{function_definitions}</h3>
                <p>Functions</p>
            </div>
            <div class="stat-card">
                <h3>{control_flow_statements}</h3>
                <p>Control Flow</p>
            </div>
        </div>
        
        <div class="flow-container">
            <div class="code-panel">
                <h3>Source Code</h3>
                <div id="code-lines">
{code_lines_html}
                </div>
            </div>
            
            <div class="steps-panel">
                <h3>Execution Steps</h3>
                <div id="steps-list">
{steps_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const steps = {steps_json};
        
        // Add click handlers for code lines and steps
        document.querySelectorAll('.code-line').forEach(line => {{
            line.addEventListener('click', function() {{
                const lineNum = parseInt(this.dataset.line);
                highlightStepsForLine(lineNum);
            }});
        }});
        
        document.querySelectorAll('.step-item').forEach(step => {{
            step.addEventListener('click', function() {{
                const lineNum = parseInt(this.dataset.line);
                highlightCodeLine(lineNum);
            }});
        }});
        
        function highlightCodeLine(lineNum) {{
            document.querySelectorAll('.code-line').forEach(l => l.classList.remove('active'));
            const line = document.querySelector(`[data-line="${{lineNum}}"]`);
            if (line) {{
                line.classList.add('active');
                line.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }}
        
        function highlightStepsForLine(lineNum) {{
            const relatedSteps = steps.filter(s => s.line === lineNum);
            console.log('Steps for line', lineNum, ':', relatedSteps);
        }}
    </script>
</body>
</html>"""
        
        # Generate HTML for code lines
        code_lines_html = ''
        for i, line in enumerate(flow_data['source_lines'], 1):
            escaped_line = line.replace('<', '&lt;').replace('>', '&gt;')
            code_lines_html += f'<div class="code-line" data-line="{i}"><span style="color:#999; width:40px; display:inline-block">{i}</span>{escaped_line}</div>\n'
        
        # Generate HTML for steps
        steps_html = ''
        for step in flow_data['steps']:
            step_type = step.get('type', 'unknown')
            line_num = step.get('line', 0)
            desc = step.get('description', '')
            func = step.get('function', '')
            variables = step.get('variables', {})
            
            vars_html = ''
            if variables:
                vars_str = ', '.join(f"{k}={v}" for k, v in variables.items())
                vars_html = f'<div class="step-vars">Variables: {vars_str}</div>'
            
            func_html = f' <small>(in {func})</small>' if func else ''
            
            steps_html += f'''<div class="step-item {step_type}" data-line="{line_num}">
    <div class="step-line">Line {line_num}{func_html}</div>
    <div class="step-desc">{desc}</div>
    {vars_html}
</div>\n'''
        
        # Fill in the template
        html_content = html_template.format(
            language=flow_data['language'].title(),
            total_lines=flow_data['metadata']['total_lines'],
            total_steps=flow_data['statistics']['total_steps'],
            function_definitions=flow_data['statistics']['function_definitions'],
            control_flow_statements=flow_data['statistics']['control_flow_statements'],
            code_lines_html=code_lines_html,
            steps_html=steps_html,
            steps_json=json.dumps(flow_data['steps'])
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    parser = argparse.ArgumentParser(
        description='Visual Code Execution Flow Animator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a Python file
  python3 code-flow-animator.py -f script.py
  
  # Analyze JavaScript file
  python3 code-flow-animator.py -f app.js -l javascript
  
  # Generate HTML report
  python3 code-flow-animator.py -f script.py --html output.html
  
  # Save JSON data
  python3 code-flow-animator.py -f script.py --json flow.json
        """
    )
    
    parser.add_argument('-f', '--file', required=True,
                       help='Code file to analyze')
    parser.add_argument('-l', '--language', 
                       help='Programming language (auto-detected from extension if not specified)')
    parser.add_argument('--json', 
                       help='Output JSON file path')
    parser.add_argument('--html', 
                       help='Output HTML report path')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Output format (default: both)')
    
    args = parser.parse_args()
    
    try:
        animator = CodeFlowAnimator()
        flow_data = animator.analyze_file(args.file, args.language)
        
        # Determine output paths
        file_stem = Path(args.file).stem
        json_path = args.json or f'{file_stem}_flow.json'
        html_path = args.html or f'{file_stem}_flow.html'
        
        # Generate outputs based on format
        if args.format in ['json', 'both']:
            animator.save_flow_data(flow_data, json_path)
            print(f"✓ Flow data saved to: {json_path}")
        
        if args.format in ['html', 'both']:
            animator.generate_html_report(flow_data, html_path)
            print(f"✓ HTML report saved to: {html_path}")
        
        # Print summary
        print(f"\nAnalysis Summary:")
        print(f"  Language: {flow_data['language']}")
        print(f"  Total Lines: {flow_data['metadata']['total_lines']}")
        print(f"  Execution Steps: {flow_data['statistics']['total_steps']}")
        print(f"  Functions: {flow_data['statistics']['function_definitions']}")
        print(f"  Control Flow: {flow_data['statistics']['control_flow_statements']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
