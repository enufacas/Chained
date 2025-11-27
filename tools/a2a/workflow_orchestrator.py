"""
A2A Workflow Orchestrator for GitHub Actions.

This module provides A2A protocol-compliant orchestration for Gemini CLI
invocations in GitHub Actions workflows. It handles the ENTIRE task lifecycle
in a single invocation, minimizing workflow steps.

DESIGN PHILOSOPHY:
==================
The A2A "Life of a Task" maps cleanly to GitHub Actions:

    A2A Concept          | GitHub Actions Equivalent
    ---------------------|---------------------------
    Task                 | Job (bounded execution context)
    Artifact             | GitHub Artifact (persistent output)
    contextId            | Workflow run ID + issue number
    referenceTaskIds     | Artifact names from previous jobs
    Task transitions     | Job success/failure + artifact upload

ARCHITECTURE:
=============
Instead of many small steps, we use:

1. **Single Analysis Step**: 
   - Creates tasks in 'submitted' state
   - Wraps Gemini CLI execution 
   - Captures output as A2A Artifact
   - Uploads as GitHub Artifact for cross-job access

2. **Single Implementation Step**:
   - Downloads analysis artifacts from GitHub
   - Creates implementation task with referenceTaskIds
   - Wraps Gemini CLI execution
   - Uploads PR result as artifact

PARALLEL JOB SUPPORT:
====================
For parallel agent execution, each agent can run as a separate job:

    Job: agent-1-analysis     Job: agent-2-analysis
           ↓                          ↓
    [Upload Artifact]          [Upload Artifact]
           ↓                          ↓
           └──────────┬───────────────┘
                      ↓
           Job: aggregate-and-implement
                      ↓
           [Download All Artifacts]
                      ↓
           [Create Implementation Task with referenceTaskIds]

Usage:
    # Complete analysis lifecycle (single step)
    python -m tools.a2a.workflow_orchestrator \\
        --lifecycle analysis \\
        --issue-number 123 \\
        --run-id abc123 \\
        --agents "agent1,agent2" \\
        --gemini-output-dir gemini-artifacts/

    # Complete implementation lifecycle (single step)  
    python -m tools.a2a.workflow_orchestrator \\
        --lifecycle implementation \\
        --issue-number 123 \\
        --run-id abc123 \\
        --analysis-artifact analysis-artifact.json

Per A2A Protocol:
- https://a2a-protocol.org/latest/topics/life-of-a-task/
- https://a2a-protocol.org/latest/topics/streaming-and-async/
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add repo root to path when run as `python -m tools.a2a.workflow_orchestrator`
# This is needed because we import from tools.a2a.task which is a sibling module
_repo_root = Path(__file__).parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

try:
    from tools.a2a.task import (
        Artifact,
        Task,
        TaskStore,
        create_analysis_task,
        create_implementation_task,
        aggregate_artifacts,
    )
except ImportError as e:
    # Provide helpful error if imports fail
    print(f"Error importing A2A task module: {e}", file=sys.stderr)
    print(f"Ensure you're running from the repo root: python -m tools.a2a.workflow_orchestrator", file=sys.stderr)
    sys.exit(1)


# =============================================================================
# GITHUB ARTIFACT FORMAT
# =============================================================================

def create_github_artifact(
    artifact_name: str,
    artifact_type: str,
    context_id: str,
    task_ids: List[str],
    content: Any,
    reference_task_ids: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a GitHub-Artifact-compatible JSON structure.
    
    This format is designed to be:
    1. Self-describing (contains its own metadata)
    2. Linkable (via contextId and taskIds per A2A spec)
    3. Portable (can be uploaded/downloaded across jobs)
    """
    return {
        "a2a_version": "0.3.0",
        "artifact_name": artifact_name,
        "artifact_type": artifact_type,
        "context_id": context_id,
        "task_ids": task_ids,
        "reference_task_ids": reference_task_ids or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content,
        "metadata": metadata or {},
    }


# =============================================================================
# CONSOLIDATED LIFECYCLE HANDLERS
# =============================================================================

