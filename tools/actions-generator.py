#!/usr/bin/env python3
"""
GitHub Actions Generator

Generates custom GitHub Actions based on detected repository patterns.
Part of the Chained autonomous AI ecosystem.

Created by @engineer-master - Systematic action generation with validation.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import re


class ActionsGenerator:
    """
    Generates custom GitHub Actions based on repository patterns and
    analysis results.
    """
    
    def __init__(self, analysis_data: Dict[str, Any]):
        self.analysis = analysis_data
        self.generated_actions = []
        
    def generate_actions(self) -> List[Dict[str, Any]]:
        """
        Generate custom GitHub Actions based on analysis.
        
        Returns:
            List of generated action definitions.
        """
        print("🏗️  Generating custom GitHub Actions...")
        
        recommendations = self.analysis.get('recommendations', [])
        
        for rec in recommendations:
            pattern = rec.get('pattern', '')
            action_type = rec.get('action_type', 'composite')
            title = rec.get('title', '').lower()
            description = rec.get('description', '').lower()
            
            # Generate action based on pattern
            if 'python_automation' in pattern:
                action = self._generate_python_action(rec)
            elif 'javascript_automation' in pattern:
                action = self._generate_javascript_action(rec)
            elif 'testing' in pattern:
                action = self._generate_testing_action(rec)
            elif pattern.startswith('deployment_'):
                deploy_type = pattern.replace('deployment_', '')
                action = self._generate_deployment_action(rec, deploy_type)
            elif 'abstract repeated' in title or 'repeated' in description:
                action = self._generate_repeated_operation_action(rec)
            else:
                # Generic action
                action = self._generate_generic_action(rec)
            
            if action:
                self.generated_actions.append(action)
        
        print(f"✅ Generated {len(self.generated_actions)} custom actions.")
        return self.generated_actions
    
    def _generate_python_action(self, recommendation: Dict) -> Dict[str, Any]:
        """Generate a Python automation action."""
        action_name = "python-automation"
        
        action_yaml = {
            'name': 'Python Project Automation',
            'description': 'Automated Python linting, testing, and quality checks',
            'inputs': {
                'python-version': {
                    'description': 'Python version to use',
                    'required': False,
                    'default': '3.11'
                },
                'requirements-file': {
                    'description': 'Path to requirements file',
                    'required': False,
                    'default': 'requirements.txt'
                },
                'run-tests': {
                    'description': 'Whether to run tests',
                    'required': False,
                    'default': 'true'
                },
                'run-lint': {
                    'description': 'Whether to run linting',
                    'required': False,
                    'default': 'true'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Set up Python',
                        'uses': 'actions/setup-python@v4',
                        'with': {
                            'python-version': '${{ inputs.python-version }}'
                        }
                    },
                    {
                        'name': 'Install dependencies',
                        'shell': 'bash',
                        'run': '''
if [ -f "${{ inputs.requirements-file }}" ]; then
  pip install -r "${{ inputs.requirements-file }}"
fi
'''
                    },
                    {
                        'name': 'Run linting',
                        'if': "inputs.run-lint == 'true'",
                        'shell': 'bash',
                        'run': '''
if command -v flake8 &> /dev/null; then
  flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
fi
if command -v pylint &> /dev/null; then
  pylint **/*.py --disable=all --enable=E,F || true
fi
'''
                    },
                    {
                        'name': 'Run tests',
                        'if': "inputs.run-tests == 'true'",
                        'shell': 'bash',
                        'run': '''
if command -v pytest &> /dev/null; then
  pytest -v
elif [ -f "test_*.py" ] || [ -d "tests/" ]; then
  python -m unittest discover
fi
'''
                    }
                ]
            }
        }
        
        return {
            'name': action_name,
            'priority': recommendation['priority'],
            'action_yaml': action_yaml,
            'file_path': f'.github/actions/{action_name}/action.yml',
            'description': recommendation['description']
        }
    
    def _generate_javascript_action(self, recommendation: Dict) -> Dict[str, Any]:
        """Generate a JavaScript/TypeScript automation action."""
        action_name = "javascript-automation"
        
        action_yaml = {
            'name': 'JavaScript/TypeScript Automation',
            'description': 'Automated JS/TS building, testing, and quality checks',
            'inputs': {
                'node-version': {
                    'description': 'Node.js version to use',
                    'required': False,
                    'default': '20'
                },
                'package-manager': {
                    'description': 'Package manager (npm, yarn, pnpm)',
                    'required': False,
                    'default': 'npm'
                },
                'run-build': {
                    'description': 'Whether to run build',
                    'required': False,
                    'default': 'true'
                },
                'run-tests': {
                    'description': 'Whether to run tests',
                    'required': False,
                    'default': 'true'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Set up Node.js',
                        'uses': 'actions/setup-node@v4',
                        'with': {
                            'node-version': '${{ inputs.node-version }}'
                        }
                    },
                    {
                        'name': 'Install dependencies',
                        'shell': 'bash',
                        'run': '''
case "${{ inputs.package-manager }}" in
  npm)
    npm ci
    ;;
  yarn)
    yarn install --frozen-lockfile
    ;;
  pnpm)
    pnpm install --frozen-lockfile
    ;;
esac
'''
                    },
                    {
                        'name': 'Run build',
                        'if': "inputs.run-build == 'true'",
                        'shell': 'bash',
                        'run': '${{ inputs.package-manager }} run build'
                    },
                    {
                        'name': 'Run tests',
                        'if': "inputs.run-tests == 'true'",
                        'shell': 'bash',
                        'run': '${{ inputs.package-manager }} test'
                    }
                ]
            }
        }
        
        return {
            'name': action_name,
            'priority': recommendation['priority'],
            'action_yaml': action_yaml,
            'file_path': f'.github/actions/{action_name}/action.yml',
            'description': recommendation['description']
        }
    
    def _generate_testing_action(self, recommendation: Dict) -> Dict[str, Any]:
        """Generate a comprehensive testing action."""
        action_name = "comprehensive-testing"
        
        action_yaml = {
            'name': 'Comprehensive Testing',
            'description': 'Run all tests with coverage reporting',
            'inputs': {
                'test-framework': {
                    'description': 'Testing framework (pytest, jest, unittest)',
                    'required': False,
                    'default': 'auto'
                },
                'coverage-threshold': {
                    'description': 'Minimum coverage percentage',
                    'required': False,
                    'default': '80'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Auto-detect and run tests',
                        'shell': 'bash',
                        'run': '''
# Auto-detect testing framework
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] || command -v pytest &> /dev/null; then
  echo "Running pytest..."
  pytest --cov=. --cov-report=term --cov-report=html
elif [ -f "package.json" ] && grep -q "jest" package.json; then
  echo "Running jest..."
  npm test -- --coverage
elif [ -d "tests/" ] || ls test_*.py 2>/dev/null; then
  echo "Running unittest..."
  python -m unittest discover -v
else
  echo "No test framework detected"
  exit 1
fi
'''
                    },
                    {
                        'name': 'Check coverage threshold',
                        'shell': 'bash',
                        'run': '''
# This is a placeholder for coverage threshold checking
# In real implementation, parse coverage reports
echo "Coverage threshold: ${{ inputs.coverage-threshold }}%"
'''
                    }
                ]
            }
        }
        
        return {
            'name': action_name,
            'priority': recommendation['priority'],
            'action_yaml': action_yaml,
            'file_path': f'.github/actions/{action_name}/action.yml',
            'description': recommendation['description']
        }
    
    def _generate_deployment_action(self, recommendation: Dict, 
                                   deploy_type: str) -> Dict[str, Any]:
        """Generate a deployment action."""
        action_name = f"deploy-{deploy_type}"
        
        if deploy_type == 'docker':
            action_yaml = self._create_docker_deployment_action()
        elif deploy_type == 'npm':
            action_yaml = self._create_npm_deployment_action()
        else:
            action_yaml = self._create_generic_deployment_action(deploy_type)
        
        return {
            'name': action_name,
            'priority': recommendation['priority'],
            'action_yaml': action_yaml,
            'file_path': f'.github/actions/{action_name}/action.yml',
            'description': recommendation['description']
        }
    
    def _create_docker_deployment_action(self) -> Dict:
        """Create Docker deployment action."""
        return {
            'name': 'Docker Deployment',
            'description': 'Build and push Docker images',
            'inputs': {
                'registry': {
                    'description': 'Docker registry',
                    'required': True
                },
                'image-name': {
                    'description': 'Image name',
                    'required': True
                },
                'tag': {
                    'description': 'Image tag',
                    'required': False,
                    'default': 'latest'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Build Docker image',
                        'shell': 'bash',
                        'run': 'docker build -t ${{ inputs.registry }}/${{ inputs.image-name }}:${{ inputs.tag }} .'
                    },
                    {
                        'name': 'Push Docker image',
                        'shell': 'bash',
                        'run': 'docker push ${{ inputs.registry }}/${{ inputs.image-name }}:${{ inputs.tag }}'
                    }
                ]
            }
        }
    
    def _create_npm_deployment_action(self) -> Dict:
        """Create NPM deployment action."""
        return {
            'name': 'NPM Package Deployment',
            'description': 'Build and publish NPM package',
            'inputs': {
                'registry-url': {
                    'description': 'NPM registry URL',
                    'required': False,
                    'default': 'https://registry.npmjs.org'
                },
                'access': {
                    'description': 'Package access level',
                    'required': False,
                    'default': 'public'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Build package',
                        'shell': 'bash',
                        'run': 'npm run build'
                    },
                    {
                        'name': 'Publish to NPM',
                        'shell': 'bash',
                        'run': 'npm publish --access ${{ inputs.access }}'
                    }
                ]
            }
        }
    
    def _create_generic_deployment_action(self, deploy_type: str) -> Dict:
        """Create generic deployment action."""
        return {
            'name': f'{deploy_type.title()} Deployment',
            'description': f'Deploy using {deploy_type}',
            'inputs': {
                'environment': {
                    'description': 'Deployment environment',
                    'required': False,
                    'default': 'production'
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': f'Deploy to {deploy_type}',
                        'shell': 'bash',
                        'run': f'echo "Deploy to {deploy_type} - ${{{{ inputs.environment }}}}"'
                    }
                ]
            }
        }
    
    def _generate_repeated_operation_action(self, recommendation: Dict) -> Dict[str, Any]:
        """Generate action for repeated operations."""
        pattern = recommendation.get('pattern', 'operation')
        # Clean up pattern name for use as action name
        action_name = pattern.replace('_', '-').replace(' ', '-').lower()
        # Ensure uniqueness by including pattern in name
        if not action_name.startswith('reusable-'):
            action_name = f'reusable-{action_name}'
        
        action_yaml = {
            'name': f'Automated {pattern.replace("_", " ").title()}',
            'description': f'Reusable action for {pattern} operations',
            'inputs': {
                'options': {
                    'description': 'Additional options',
                    'required': False,
                    'default': ''
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': f'Execute {pattern}',
                        'shell': 'bash',
                        'run': f'echo "Executing {pattern} with options: ${{{{ inputs.options }}}}"'
                    }
                ]
            }
        }
        
        return {
            'name': action_name,
            'priority': recommendation['priority'],
            'action_yaml': action_yaml,
            'file_path': f'.github/actions/{action_name}/action.yml',
            'description': recommendation['description']
        }
    
    def _generate_generic_action(self, recommendation: Dict) -> Dict[str, Any]:
        """Generate a generic action."""
        action_name = "custom-automation"
        
        action_yaml = {
            'name': 'Custom Automation',
            'description': recommendation.get('description', 'Custom automated action'),
            'inputs': {
                'command': {
                    'description': 'Command to execute',
                    'required': True
                }
            },
            'runs': {
                'using': 'composite',
                'steps': [
                    {
                        'name': 'Execute command',
                        'shell': 'bash',
                        'run': '${{ inputs.command }}'
                    }
                ]
            }
        }
        
        return {
            'name': action_name,
            'priority': recommendation['priority'],
            'action_yaml': action_yaml,
            'file_path': f'.github/actions/{action_name}/action.yml',
            'description': recommendation['description']
        }
    
    def save_actions(self, output_dir: str = ".github/actions") -> List[str]:
        """
        Save generated actions to files.
        
        Returns:
            List of created file paths.
        """
        if not self.generated_actions:
            self.generate_actions()
        
        created_files = []
        output_path = Path(output_dir)
        
        for action in self.generated_actions:
            # Extract just the action name from the file path
            action_name = action['name']
            # Create file path relative to output_dir
            file_path = output_path / action_name / 'action.yml'
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write action YAML
            with open(file_path, 'w') as f:
                yaml.dump(action['action_yaml'], f, 
                         default_flow_style=False, sort_keys=False)
            
            created_files.append(str(file_path))
            print(f"  ✅ Created action: {file_path}")
        
        # Create summary
        summary_path = output_path / 'GENERATED_ACTIONS.md'
        self._create_summary(summary_path)
        created_files.append(str(summary_path))
        
        print(f"\n💾 Saved {len(created_files)} files.")
        return created_files
    
    def _create_summary(self, summary_path: Path):
        """Create a summary document of generated actions."""
        content = [
            "# Generated GitHub Actions",
            "",
            f"**Generated by:** @engineer-master",
            f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Actions Created",
            ""
        ]
        
        for i, action in enumerate(self.generated_actions, 1):
            content.append(f"### {i}. {action['name']}")
            content.append(f"**Priority:** {action['priority']}")
            content.append(f"**File:** `{action['file_path']}`")
            content.append(f"**Description:** {action['description']}")
            content.append("")
        
        content.append("## Usage")
        content.append("")
        content.append("To use these actions in your workflows:")
        content.append("")
        content.append("```yaml")
        content.append("- name: Use custom action")
        content.append("  uses: ./.github/actions/action-name")
        content.append("  with:")
        content.append("    # action inputs here")
        content.append("```")
        content.append("")
        content.append("---")
        content.append("*Generated by the Chained autonomous AI ecosystem*")
        
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, 'w') as f:
            f.write('\n'.join(content))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate custom GitHub Actions from analysis'
    )
    parser.add_argument(
        '--analysis',
        default='analysis/actions-patterns.json',
        help='Path to analysis JSON file'
    )
    parser.add_argument(
        '--output-dir',
        default='.github/actions',
        help='Output directory for actions'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate but do not save actions'
    )
    
    args = parser.parse_args()
    
    # Load analysis
    with open(args.analysis, 'r') as f:
        analysis_data = json.load(f)
    
    generator = ActionsGenerator(analysis_data)
    actions = generator.generate_actions()
    
    if not args.dry_run:
        created_files = generator.save_actions(args.output_dir)
        print(f"\n✅ Generated {len(actions)} custom GitHub Actions!")
    else:
        print(f"\n🔍 Dry run: Would generate {len(actions)} actions")
        for action in actions:
            print(f"  - {action['name']} ({action['priority']} priority)")


if __name__ == '__main__':
    main()
