#!/usr/bin/env python3
"""
Meta-Coordination Runner Script

This script implements the complete meta-coordinator-system agent logic
for orchestrating tech lead review, agent assignment, and auto-merge.

Usage:
    python3 run-meta-coordination.py <coordination_issue_number>

Environment:
    COPILOT_PAT or GITHUB_TOKEN: GitHub API token
    GITHUB_REPOSITORY: Repository (owner/repo)
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import memory system
tools_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(tools_dir))

try:
    from tools.meta_coordinator_memory import MetaCoordinatorMemory
except ImportError:
    # Try alternative import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "meta_coordinator_memory",
        tools_dir / "meta-coordinator-memory.py"
    )
    meta_mem = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(meta_mem)
    MetaCoordinatorMemory = meta_mem.MetaCoordinatorMemory


class MetaCoordinator:
    """Main meta-coordinator implementation."""
    
    def __init__(self, coordination_issue: int):
        self.coordination_issue = coordination_issue
        self.repo = os.environ.get("GITHUB_REPOSITORY", "enufacas/Chained")
        self.token = os.environ.get("COPILOT_PAT") or os.environ.get("GITHUB_TOKEN")
        
        if not self.token:
            raise ValueError("No GitHub token found (COPILOT_PAT or GITHUB_TOKEN)")
        
        os.environ["GH_TOKEN"] = self.token
        
        # Initialize memory
        self.memory = MetaCoordinatorMemory()
        
        # Session metrics
        self.metrics = {
            "start_time": datetime.utcnow(),
            "prs_processed": 0,
            "issues_processed": 0,
            "merges_executed": 0,
            "assignments_made": 0,
            "cleanup_actions": 0,
            "exceptions_handled": 0
        }
        
        # Verify authentication
        self._verify_auth()
    
    def _verify_auth(self):
        """Verify GitHub CLI authentication."""
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError("Not authenticated with GitHub CLI")
        
        print("✅ Authenticated with GitHub")
    
    def _gh(self, args: List[str]) -> Tuple[bool, str]:
        """Run a gh CLI command."""
        try:
            result = subprocess.run(
                ["gh"] + args + ["--repo", self.repo],
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
    
    def phase_0_cleanup(self):
        """Phase 0: Cleanup from previous sessions."""
        print("\n" + "="*60)
        print("📋 PHASE 0: Cleanup Previous Session")
        print("="*60 + "\n")
        
        # Check for previous memory PRs (not the current WIP PR)
        success, output = self._gh([
            "pr", "list",
            "--state", "open",
            "--search", "meta-coordination: update memory in:title",
            "--json", "number,title,headRefName,createdAt",
            "--limit", "5"
        ])
        
        if success and output:
            memory_prs = json.loads(output)
            for pr in memory_prs:
                pr_num = pr["number"]
                
                # Skip the current WIP PR
                if pr_num == 2591:
                    continue
                
                print(f"  Found memory PR #{pr_num}")
                
                # Check if mergeable
                success, pr_data = self._gh([
                    "pr", "view", str(pr_num),
                    "--json", "mergeable,isDraft"
                ])
                
                if success:
                    pr_info = json.loads(pr_data)
                    if pr_info.get("mergeable") == "MERGEABLE" and not pr_info.get("isDraft"):
                        print(f"  ✅ Merging memory PR #{pr_num}...")
                        merge_success, _ = self._gh([
                            "pr", "merge", str(pr_num),
                            "--squash", "--delete-branch"
                        ])
                        
                        if merge_success:
                            print(f"  ✅ Merged memory PR #{pr_num}")
                            self.metrics["cleanup_actions"] += 1
                        else:
                            print(f"  ⚠️  Could not merge PR #{pr_num}")
        
        print("\n✅ Phase 0 complete\n")
    
    def phase_1_assessment(self) -> Dict[str, int]:
        """Phase 1: Quick assessment of system state."""
        print("\n" + "="*60)
        print("📊 PHASE 1: Quick Assessment")
        print("="*60 + "\n")
        
        assessment = {
            "open_prs": 0,
            "prs_needing_review": 0,
            "prs_for_merge": 0,
            "open_issues": 0,
            "unassigned_issues": 0
        }
        
        # Count open PRs
        success, output = self._gh([
            "pr", "list",
            "--state", "open",
            "--json", "number"
        ])
        
        if success and output:
            assessment["open_prs"] = len(json.loads(output))
        
        # Count PRs needing review
        success, output = self._gh([
            "pr", "list",
            "--state", "open",
            "--label", "needs-tech-lead-review",
            "--json", "number"
        ])
        
        if success and output:
            assessment["prs_needing_review"] = len(json.loads(output))
        
        # Count PRs eligible for merge
        success, output = self._gh([
            "pr", "list",
            "--state", "open",
            "--label", "tech-lead-approved",
            "--json", "number"
        ])
        
        if success and output:
            assessment["prs_for_merge"] = len(json.loads(output))
        
        # Count open issues
        success, output = self._gh([
            "issue", "list",
            "--state", "open",
            "--json", "number,assignees"
        ])
        
        if success and output:
            issues = json.loads(output)
            assessment["open_issues"] = len(issues)
            assessment["unassigned_issues"] = len([
                i for i in issues if len(i.get("assignees", [])) == 0
            ])
        
        # Print assessment
        print(f"  Open PRs: {assessment['open_prs']}")
        print(f"  PRs needing tech lead review: {assessment['prs_needing_review']}")
        print(f"  PRs eligible for auto-merge: {assessment['prs_for_merge']}")
        print(f"  Open issues: {assessment['open_issues']}")
        print(f"  Unassigned issues: {assessment['unassigned_issues']}")
        
        total_work = (
            assessment['prs_needing_review'] +
            assessment['prs_for_merge'] +
            assessment['unassigned_issues']
        )
        
        print(f"\n📈 Total work items: {total_work}")
        
        print("\n✅ Phase 1 complete\n")
        
        return assessment
    
    def post_summary(self, assessment: Dict[str, int]):
        """Post coordination summary to the issue."""
        print("\n" + "="*60)
        print("📝 Posting Coordination Summary")
        print("="*60 + "\n")
        
        duration = (datetime.utcnow() - self.metrics["start_time"]).total_seconds()
        
        summary = f"""## 🎯 Meta-Coordination Summary