def handle_analysis_lifecycle(
    issue_number: int,
    run_id: str,
    agents: List[str],
    gemini_output_dir: Path,
    output_artifact_path: Path,
) -> Dict[str, Any]:
    """
    Handle the COMPLETE analysis lifecycle in a single call.
    
    This consolidates what was previously 4-5 steps into ONE:
    1. Create tasks (submitted state)
    2. [Gemini CLI runs externally - output saved to gemini_output_dir]
    3. Capture output (working → completed)
    4. Package as GitHub Artifact
    
    The output file can be uploaded with actions/upload-artifact.
    
    Args:
        issue_number: GitHub issue number
        run_id: Workflow run ID  
        agents: List of agent names
        gemini_output_dir: Path to gemini-artifacts/ directory
        output_artifact_path: Where to write the artifact JSON
        
    Returns:
        The artifact data (also written to output_artifact_path)
    """
    context_id = f"issue-{issue_number}"
    store = TaskStore()  # In-memory for this lifecycle
    
    print("=" * 60)
    print("A2A ANALYSIS LIFECYCLE (Consolidated)")
    print("=" * 60)
    print(f"Issue: #{issue_number}")
    print(f"Context ID: {context_id}")
    print(f"Agents: {', '.join(agents)}")
    print()
    
    # 1. Create tasks in submitted state
    tasks = []
    for agent_name in agents:
        task = create_analysis_task(
            issue_number=issue_number,
            agent_name=agent_name,
            run_id=run_id,
            context_id=context_id,
        )
        tasks.append(task)
        store.store(task)
        print(f"[Task] Created {task.id} for @{agent_name} (submitted)")
    
    # 2. Read Gemini output from filesystem
    analysis_content = _read_gemini_output(gemini_output_dir)
    
    # 3. Transition tasks: submitted → working → completed
    for task in tasks:
        task.set_working(f"Processing analysis for issue #{issue_number}")
        
        artifact = task.add_text_artifact(
            name=f"{task.agent_name}-analysis",
            text=analysis_content,
            description=f"Analysis from {task.agent_name}",
        )
        
        task.complete("Analysis complete")
        store.store(task)
        print(f"[Task] {task.id} completed with artifact {artifact.artifact_id}")
    
    # 4. Package as GitHub Artifact
    task_ids = [t.id for t in tasks]
    
    artifact_data = create_github_artifact(
        artifact_name=f"analysis-{issue_number}",
        artifact_type="analysis",
        context_id=context_id,
        task_ids=task_ids,
        content={
            "agents": agents,
            "full_analysis": analysis_content,
            "tasks": [t.to_dict() for t in tasks],
        },
        metadata={
            "issue_number": issue_number,
            "run_id": run_id,
            "agent_count": len(agents),
        },
    )
    
    # Write artifact file for GitHub Artifact upload
    try:
        output_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, indent=2)
    except (OSError, IOError) as e:
        print(f"[Artifact] Error writing to {output_artifact_path}: {e}")
        raise
    
    print()
    print(f"[Artifact] Written to {output_artifact_path}")
    print(f"[Artifact] Upload with: actions/upload-artifact@v4")
    print("=" * 60)
    
    # Set GitHub Actions outputs
    _set_github_output("context_id", context_id)
    _set_github_output("task_ids", ",".join(task_ids))
    _set_github_output("artifact_path", str(output_artifact_path))
    _set_github_output("analysis_length", str(len(analysis_content)))
    
    return artifact_data


