#!/usr/bin/env python3
"""
Branch Cleanup - Removes A2A task branches after completion
"""

import os
import subprocess

def main():
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    
    print(f"🧹 Cleaning up A2A task branches for issue #{issue_number}")
    
    # List and delete a2a-tasks/* branches
    result = subprocess.run(
        ['git', 'branch', '-r'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        branches = result.stdout.split('\n')
        a2a_branches = [b.strip() for b in branches if f'a2a-tasks/{issue_number}' in b]
        
        for branch in a2a_branches:
            if branch:
                remote_branch = branch.replace('origin/', '')
                print(f"   🗑️ Deleting branch: {remote_branch}")
                subprocess.run(['git', 'push', 'origin', '--delete', remote_branch],
                              capture_output=True)
    
    print("   ✅ Branch cleanup complete")

if __name__ == '__main__':
    main()
