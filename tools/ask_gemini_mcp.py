#!/usr/bin/env python3
"""
Ask Gemini with MCP Server Support

This enhanced version of ask_gemini can optionally use MCP (Model Context Protocol)
servers to give Gemini direct repository access, just like the workflows do.

**Two Modes:**
1. **API Mode** (default): Simple API call, requires manual context gathering
2. **MCP Mode** (enhanced): Uses Gemini CLI with GitHub MCP server for full repo access

Usage:
    # Simple API mode (existing behavior)
    python3 ask_gemini_mcp.py "How to fix this bug?"
    
    # MCP mode with full repository access (like workflows)
    python3 ask_gemini_mcp.py --mcp "How to fix this bug?"
    
    # Python API
    from tools.ask_gemini_mcp import ask_gemini_with_mcp
    
    response = ask_gemini_with_mcp(
        question="Fix the auth bug",
        use_mcp=True  # Enable GitHub MCP server
    )

Requirements for MCP Mode:
    - Docker installed and running
    - npm/npx available (for @google/generative-ai-cli)
    - GITHUB_TOKEN environment variable set

Author: Enhanced by investigation of gemini-invoke.yml workflow
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Import the original ask_gemini for API mode
sys.path.insert(0, str(Path(__file__).parent))
from ask_gemini import ask_gemini, ask_gemini_fix_code


def check_mcp_requirements():
    """
    Check if MCP mode requirements are met.
    
    Returns:
        tuple: (bool, str) - (requirements_met, error_message)
    """
    errors = []
    
    # Check Docker
    try:
        subprocess.run(['docker', '--version'], 
                      capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        errors.append("Docker not found or not running")
    
    # Check npx
    try:
        subprocess.run(['npx', '--version'], 
                      capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        errors.append("npx not found (install Node.js)")
    
    # Check GITHUB_TOKEN
    if not os.getenv('GITHUB_TOKEN'):
        errors.append("GITHUB_TOKEN environment variable not set")
    
    if errors:
        return False, "\n".join(f"  • {err}" for err in errors)
    
    return True, ""


def create_mcp_config(github_token):
    """
    Create MCP configuration matching gemini-invoke.yml workflow.
    
    Args:
        github_token: GitHub personal access token
        
    Returns:
        dict: MCP configuration
    """
    return {
        "model": {
            "maxSessionTurns": 25
        },
        "mcpServers": {
            "github": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "ghcr.io/github/github-mcp-server:v0.18.0"
                ],
                "includeTools": [
                    "get_file_contents",
                    "search_code",
                    "list_commits",
                    "get_commit",
                    "create_or_update_file",
                    "delete_file",
                    "push_files"
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": github_token
                }
            }
        },
        "tools": {
            "core": [
                "run_shell_command(cat)",
                "run_shell_command(echo)",
                "run_shell_command(grep)",
                "run_shell_command(head)",
                "run_shell_command(tail)",
                "run_shell_command(git)"
            ]
        }
    }


def ask_gemini_with_mcp(
    question: str,
    use_mcp: bool = False,
    repo_context: str = None,
    model: str = "gemini-3-pro-preview"
):
    """
    Consult Gemini with optional MCP server support.
    
    Args:
        question: The question to ask Gemini
        use_mcp: If True, use MCP mode with GitHub server access
        repo_context: Optional repository context (owner/repo format)
        model: Gemini model to use
        
    Returns:
        str: Gemini's response
        
    Raises:
        RuntimeError: If MCP requirements not met or execution fails
    """
    if not use_mcp:
        # Fall back to simple API mode
        return ask_gemini(question, model=model)
    
    # MCP Mode - use Gemini CLI with GitHub MCP server
    print("🔧 MCP Mode: Gemini will have direct repository access", file=sys.stderr)
    
    # Check requirements
    ok, error = check_mcp_requirements()
    if not ok:
        raise RuntimeError(
            f"MCP mode requirements not met:\n{error}\n\n"
            "To use MCP mode, ensure:\n"
            "  1. Docker is installed and running\n"
            "  2. Node.js/npm is installed (for Gemini CLI)\n"
            "  3. GITHUB_TOKEN is set: export GITHUB_TOKEN=your_token\n\n"
            "Falling back to API mode is not automatic. Use use_mcp=False."
        )
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    
    # Create MCP configuration
    config = create_mcp_config(github_token)
    
    # Add repo context if provided
    if repo_context:
        question = f"Repository: {repo_context}\n\n{question}"
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        config_file = f.name
    
    try:
        print(f"📋 Using MCP config: {config_file}", file=sys.stderr)
        print("🚀 Launching Gemini CLI with GitHub MCP server...", file=sys.stderr)
        
        # Use Gemini CLI via npx
        # The CLI will use the MCP config and have full repo access
        cmd = [
            'npx',
            '--yes',  # Auto-install if needed
            '@google/generative-ai-cli@latest',
            '--config', config_file,
            '--model', model,
            '--prompt', question
        ]
        
        # Set API key
        env = os.environ.copy()
        if os.getenv('GEMINI_API_KEY'):
            env['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
        elif os.getenv('GOOGLE_API_KEY'):
            env['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
        else:
            raise RuntimeError(
                "No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
            )
        
        # Run Gemini CLI
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Gemini CLI failed:\n{result.stderr}"
            )
        
        print("✅ Gemini CLI execution complete", file=sys.stderr)
        return result.stdout
        
    finally:
        # Clean up temp config
        try:
            os.unlink(config_file)
        except Exception:
            pass


def main():
    """CLI entry point with MCP support."""
    parser = argparse.ArgumentParser(
        description="Ask Gemini with optional MCP server support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple API mode (existing behavior)
  python3 ask_gemini_mcp.py "How to fix auth bug?"
  
  # MCP mode with full repository access (like workflows!)
  python3 ask_gemini_mcp.py --mcp "How to fix auth bug?"
  
  # MCP mode with repo context
  python3 ask_gemini_mcp.py --mcp --repo enufacas/Chained "Fix issue #123"

MCP Mode vs API Mode:
  API Mode (default):
    - Simple Gemini API call
    - No repository access
    - Requires manual context gathering
    - Fast and lightweight
    
  MCP Mode (--mcp flag):
    - Uses Gemini CLI with GitHub MCP server
    - Full repository access (like workflows!)
    - Can read files, search code, check history
    - Requires Docker, npx, GITHUB_TOKEN
    - Slightly slower due to setup

Requirements for MCP Mode:
  - Docker installed and running
  - Node.js/npm installed
  - GITHUB_TOKEN environment variable set
  - export GITHUB_TOKEN=ghp_your_token_here
        """
    )
    
    parser.add_argument(
        'question',
        help='Question to ask Gemini'
    )
    parser.add_argument(
        '--mcp',
        action='store_true',
        help='Enable MCP mode with GitHub server access (like workflows)'
    )
    parser.add_argument(
        '--repo',
        help='Repository context in owner/repo format (for MCP mode)'
    )
    parser.add_argument(
        '-m', '--model',
        default='gemini-3-pro-preview',
        help='Gemini model to use'
    )
    
    args = parser.parse_args()
    
    try:
        response = ask_gemini_with_mcp(
            question=args.question,
            use_mcp=args.mcp,
            repo_context=args.repo,
            model=args.model
        )
        
        print("\n✅ Gemini's Response:\n")
        print(response)
        return 0
        
    except RuntimeError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