def handle_implementation_lifecycle(
    issue_number: int,
    run_id: str,
    analysis_artifact_path: Path,
    gemini_output_dir: Path,
    output_artifact_path: Path,
    branch_name: Optional[str] = None,
    pr_number: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Handle the COMPLETE implementation lifecycle in a single call.
    
    This:
    1. Loads analysis artifact (from previous job via actions/download-artifact)
    2. Creates implementation task with referenceTaskIds linking to analysis
    3. [Gemini CLI runs externally]
    4. Captures PR creation result
    5. Packages as final artifact
    
    Args:
        issue_number: GitHub issue number
        run_id: Workflow run ID
        analysis_artifact_path: Path to downloaded analysis artifact
        gemini_output_dir: Path to gemini-artifacts/ directory  
        output_artifact_path: Where to write the result artifact
        branch_name: Branch created (if any)
        pr_number: PR number created (if any)
        
    Returns:
        The artifact data
    """
    context_id = f"issue-{issue_number}"
    
    print("=" * 60)
    print("A2A IMPLEMENTATION LIFECYCLE (Consolidated)")
    print("=" * 60)
    print(f"Issue: #{issue_number}")
    print(f"Context ID: {context_id}")
    print()
    
    # 1. Load analysis artifact (from previous job)
    reference_task_ids = []
    analysis_content = ""
    
    if analysis_artifact_path.exists():
        with open(analysis_artifact_path) as f:
            analysis_data = json.load(f)
        
        reference_task_ids = analysis_data.get("task_ids", [])
        analysis_content = analysis_data.get("content", {}).get("full_analysis", "")
        
        print(f"[Input] Loaded {len(reference_task_ids)} reference tasks from previous job")
        print(f"[Input] Analysis: {len(analysis_content)} chars")
    else:
        print(f"[Input] Warning: Analysis artifact not found at {analysis_artifact_path}")
    
    # 2. Create implementation task with referenceTaskIds
    # Per A2A "Life of a Task": referenceTaskIds link follow-up to predecessors
    impl_task = create_implementation_task(
        issue_number=issue_number,
        run_id=run_id,
        reference_task_ids=reference_task_ids,
        context_id=context_id,
    )
    
    print(f"[Task] Created {impl_task.id}")
    print(f"[Task] References: {reference_task_ids}")
    
    # 3. Transition: submitted → working
    impl_task.set_working("Implementing changes")
    
    # 4. Read implementation output
    impl_output = _read_gemini_output(gemini_output_dir)
    
    # 5. Complete task based on result
    impl_task.add_json_artifact(
        name="implementation-result",
        data={
            "branch_name": branch_name,
            "pr_number": pr_number,
            "output_preview": impl_output[:500] if impl_output else None,
        },
        description="Implementation result",
    )
    
    if pr_number:
        impl_task.complete(f"PR #{pr_number} created")
        status = "completed"
    elif branch_name:
        impl_task.complete(f"Branch {branch_name} created")
        status = "completed"  
    else:
        impl_task.fail("No PR or branch created")
        status = "failed"
    
    print(f"[Task] {impl_task.id} → {status}")
    
    # 6. Package as GitHub Artifact
    artifact_data = create_github_artifact(
        artifact_name=f"implementation-{issue_number}",
        artifact_type="implementation",
        context_id=context_id,
        task_ids=[impl_task.id],
        reference_task_ids=reference_task_ids,
        content={
            "task": impl_task.to_dict(),
            "branch_name": branch_name,
            "pr_number": pr_number,
        },
        metadata={
            "issue_number": issue_number,
            "run_id": run_id,
        },
    )
    
    try:
        output_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, indent=2)
    except (OSError, IOError) as e:
        print(f"[Artifact] Error writing to {output_artifact_path}: {e}")
        raise
    
    print()
    print(f"[Artifact] Written to {output_artifact_path}")
    print("=" * 60)
    
    # Set GitHub Actions outputs
    _set_github_output("task_id", impl_task.id)
    _set_github_output("status", status)
    _set_github_output("artifact_path", str(output_artifact_path))
    
    return artifact_data


def prepare_execution_context(
    analysis_artifact_path: Path,
    context_output_path: Path,
    issue_number: int,
) -> str:
    """
    Prepare implementation context from analysis artifact.
    
    Creates the context file that Gemini CLI will read
    to understand what to implement.
    
    Args:
        analysis_artifact_path: Path to analysis artifact
        context_output_path: Where to write the context
        issue_number: GitHub issue number
        
    Returns:
        Path to context file
    """
    # Load analysis artifact
    if analysis_artifact_path.exists():
        with open(analysis_artifact_path) as f:
            artifact = json.load(f)
        
        context_id = artifact.get("context_id", f"issue-{issue_number}")
        task_ids = artifact.get("task_ids", [])
        analysis = artifact.get("content", {}).get("full_analysis", "")
        agents = artifact.get("content", {}).get("agents", [])
    else:
        context_id = f"issue-{issue_number}"
        task_ids = []
        analysis = ""
        agents = []
    
    # Build context document
    context = f"""# A2A Implementation Task

## Task Linking (per "Life of a Task")
- **contextId**: {context_id}
- **referenceTaskIds**: {', '.join(task_ids)}

## Agents Who Analyzed
{', '.join(f'@{a}' for a in agents)}

## Analysis Artifacts

{analysis}

## Instructions

Implement the changes recommended above and create a PR.
Use "Fixes #{issue_number}" in the PR body.
"""
    
    try:
        context_output_path.parent.mkdir(parents=True, exist_ok=True)
        context_output_path.write_text(context, encoding="utf-8")
        print(f"[Context] Written to {context_output_path}")
    except (OSError, IOError) as e:
        print(f"[Context] Error writing to {context_output_path}: {e}")
        raise
    
    _set_github_output("context_path", str(context_output_path))
    
    return str(context_output_path)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _read_gemini_output(gemini_output_dir: Path) -> str:
    """Read Gemini output from the artifacts directory."""
    gemini_output_dir = Path(gemini_output_dir)
    
    if not gemini_output_dir.exists():
        print(f"[Output] Warning: Directory not found: {gemini_output_dir}")
        return ""
    
    # Look for known output files
    for candidate in ["response.md", "stdout.log"]:
        output_file = gemini_output_dir / candidate
        if output_file.exists():
            try:
                content = output_file.read_text(encoding="utf-8")
                print(f"[Output] Read {len(content)} chars from {output_file}")
                return content
            except (OSError, IOError, UnicodeDecodeError) as e:
                print(f"[Output] Error reading {output_file}: {e}")
                continue
    
    # Try any file with content
    try:
        for f in gemini_output_dir.iterdir():
            if f.is_file() and f.stat().st_size > 0:
                try:
                    content = f.read_text(encoding="utf-8")
                    print(f"[Output] Read {len(content)} chars from {f}")
                    return content
                except (UnicodeDecodeError, OSError) as e:
                    print(f"[Output] Skipping {f}: {e}")
                    continue
    except OSError as e:
        print(f"[Output] Error iterating directory: {e}")
    
    print("[Output] Warning: No Gemini output found")
    return ""


def _set_github_output(name: str, value: str) -> None:
    """Set a GitHub Actions output variable."""
    if os.environ.get("GITHUB_OUTPUT"):
        try:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                f.write(f"{name}={value}\n")
        except (OSError, IOError) as e:
            print(f"[Output] Warning: Failed to set {name}: {e}")


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """CLI entry point for workflow orchestration."""
    parser = argparse.ArgumentParser(
        description="A2A Workflow Orchestrator - Consolidated Lifecycle Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Complete analysis lifecycle (replaces 4-5 separate steps)
  python -m tools.a2a.workflow_orchestrator \\
      --lifecycle analysis \\
      --issue-number 123 \\
      --run-id abc123 \\
      --agents "engineer-master,secure-specialist" \\
      --gemini-output-dir gemini-artifacts/ \\
      --output-artifact .a2a/artifacts/analysis.json

  # Complete implementation lifecycle
  python -m tools.a2a.workflow_orchestrator \\
      --lifecycle implementation \\
      --issue-number 123 \\
      --run-id abc123 \\
      --analysis-artifact .a2a/artifacts/analysis.json \\
      --gemini-output-dir gemini-artifacts/ \\
      --output-artifact .a2a/artifacts/implementation.json \\
      --pr-number 456

  # Prepare context for Gemini CLI
  python -m tools.a2a.workflow_orchestrator \\
      --lifecycle prepare-context \\
      --issue-number 123 \\
      --analysis-artifact .a2a/artifacts/analysis.json \\
      --context-output .a2a/context/implementation.md
        """
    )
    
    parser.add_argument(
        "--lifecycle",
        required=True,
        choices=["analysis", "implementation", "prepare-context"],
        help="Which lifecycle phase to handle",
    )
    parser.add_argument(
        "--issue-number",
        type=int,
        required=True,
        help="GitHub issue number",
    )
    parser.add_argument(
        "--run-id",
        default="local",
        help="Workflow run ID",
    )
    parser.add_argument(
        "--agents",
        help="Comma-separated list of agent names (for analysis)",
    )
    parser.add_argument(
        "--gemini-output-dir",
        type=Path,
        default=Path("gemini-artifacts"),
        help="Path to Gemini output directory",
    )
    parser.add_argument(
        "--analysis-artifact",
        type=Path,
        help="Path to analysis artifact (for implementation/prepare-context)",
    )
    parser.add_argument(
        "--output-artifact",
        type=Path,
        default=Path(".a2a/artifacts/output.json"),
        help="Where to write the output artifact",
    )
    parser.add_argument(
        "--context-output",
        type=Path,
        default=Path(".a2a/context/implementation.md"),
        help="Where to write the context file (for prepare-context)",
    )
    parser.add_argument(
        "--branch-name",
        help="Branch name created (for implementation)",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        help="PR number created (for implementation)",
    )
    
    args = parser.parse_args()
    
    if args.lifecycle == "analysis":
        if not args.agents:
            parser.error("--agents is required for analysis lifecycle")
        
        agents = [a.strip() for a in args.agents.split(",") if a.strip()]
        handle_analysis_lifecycle(
            issue_number=args.issue_number,
            run_id=args.run_id,
            agents=agents,
            gemini_output_dir=args.gemini_output_dir,
            output_artifact_path=args.output_artifact,
        )
        
    elif args.lifecycle == "implementation":
        if not args.analysis_artifact:
            parser.error("--analysis-artifact is required for implementation lifecycle")
        
        handle_implementation_lifecycle(
            issue_number=args.issue_number,
            run_id=args.run_id,
            analysis_artifact_path=args.analysis_artifact,
            gemini_output_dir=args.gemini_output_dir,
            output_artifact_path=args.output_artifact,
            branch_name=args.branch_name,
            pr_number=args.pr_number,
        )
        
    elif args.lifecycle == "prepare-context":
        if not args.analysis_artifact:
            parser.error("--analysis-artifact is required for prepare-context")
        
        prepare_execution_context(
            analysis_artifact_path=args.analysis_artifact,
            context_output_path=args.context_output,
            issue_number=args.issue_number,
        )


if __name__ == "__main__":
    main()
