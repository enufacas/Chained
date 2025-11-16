#!/usr/bin/env python3
"""
Secure CI/CD Pipeline Generator
Mission ID: idea:15 - DevOps: Cloud Innovation
Author: @cloud-architect
Date: 2025-11-16

Generates secure CI/CD pipeline configurations with built-in security gates.
"""

import argparse
import json
import yaml
from typing import Dict, List, Any

class SecureCICDGenerator:
    """Generate secure CI/CD pipeline configurations"""
    
    def __init__(self):
        self.security_tools = {
            'secret_scanning': ['trufflehog', 'git-secrets', 'gitleaks'],
            'sast': ['semgrep', 'bandit', 'sonarqube'],
            'sca': ['snyk', 'dependabot', 'safety'],
            'container_scanning': ['trivy', 'clair', 'anchore'],
            'iac_scanning': ['tfsec', 'checkov', 'terrascan'],
            'dast': ['zap', 'burp', 'w3af'],
            'policy': ['opa', 'kyverno', 'gatekeeper']
        }
    
    def generate_github_actions(self, 
                                project_type: str = 'python',
                                security_level: str = 'high') -> str:
        """
        Generate GitHub Actions workflow with security gates
        
        Args:
            project_type: Type of project (python, node, go, etc.)
            security_level: Security level (basic, medium, high, paranoid)
        
        Returns:
            YAML string for GitHub Actions workflow
        """
        workflow = {
            'name': 'Secure CI/CD Pipeline',
            'on': {
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main']}
            },
            'env': {
                'SECURITY_LEVEL': security_level
            },
            'jobs': {}
        }
        
        # Add security scan job
        workflow['jobs']['security-scan'] = self._create_security_scan_job(
            project_type, security_level
        )
        
        # Add build job
        workflow['jobs']['build'] = self._create_build_job(project_type)
        
        # Add deploy job (only on main branch)
        workflow['jobs']['deploy'] = self._create_deploy_job(project_type)
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _create_security_scan_job(self, project_type: str, security_level: str) -> Dict:
        """Create comprehensive security scanning job"""
        job = {
            'runs-on': 'ubuntu-latest',
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v3',
                    'with': {'fetch-depth': 0}  # Full history for better analysis
                }
            ]
        }
        
        # 1. Secret scanning
        job['steps'].append({
            'name': 'Run TruffleHog (Secret Scanning)',
            'uses': 'trufflesecurity/trufflehog@main',
            'with': {
                'path': './',
                'base': '${{ github.event.repository.default_branch }}',
                'head': 'HEAD'
            }
        })
        
        # 2. SAST scanning
        if security_level in ['high', 'paranoid']:
            job['steps'].append({
                'name': 'Run Semgrep (SAST)',
                'uses': 'returntocorp/semgrep-action@v1',
                'with': {
                    'config': 'p/security-audit p/owasp-top-ten p/secrets'
                }
            })
        
        # 3. Dependency scanning
        if project_type == 'python':
            job['steps'].extend([
                {
                    'name': 'Set up Python',
                    'uses': 'actions/setup-python@v4',
                    'with': {'python-version': '3.11'}
                },
                {
                    'name': 'Install dependencies',
                    'run': 'pip install safety pip-audit'
                },
                {
                    'name': 'Run Safety check',
                    'run': 'safety check --json || true'
                },
                {
                    'name': 'Run pip-audit',
                    'run': 'pip-audit || true'
                }
            ])
        elif project_type == 'node':
            job['steps'].extend([
                {
                    'name': 'Set up Node.js',
                    'uses': 'actions/setup-node@v3',
                    'with': {'node-version': '18'}
                },
                {
                    'name': 'Run npm audit',
                    'run': 'npm audit --audit-level=moderate'
                },
                {
                    'name': 'Run Snyk',
                    'uses': 'snyk/actions/node@master',
                    'env': {'SNYK_TOKEN': '${{ secrets.SNYK_TOKEN }}'}
                }
            ])
        
        # 4. Container scanning (if Dockerfile exists)
        job['steps'].append({
            'name': 'Build and scan Docker image',
            'if': "hashFiles('Dockerfile') != ''",
            'run': '''
                docker build -t temp-image:${{ github.sha }} .
                docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                  aquasec/trivy image --severity HIGH,CRITICAL \\
                  --exit-code 1 temp-image:${{ github.sha }}
            '''
        })
        
        # 5. IaC scanning (if terraform exists)
        if security_level in ['high', 'paranoid']:
            job['steps'].append({
                'name': 'Run tfsec (IaC Scanning)',
                'if': "hashFiles('**/*.tf') != ''",
                'uses': 'aquasecurity/tfsec-action@v1.0.0',
                'with': {
                    'soft_fail': 'false'
                }
            })
        
        return job
    
    def _create_build_job(self, project_type: str) -> Dict:
        """Create build and test job"""
        job = {
            'needs': ['security-scan'],
            'runs-on': 'ubuntu-latest',
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v3'
                }
            ]
        }
        
        if project_type == 'python':
            job['steps'].extend([
                {
                    'name': 'Set up Python',
                    'uses': 'actions/setup-python@v4',
                    'with': {'python-version': '3.11'}
                },
                {
                    'name': 'Install dependencies',
                    'run': 'pip install -r requirements.txt'
                },
                {
                    'name': 'Run tests',
                    'run': 'pytest --cov --cov-report=xml'
                },
                {
                    'name': 'Upload coverage',
                    'uses': 'codecov/codecov-action@v3'
                }
            ])
        elif project_type == 'node':
            job['steps'].extend([
                {
                    'name': 'Set up Node.js',
                    'uses': 'actions/setup-node@v3',
                    'with': {'node-version': '18'}
                },
                {
                    'name': 'Install dependencies',
                    'run': 'npm ci'
                },
                {
                    'name': 'Run tests',
                    'run': 'npm test'
                },
                {
                    'name': 'Build',
                    'run': 'npm run build'
                }
            ])
        
        return job
    
    def _create_deploy_job(self, project_type: str) -> Dict:
        """Create deployment job"""
        return {
            'needs': ['build'],
            'runs-on': 'ubuntu-latest',
            'if': "github.ref == 'refs/heads/main'",
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v3'
                },
                {
                    'name': 'Deploy to production',
                    'run': '''
                        echo "Deploying with security validation..."
                        # Add deployment commands here
                    '''
                }
            ]
        }
    
    def generate_gitlab_ci(self, project_type: str = 'python') -> str:
        """Generate GitLab CI configuration"""
        config = {
            'stages': ['security', 'build', 'test', 'deploy'],
            'variables': {
                'DOCKER_DRIVER': 'overlay2',
                'SECURITY_LEVEL': 'high'
            },
            'security:secrets': {
                'stage': 'security',
                'image': 'trufflesecurity/trufflehog:latest',
                'script': [
                    'trufflehog filesystem --directory=. --json'
                ]
            },
            'security:sast': {
                'stage': 'security',
                'image': 'returntocorp/semgrep:latest',
                'script': [
                    'semgrep --config="p/security-audit" --config="p/owasp-top-ten" .'
                ]
            }
        }
        
        if project_type == 'python':
            config['security:dependencies'] = {
                'stage': 'security',
                'image': 'python:3.11',
                'script': [
                    'pip install safety pip-audit',
                    'safety check',
                    'pip-audit'
                ]
            }
            config['build'] = {
                'stage': 'build',
                'image': 'python:3.11',
                'script': [
                    'pip install -r requirements.txt',
                    'python -m pytest'
                ]
            }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def generate_security_policy_opa(self) -> str:
        """Generate OPA (Open Policy Agent) security policy"""
        policy = '''# Kubernetes Security Policy
# Author: @cloud-architect
# Mission: idea:15

package kubernetes.admission

# Deny containers running as root
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container %v must run as non-root user", [container.name])
}

# Require resource limits
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container %v must have memory limits", [container.name])
}

# Deny privileged containers
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged
    msg := sprintf("Container %v cannot run in privileged mode", [container.name])
}

# Require image scanning
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.image_scanned
    msg := sprintf("Container %v must use scanned image", [container.name])
}
'''
        return policy


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate secure CI/CD pipeline configurations'
    )
    parser.add_argument(
        '--platform',
        choices=['github', 'gitlab', 'opa'],
        default='github',
        help='CI/CD platform to generate for'
    )
    parser.add_argument(
        '--project-type',
        choices=['python', 'node', 'go', 'java'],
        default='python',
        help='Type of project'
    )
    parser.add_argument(
        '--security-level',
        choices=['basic', 'medium', 'high', 'paranoid'],
        default='high',
        help='Security level for scanning'
    )
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    generator = SecureCICDGenerator()
    
    # Generate configuration
    if args.platform == 'github':
        config = generator.generate_github_actions(
            args.project_type,
            args.security_level
        )
    elif args.platform == 'gitlab':
        config = generator.generate_gitlab_ci(args.project_type)
    elif args.platform == 'opa':
        config = generator.generate_security_policy_opa()
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(config)
        print(f"✅ Generated secure CI/CD configuration: {args.output}")
    else:
        print(config)


if __name__ == '__main__':
    main()
