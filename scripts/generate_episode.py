#!/usr/bin/env python3
"""
Chained TV Episode Generator
Generates episodic stories from repository activity (Issues and PRs).
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path


class EpisodeGenerator:
    """Generates TV-style episodes from GitHub activity"""
    
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo  # format: "owner/repo"
        self.owner, self.repo_name = repo.split('/')
        self.api_base = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def fetch_recent_activity(self, hours=2):
        """Fetch issues and PRs updated in the last N hours"""
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        
        print(f"Fetching activity since {since}")
        
        # Fetch issues
        issues_url = f"{self.api_base}/repos/{self.owner}/{self.repo_name}/issues"
        issues_params = {
            'state': 'all',
            'since': since,
            'per_page': 100,
            'sort': 'updated'
        }
        
        try:
            response = requests.get(issues_url, headers=self.headers, params=issues_params, timeout=30)
            response.raise_for_status()
            all_items = response.json()
        except Exception as e:
            print(f"Error fetching activity: {e}")
            return [], []
        
        # Separate issues from PRs (PRs have 'pull_request' key)
        issues = [item for item in all_items if 'pull_request' not in item]
        prs = [item for item in all_items if 'pull_request' in item]
        
        # For PRs, fetch additional details
        detailed_prs = []
        for pr in prs[:20]:  # Limit to 20 PRs to avoid rate limits
            pr_url = f"{self.api_base}/repos/{self.owner}/{self.repo_name}/pulls/{pr['number']}"
            try:
                pr_response = requests.get(pr_url, headers=self.headers, timeout=30)
                pr_response.raise_for_status()
                detailed_prs.append(pr_response.json())
            except Exception as e:
                print(f"Warning: Could not fetch details for PR #{pr['number']}: {e}")
                detailed_prs.append(pr)
        
        print(f"Found {len(issues)} issues and {len(detailed_prs)} PRs")
        return issues, detailed_prs
    
    def generate_episode(self, issues, prs):
        """Generate an episode JSON from issues and PRs"""
        
        if not issues and not prs:
            # Generate a "quiet repo" filler episode
            return self._generate_quiet_episode()
        
        # Collect all actors (unique users)
        actors = set()
        for issue in issues:
            if issue.get('user'):
                actors.add(issue['user']['login'])
        for pr in prs:
            if pr.get('user'):
                actors.add(pr['user']['login'])
        
        # Generate title
        title = self._generate_title(issues, prs, actors)
        
        # Generate scenes
        scenes = []
        
        # Scene 1: Introduction
        intro_scene = self._generate_intro_scene(issues, prs, actors)
        if intro_scene:
            scenes.append(intro_scene)
        
        # Scene 2-4: Activity scenes (merged PRs, closed issues, open PRs, etc.)
        activity_scenes = self._generate_activity_scenes(issues, prs)
        scenes.extend(activity_scenes[:5])  # Cap at 5 activity scenes
        
        # Build episode
        episode = {
            "date": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "scenes": scenes
        }
        
        return episode
    
    def _generate_quiet_episode(self):
        """Generate a filler episode when there's no activity"""
        return {
            "date": datetime.now(timezone.utc).isoformat(),
            "title": "The Calm Before the Storm",
            "scenes": [
                {
                    "bg": "calm",
                    "narration": "The repository rests in peaceful silence. Not a single commit disturbs the tranquil codebase.",
                    "characters": [
                        {
                            "name": "System Monitor",
                            "side": "center",
                            "mood": "happy",
                            "line": "All systems operational. Zero activity detected."
                        }
                    ]
                },
                {
                    "bg": "night",
                    "narration": "The AI agents wait patiently, ready to spring into action at the next issue or pull request.",
                    "characters": [
                        {
                            "name": "Standby Agent",
                            "side": "left",
                            "mood": "determined",
                            "line": "We stand ready. The next challenge awaits."
                        }
                    ]
                }
            ]
        }
    
    def _generate_title(self, issues, prs, actors):
        """Generate a witty episode title"""
        merged_prs = [pr for pr in prs if pr.get('merged_at')]
        open_prs = [pr for pr in prs if pr.get('state') == 'open' and not pr.get('merged_at')]
        closed_issues = [i for i in issues if i.get('state') == 'closed']
        
        if merged_prs:
            if len(merged_prs) > 3:
                return "The Great Merge-athon"
            elif len(actors) > 3:
                return "United We Merge"
            else:
                return "Merge Victory"
        elif open_prs:
            if len(open_prs) > 5:
                return "PR Storm Incoming"
            else:
                return "Code Review Chronicles"
        elif closed_issues:
            return "Issue Hunters Strike"
        elif issues:
            return "The Bug Trackers"
        else:
            return "A Day in the Life"
    
    def _generate_intro_scene(self, issues, prs, actors):
        """Generate an introductory scene"""
        now = datetime.now(timezone.utc)
        hours_ago = 2
        time_desc = f"the last {hours_ago} hours"
        
        activity_count = len(issues) + len(prs)
        actor_count = len(actors)
        
        narration = f"In {time_desc}, {activity_count} events unfolded in the Chained repository"
        if actor_count == 1:
            narration += ", driven by a lone developer's determination."
        elif actor_count > 1:
            narration += f", orchestrated by {actor_count} collaborators working in harmony."
        else:
            narration += "."
        
        # Pick a character based on activity
        if prs:
            character_name = "Build Guardian"
            mood = "determined"
            line = f"I've tracked {len(prs)} pull requests. Let's see what stories they tell."
        elif issues:
            character_name = "Issue Tracker"
            mood = "determined"
            line = f"My sensors detected {len(issues)} issue updates. Time to investigate."
        else:
            character_name = "Repository Watcher"
            mood = "happy"
            line = "Another peaceful interval in the codebase."
        
        return {
            "bg": "lab",
            "narration": narration,
            "characters": [
                {
                    "name": character_name,
                    "side": "center",
                    "mood": mood,
                    "line": line
                }
            ]
        }
    
    def _generate_activity_scenes(self, issues, prs):
        """Generate scenes based on specific activities"""
        scenes = []
        
        # Scene: Merged PRs (success story)
        merged_prs = [pr for pr in prs if pr.get('merged_at')]
        if merged_prs:
            scene = self._generate_merge_scene(merged_prs)
            if scene:
                scenes.append(scene)
        
        # Scene: Open PRs (work in progress)
        open_prs = [pr for pr in prs if pr.get('state') == 'open' and not pr.get('merged_at')]
        if open_prs:
            scene = self._generate_open_pr_scene(open_prs)
            if scene:
                scenes.append(scene)
        
        # Scene: Closed PRs without merge (rivalry/failure)
        closed_unmerged = [pr for pr in prs if pr.get('state') == 'closed' and not pr.get('merged_at')]
        if closed_unmerged:
            scene = self._generate_closed_pr_scene(closed_unmerged)
            if scene:
                scenes.append(scene)
        
        # Scene: Closed issues
        closed_issues = [i for i in issues if i.get('state') == 'closed']
        if closed_issues:
            scene = self._generate_closed_issue_scene(closed_issues)
            if scene:
                scenes.append(scene)
        
        # Scene: New/updated open issues
        open_issues = [i for i in issues if i.get('state') == 'open']
        if open_issues and not scenes:  # Only if no other scenes
            scene = self._generate_open_issue_scene(open_issues)
            if scene:
                scenes.append(scene)
        
        return scenes
    
    def _generate_merge_scene(self, merged_prs):
        """Generate a scene for merged PRs"""
        pr = merged_prs[0]
        author = pr.get('user', {}).get('login', 'Unknown')
        
        additions = pr.get('additions', 0)
        deletions = pr.get('deletions', 0)
        
        if len(merged_prs) == 1:
            narration = f"PR #{pr['number']} has been merged successfully. {additions} lines added, {deletions} removed."
        else:
            narration = f"{len(merged_prs)} pull requests merged into main. The codebase evolves."
        
        characters = [
            {
                "name": "Merge Oracle",
                "side": "left",
                "mood": "smug",
                "line": f"The merge is complete. Well done, {author}."
            }
        ]
        
        # Add author as character if multiple PRs
        if len(merged_prs) > 1:
            authors = set(pr.get('user', {}).get('login', 'Unknown') for pr in merged_prs)
            if len(authors) > 1:
                characters.append({
                    "name": f"Team ({len(authors)} devs)",
                    "side": "right",
                    "mood": "happy",
                    "line": "Collaboration makes us stronger!"
                })
        
        return {
            "bg": "calm",
            "narration": narration,
            "characters": characters
        }
    
    def _generate_open_pr_scene(self, open_prs):
        """Generate a scene for open PRs"""
        pr = open_prs[0]
        author = pr.get('user', {}).get('login', 'Unknown')
        
        if len(open_prs) == 1:
            narration = f"PR #{pr['number']} awaits review. The code hangs in the balance."
        else:
            narration = f"{len(open_prs)} pull requests are open, awaiting the judgment of reviewers."
        
        return {
            "bg": "night",
            "narration": narration,
            "characters": [
                {
                    "name": author,
                    "side": "left",
                    "mood": "worried",
                    "line": "I hope the reviewers like my changes..."
                },
                {
                    "name": "Code Reviewer",
                    "side": "right",
                    "mood": "determined",
                    "line": "Let me examine this carefully. Quality matters."
                }
            ]
        }
    
    def _generate_closed_pr_scene(self, closed_prs):
        """Generate a scene for closed but unmerged PRs"""
        pr = closed_prs[0]
        author = pr.get('user', {}).get('login', 'Unknown')
        
        narration = f"PR #{pr['number']} was closed without merging. Not every branch reaches main."
        
        return {
            "bg": "alert",
            "narration": narration,
            "characters": [
                {
                    "name": author,
                    "side": "left",
                    "mood": "worried",
                    "line": "Perhaps another approach is needed..."
                },
                {
                    "name": "Repository Guardian",
                    "side": "right",
                    "mood": "determined",
                    "line": "We maintain our standards. Try again."
                }
            ]
        }
    
    def _generate_closed_issue_scene(self, closed_issues):
        """Generate a scene for closed issues"""
        issue = closed_issues[0]
        
        if len(closed_issues) == 1:
            narration = f"Issue #{issue['number']} has been resolved. Another victory for the team."
        else:
            narration = f"{len(closed_issues)} issues closed. The bug hunters have been busy."
        
        return {
            "bg": "calm",
            "narration": narration,
            "characters": [
                {
                    "name": "Issue Hunter",
                    "side": "center",
                    "mood": "happy",
                    "line": f"Mission accomplished! {len(closed_issues)} bug(s) eliminated."
                }
            ]
        }
    
    def _generate_open_issue_scene(self, open_issues):
        """Generate a scene for open issues"""
        issue = open_issues[0]
        
        if len(open_issues) == 1:
            narration = f"Issue #{issue['number']}: {issue.get('title', 'Untitled')}. The investigation begins."
        else:
            narration = f"{len(open_issues)} issues demand attention. The team mobilizes."
        
        return {
            "bg": "alert",
            "narration": narration,
            "characters": [
                {
                    "name": "Alert System",
                    "side": "center",
                    "mood": "worried",
                    "line": f"We have {len(open_issues)} open issue(s) requiring attention!"
                }
            ]
        }
    
    def save_episode(self, episode):
        """Save episode to docs/episodes/"""
        # Create directory if it doesn't exist
        episodes_dir = Path('docs/episodes')
        episodes_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as latest.json
        latest_path = episodes_dir / 'latest.json'
        with open(latest_path, 'w') as f:
            json.dump(episode, f, indent=2)
        print(f"Saved latest episode to {latest_path}")
        
        # Save timestamped version
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')
        timestamped_path = episodes_dir / f'episode-{timestamp}.json'
        with open(timestamped_path, 'w') as f:
            json.dump(episode, f, indent=2)
        print(f"Saved timestamped episode to {timestamped_path}")
        
        return latest_path, timestamped_path


def main():
    """Main entry point"""
    # Get token and repo from environment
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    if not repo:
        print("Error: GITHUB_REPOSITORY environment variable not set")
        sys.exit(1)
    
    print("=" * 70)
    print("Chained TV Episode Generator")
    print("=" * 70)
    print(f"Repository: {repo}")
    print()
    
    # Generate episode
    generator = EpisodeGenerator(token, repo)
    issues, prs = generator.fetch_recent_activity(hours=2)
    episode = generator.generate_episode(issues, prs)
    
    print()
    print(f"Generated episode: {episode['title']}")
    print(f"Scenes: {len(episode['scenes'])}")
    print()
    
    # Save episode
    generator.save_episode(episode)
    
    print()
    print("=" * 70)
    print("Episode generation complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