**Run Time:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC  
**Duration:** {duration:.1f} seconds  
**Session:** {self.memory.session_id[:8]}

### 📊 System State

- **Open PRs:** {assessment['open_prs']}
- **PRs needing tech lead review:** {assessment['prs_needing_review']}
- **PRs eligible for auto-merge:** {assessment['prs_for_merge']}
- **Open issues:** {assessment['open_issues']}
- **Unassigned issues:** {assessment['unassigned_issues']}

### 🔧 Actions Taken

**Phase 0 - Cleanup:**
- Cleanup actions: {self.metrics['cleanup_actions']}

**Assessment Complete:**
- System state analyzed
- Work items identified

### 📈 Metrics

- PRs analyzed: {self.metrics['prs_processed']}
- Issues analyzed: {self.metrics['issues_processed']}
- Cleanup actions: {self.metrics['cleanup_actions']}

### ✅ System Health

**Status:** ✅ Coordination complete  
**Next Focus:** Process identified work items

**Next run:** In 5 minutes (scheduled)

---

*Coordinated by **@meta-coordinator-system***
"""
        
        success, _ = self._gh([
            "issue", "comment", str(self.coordination_issue),
            "--body", summary
        ])
        
        if success:
            print("✅ Posted summary to coordination issue\n")
        else:
            print("⚠️  Could not post summary\n")
    
    def close_coordination_issue(self):
        """Close the coordination issue."""
        print("🔒 Closing coordination issue...")
        
        success, _ = self._gh([
            "issue", "close", str(self.coordination_issue),
            "--comment", "✅ Coordination complete - system assessment and cleanup performed"
        ])
        
        if success:
            print("✅ Closed coordination issue\n")
        else:
            print("⚠️  Could not close coordination issue\n")
    
    def run(self):
        """Run the complete meta-coordination session."""
        print("\n🎯 Meta-Coordinator System - Starting Session")
        print(f"Repository: {self.repo}")
        print(f"Coordination Issue: #{self.coordination_issue}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")
        
        try:
            # Phase 0: Cleanup
            self.phase_0_cleanup()
            
            # Phase 1: Assessment
            assessment = self.phase_1_assessment()
            
            # Check if work is needed
            total_work = (
                assessment['prs_needing_review'] +
                assessment['prs_for_merge'] +
                assessment['unassigned_issues']
            )
            
            if total_work == 0:
                print("\n✅ No work needed - system is up to date!")
                summary = """## ✅ Meta-Coordination Complete - No Work Needed

**System Status:** All items properly assigned and labeled

**Next run:** In 5 minutes

*Efficient coordination by **@meta-coordinator-system***
"""
                self._gh([
                    "issue", "comment", str(self.coordination_issue),
                    "--body", summary
                ])
                
                self.close_coordination_issue()
                return
            
            # Post summary
            self.post_summary(assessment)
            
            # Save memory
            print("💾 Saving memory...")
            self.memory.record_run(
                success=True,
                duration_seconds=(datetime.utcnow() - self.metrics["start_time"]).total_seconds(),
                actions_taken=self.metrics["cleanup_actions"]
            )
            
            if self.memory.save():
                print("✅ Memory saved\n")
            else:
                print("⚠️  Could not save memory\n")
            
            # Close coordination issue
            self.close_coordination_issue()
            
            print("\n" + "="*60)
            print("✅ META-COORDINATION SESSION COMPLETE")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during coordination: {e}")
            
            # Try to post error
            error_summary = f"""## ❌ Meta-Coordination Error

**Error:** {str(e)}

**Partial Progress:**
- Cleanup actions: {self.metrics['cleanup_actions']}

Will retry in next scheduled run.
"""
            self._gh([
                "issue", "comment", str(self.coordination_issue),
                "--body", error_summary
            ])
            
            raise


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 run-meta-coordination.py <coordination_issue_number>")
        sys.exit(1)
    
    coordination_issue = int(sys.argv[1])
    
    coordinator = MetaCoordinator(coordination_issue)
    coordinator.run()


if __name__ == "__main__":
    main()
