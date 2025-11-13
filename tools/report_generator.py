#!/usr/bin/env python3
"""
Agent Evaluation Report Generator

Crafts beautiful evaluation reports with elegance and clarity.
Every report tells a story - of agents rising, falling, and persisting.

The art of storytelling through code.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


class ReportFormatter:
    """
    Formats evaluation data into beautiful, readable reports.
    
    Transforms raw data into compelling narratives.
    """
    
    @staticmethod
    def format_timestamp() -> str:
        """Create a human-readable timestamp"""
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def format_date() -> str:
        """Create a date string"""
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    @staticmethod
    def format_score(score: float) -> str:
        """Format a score as a percentage"""
        return f"{score:.2%}"


class IssueReportGenerator:
    """
    Generates GitHub issues for evaluation reports.
    
    Creates informative, well-structured reports that tell the story
    of the agent ecosystem's evolution.
    """
    
    def __init__(
        self,
        results: Dict[str, List[Dict[str, Any]]],
        registry: Dict[str, Any]
    ):
        self.results = results
        self.registry = registry
        self.formatter = ReportFormatter()
    
    def generate(self) -> str:
        """
        Generate a complete evaluation report.
        
        Beautiful in structure, informative in content.
        """
        sections = [
            self._create_header(),
            self._create_summary(),
            self._create_hall_of_fame_section(),
            self._create_system_lead_section(),
            self._create_metrics_section(),
            self._create_next_steps_section(),
            self._create_footer()
        ]
        
        return '\n\n'.join(sections)
    
    def _create_header(self) -> str:
        """Create report header"""
        return f"""## 📊 Daily Agent Evaluation Report

**Date**: {self.formatter.format_timestamp()} UTC"""
    
    def _create_summary(self) -> str:
        """Create results summary"""
        promoted_count = len(self.results.get('promoted', []))
        eliminated_count = len(self.results.get('eliminated', []))
        maintained_count = len(self.results.get('maintained', []))
        
        active_agents = [
            a for a in self.registry['agents']
            if a['status'] == 'active'
        ]
        
        return f"""### Results Summary

- 🏆 **Promoted**: {promoted_count} agents
- ❌ **Eliminated**: {eliminated_count} agents
- ✅ **Maintained**: {maintained_count} agents
- 📊 **Total Active**: {len(active_agents)} agents"""
    
    def _create_hall_of_fame_section(self) -> str:
        """Create Hall of Fame section"""
        hall_of_fame = self.registry.get('hall_of_fame', [])
        
        if not hall_of_fame:
            return "### Hall of Fame\n\n*No agents in Hall of Fame yet*"
        
        members_text = f"{len(hall_of_fame)} agents have earned their place:\n\n"
        
        # Sort by score, highest first
        sorted_members = sorted(
            hall_of_fame,
            key=lambda a: a['metrics']['overall_score'],
            reverse=True
        )
        
        system_lead_id = self.registry.get('system_lead')
        
        for member in sorted_members:
            score = member['metrics']['overall_score']
            is_lead = member['id'] == system_lead_id
            crown = "👑 " if is_lead else ""
            name = member['name']
            
            members_text += f"- {crown}**{name}** - {self.formatter.format_score(score)}\n"
        
        return f"### Hall of Fame\n\n{members_text}"
    
    def _create_system_lead_section(self) -> str:
        """Create system lead section"""
        lead_id = self.registry.get('system_lead')
        
        if not lead_id:
            return "### System Lead\n\n*No system lead elected yet*"
        
        hall_of_fame = self.registry.get('hall_of_fame', [])
        lead = next(
            (a for a in hall_of_fame if a['id'] == lead_id),
            None
        )
        
        if not lead:
            return "### System Lead\n\n*System lead not found*"
        
        return f"""### System Lead

👑 **{lead['name']}** is currently governing the agent ecosystem."""
    
    def _create_metrics_section(self) -> str:
        """Create performance metrics explanation"""
        return """### Performance Metrics

Agents are evaluated on:
- **Code Quality** (30%): Linting, best practices, maintainability
- **Issue Resolution** (20%): Issues completed, time to resolution
- **PR Success** (20%): PRs merged, review feedback
- **Peer Review** (15%): Reviews provided, quality of feedback
- **🎨 Creativity** (15%): Novel solutions, diverse approaches, impactful changes"""
    
    def _create_next_steps_section(self) -> str:
        """Create next steps section"""
        return """### Next Steps

- New agents will continue spawning every 3 hours
- Next evaluation in 24 hours
- Community feedback influences agent scores"""
    
    def _create_footer(self) -> str:
        """Create report footer"""
        return "---\n*🤖 Automated evaluation - May the best agents thrive!*"
    
    def create_issue(self) -> bool:
        """
        Create GitHub issue with the generated report.
        
        Returns True if successful, False otherwise.
        """
        title = f"🏛️ Agent Evaluation Report - {self.formatter.format_date()}"
        body = self.generate()
        
        try:
            result = subprocess.run(
                ['gh', 'issue', 'create', '--title', title, '--body', body,
                 '--label', 'agent-system,evaluation'],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Evaluation report issue created")
            return True
            
        except subprocess.CalledProcessError as error:
            print(f"⚠️ Failed to create issue: {error.stderr}")
            return False


def create_evaluation_report() -> None:
    """
    Main entry point for report generation.
    
    Elegant simplicity - load data, generate report, create issue.
    """
    # Load evaluation results
    results_path = Path('/tmp/evaluation_results.json')
    with open(results_path, 'r') as file:
        results = json.load(file)
    
    # Load registry
    registry_path = Path('.github/agent-system/registry.json')
    with open(registry_path, 'r') as file:
        registry = json.load(file)
    
    # Generate and create report
    generator = IssueReportGenerator(results, registry)
    generator.create_issue()


if __name__ == '__main__':
    create_evaluation_report()
